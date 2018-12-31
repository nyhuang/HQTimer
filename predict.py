#  implement a timeout predictor
from __future__ import print_function


import setting

from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *

from random import seed
seed(setting.SEED)


class Predictor:
    def __init__(self):
        self.name = setting.PREDICTOR_DEFAULT
        self.rule_retrig = {}
        self.rule_remove = {}
        self.table_size = {}
        
    def update(self, info):
        (info_type, label, curtime, cont) = info
        if info_type == setting.INFO_PACKET_IN:
            if label in self.rule_retrig:
                if cont in self.rule_retrig[label]: 
                    self.rule_retrig[label][cont].append(curtime)
                else:
                    self.rule_retrig[label] = {cont: [curtime]}
            else:
                self.rule_retrig[label] = {cont: [curtime]}

        elif info_type == setting.INFO_FLOW_REMOVED:
            if label in self.rule_remove:
                if cont in self.rule_remove[label]: 
                    self.rule_remove[label][cont].append(curtime)
                else:
                    self.rule_remove[label] = {cont: [curtime]}
            else:
                self.rule_remove[label] = {cont: [curtime]}

        elif info_type == setting.INFO_TABLE_SIZE:
            if label in self.table_size:
                self.table_size[label].append((curtime, cont))
            else:
                self.table_size[label] = [(curtime, cont)]

        else:
            raise NameError('Error. No such info type. Exit.')
        
        return

    def predict(self, key, curtime=None):
        return setting.DEFAULT_TIMEOUT

    def round(self, value):
        # round to 1s
        return int(value / 1e6 + 0.5) * 1e6


class SimplePredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = setting.PREDICTOR_SIMPLE
        self.rule_last_retrig = {}
        self.rule_last_remove = {}
        self.table_size = {}

        self.old_max_timeout = {}
        self.t_max = {}
        self.t_bound = setting.ITM_TMAX
    
    def update(self, info):
        (info_type, label, curtime, cont) = info
        if info_type == setting.INFO_PACKET_IN:
            if label in self.rule_last_retrig:
                self.rule_last_retrig[label][cont] = curtime
            else:
                self.rule_last_retrig[label] = {cont: curtime}

        elif info_type == setting.INFO_FLOW_REMOVED:
            if label in self.rule_last_remove:
                self.rule_last_remove[label][cont] = curtime
            else:
                self.rule_last_remove[label] = {cont: curtime}

        elif info_type == setting.INFO_TABLE_SIZE:
            if label in self.table_size:
                self.table_size[label].append((curtime, cont))
            else:
                self.table_size[label] = [(curtime, cont)]

        else:
            raise NameError('Error. No such info type. Exit.')

        return

    def update_t_max(self):
        for label in self.table_size:
            entry_arr = self.table_size[label][-setting.ITM_N:]
            ocup_arr = [ocup for (_, ocup) in entry_arr]
            ocup_avg = sum(ocup_arr) / setting.ITM_N
            if label not in self.old_max_timeout:
                self.old_max_timeout[label] = setting.ITM_TMAX
            if label not in self.t_max:
                self.t_max[label] = setting.ITM_TMAX
            if ocup_avg >= setting.ITM_FB_START:
                k = (1.0 * (ocup_avg-setting.ITM_FB_START) / 
                     (setting.ITM_FB_PEAK-setting.ITM_FB_START))
                self.t_max[label] = int(self.old_max_timeout[label]*(1-k)+k)
            else:
                k = 1.0 * (ocup_avg-setting.ITM_FB_START) / setting.ITM_FB_START
                self.t_max[label] = int(self.old_max_timeout[label]*(1-k)+1)
            self.t_max[label] = max(self.t_max[label], 1e6)
            self.t_max[label] = min(self.t_max[label], self.t_bound)
            self.old_max_timeout[label] = self.t_max[label]
        return

    def predict(self, rule, curtime, label):
        if label not in self.t_max:
            self.t_max[label] = setting.ITM_TMAX

        if label in self.rule_last_remove:
            if rule in self.rule_last_remove[label]:
                last_remove = self.rule_last_remove[label][rule]
                delta = self.rule_last_retrig[label][rule]-last_remove
                return self.round(min(delta+setting.ITM_T, self.t_max[label]))

        return self.round(self.t_max[label])


class QPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = setting.PREDICTOR_Q
        self.training_data = []
        self.rule_table = {}
        self.Q = {}
    
        self.gamma = setting.Q_GAMMA
        self.batch_size = setting.Q_BATCH_SIZE
        self.epsilon = setting.Q_EPSILON_MAX
        self.epsilon_min = setting.Q_EPSILON_MIN
        self.epsilon_max = setting.Q_EPSILON_MAX
        self.lambda_ = setting.Q_LAMBDA

        self.steps = 0
        self.action_cnt = 10
        self.actcnt2timeout = {i: (i+1)*1e6 for i in range(self.action_cnt)}
        self.timeout2actcnt = {(i+1)*1e6: i for i in range(self.action_cnt)}

    def init(self, switch_num):
        for label in range(switch_num):
            self.rule_table[label] = {}
        return

    def update(self, info):
        (info_type, label, curtime, cont) = info
        if info_type == setting.INFO_FLOW_REMOVED:
            entry = cont
            if entry.timeout == setting.INF:
                return
            rule = (entry.priority, entry.match_field)
            if rule in self.rule_table[label]:
                (duration, counter) = self.rule_table[label][rule]
                x = (duration, counter)
            else:
                x = (0, 0)
            new_duration = x[0] + max(curtime-entry.ts, entry.timeout) / 1e6  # convert to second
            new_counter = x[1] + entry.counter
            self.rule_table[label][rule] = (new_duration, new_counter)
            x_ = (new_duration, new_counter)
            a = self.timeout2actcnt[entry.timeout]  # convert to index
            if x[0] == 0:
                r = x_[1] / x_[0]
            else:
                r = x_[1] / x_[0] - x[1] / x[0]

            self.training_data.append((x, a, x_, r))
        else:
            raise NameError('Error. No such info type. Exit.')
        return

    def get_Qmax(self, x):
        from random import randint

        if x not in self.Q:
            self.Q[x] = {i: 0 for i in range(self.action_cnt)}
            return [0, randint(0, self.action_cnt-1)]
        Qmax = None; actcnt = None
        for cnt in self.Q[x]:
            Q = self.Q[x][cnt]
            if Qmax is None or Q > Qmax:
                Qmax = Q
                actcnt = cnt
        return [Qmax, actcnt]

    def train(self):
        from random import sample
        from math import exp

        if len(self.training_data) == 0:
            return

        self.steps += 1
        self.epsilon = (self.epsilon_min+(self.epsilon_max-self.epsilon_min)*
                        exp(-self.lambda_*self.steps))

        training_size = min(self.batch_size, len(self.training_data))
        sample_training_data = sample(self.training_data, training_size)
        for cnt in range(training_size):
            (x, a, x_, r) = sample_training_data[cnt]
            [Qmax, actcnt] = self.get_Qmax(x_)
            if x not in self.Q:
                self.Q[x] = {i: 0 for i in range(self.action_cnt)}
            self.Q[x][a] = r + self.gamma * Qmax

        return

    def predict(self, rule, curtime, label):
        from random import random, randint

        if random() < self.epsilon:
            actcnt = randint(0, self.action_cnt-1)
        else:
            if rule in self.rule_table[label]:
                x = self.rule_table[label][rule]
            else:
                x = (0, 0)
            [_, actcnt] = self.get_Qmax(x)
        return self.actcnt2timeout[actcnt]


class DQNPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = setting.PREDICTOR_DQN
        self.training_data = []
        self.rule_table = {}

        self.gamma = setting.Q_GAMMA
        self.batch_size = setting.Q_BATCH_SIZE
        self.epsilon = setting.Q_EPSILON_MAX
        self.epsilon_min = setting.Q_EPSILON_MIN
        self.epsilon_max = setting.Q_EPSILON_MAX
        self.lambda_ = setting.Q_LAMBDA

        self.model = None
        self.steps = 0
        self.state_cnt = 2
        self.action_cnt = 10
        self.actcnt2timeout = {i: (i+1)*1e6 for i in range(self.action_cnt)}
        self.timeout2actcnt = {(i+1)*1e6: i for i in range(self.action_cnt)}

    def init(self, switch_num):
        for label in range(switch_num):
            self.rule_table[label] = {}
        
        self.model = Sequential()
        self.model.add(Dense(units=64, activation='relu', input_dim=self.state_cnt))
        self.model.add(Dense(units=self.action_cnt, activation='linear'))

        opt = RMSprop(lr=0.00025)
        self.model.compile(loss='mse', optimizer=opt)

        return

    def update(self, info):
        (info_type, label, curtime, cont) = info
        if info_type == setting.INFO_FLOW_REMOVED:
            entry = cont
            if entry.timeout == setting.INF:
                return
            rule = (entry.priority, entry.match_field)
            if rule in self.rule_table[label]:
                (duration, counter) = self.rule_table[label][rule]
                x = (duration, counter)
            else:
                x = (0, 0)
            new_duration = x[0] + max(curtime-entry.ts, entry.timeout) / 1e6  # convert to second
            new_counter = x[1] + entry.counter
            self.rule_table[label][rule] = (new_duration, new_counter)
            x_ = (new_duration, new_counter)
            a = self.timeout2actcnt[entry.timeout]  # convert to index
            if x[0] == 0:
                r = x_[1] / x_[0]
            else:
                r = x_[1] / x_[0] - x[1] / x[0]

            self.training_data.append((x, a, x_, r))
        else:
            raise NameError('Error. No such info type. Exit.')
        return

    def predict_states(self, states):
        return self.model.predict(states)

    def train(self):
        from random import sample
        from math import exp
        import numpy

        if len(self.training_data) == 0: 
            return

        self.steps += 1
        self.epsilon = (self.epsilon_min+(self.epsilon_max-self.epsilon_min)*
                        exp(-self.lambda_*self.steps))

        """ Approximate Q function using DNN
        """
        training_size = min(self.batch_size, len(self.training_data))
        sample_training_data = sample(self.training_data, training_size)

        old_states = numpy.array([tp[0] for tp in sample_training_data])
        old_states_Q = self.predict_states(old_states)
        new_states = numpy.array([tp[2] for tp in sample_training_data])
        new_states_Q = self.predict_states(new_states)
        inputs = numpy.zeros((training_size, self.state_cnt))
        outputs = numpy.zeros((training_size, self.action_cnt))

        for cnt in range(training_size):
            (x, a, x_, r) = sample_training_data[cnt]
            inputs[cnt] = x
            outputs[cnt] = old_states_Q[cnt]
            outputs[cnt][a] = r + self.gamma * numpy.amax(new_states_Q[cnt])

        self.model.fit(inputs, outputs, batch_size=self.batch_size, 
                       epochs=1, verbose=0)
        return

    def predict(self, rule, curtime, label):
        from random import random, randint
        import numpy

        if random() < self.epsilon:
            actcnt = randint(0, self.action_cnt-1)
        else:
            if rule in self.rule_table[label]:
                x = self.rule_table[label][rule]
            else:
                x = (0, 0)

            inputs = numpy.zeros((1, self.state_cnt))
            inputs[0] = x
            estimated_Q = self.model.predict(inputs).flatten()
            actcnt = numpy.argmax(estimated_Q)

        return self.actcnt2timeout[actcnt]

    def save_weights(self, log_prefix):
        import json
        all_weights = self.model.get_weights()
        weights = {}
        for i in range(2):
            weights[i] = {}
            weights[i]['w'] = all_weights[2 * i].tolist()
            weights[i]['b'] = [all_weights[2 * i + 1].tolist()]
        with open(log_prefix + '_model_weights.json', 'a') as f:
            print(json.dumps(weights), file = f)
        return

    def save_model(self, log_prefix):
        self.model.save(log_prefix + '_model.h5')
        return


if __name__ == '__main__':
    label = 0
    
    p = Predictor()
    p.update((setting.INFO_PACKET_IN, label, 1e6, (32, '1.2.3.4')))
    assert p.predict((32, '1.2.3.4')) == setting.DEFAULT_TIMEOUT

    p = SimplePredictor()
    for t in range(1, 11):
        p.update((setting.INFO_TABLE_SIZE, label, t, 1000+10*t))
    p.update_t_max()
    assert p.round(p.t_max[label]) == 6e6
    rule = (32, '1.2.3.4')
    p.update((setting.INFO_PACKET_IN, label, 12e6, rule))
    assert p.predict(rule, 12, label) == 6e6
    p.update((setting.INFO_FLOW_REMOVED, label, 11e6, rule))
    assert p.predict(rule, 12, label) == 3e6

    import element
    p = QPredictor()
    p.init(1)
    rule = (32, '1.2.3.4')
    timeout = p.predict(rule, 0, label)
    e = element.Entry(setting.FIELD_DSTIP, 32, '1.2.3.4', None,
                      flag=None, ts=0, timeout=timeout, timeout_type=None)    
    e.counter = 10  # 10 hits between 0~timeout then expire
    p.update((setting.INFO_FLOW_REMOVED, label, timeout, e))
    p.train()
    assert p.Q[(0, 0)][(timeout/1e6)-1] == 1.0* e.counter/(timeout/1e6)

    p = DQNPredictor()
    p.init(1)
    rule = (32, '1.2.3.4')
    timeout = p.predict(rule, 0, label)
    e = element.Entry(setting.FIELD_DSTIP, 32, '1.2.3.4', None,
                      flag=None, ts=0, timeout=timeout, timeout_type=None)    
    e.counter = 10  # 10 hits between 0~timeout then expire
    p.update((setting.INFO_FLOW_REMOVED, label, timeout, e))
    p.train()
    timeout = p.predict(rule, 2e6, label)
