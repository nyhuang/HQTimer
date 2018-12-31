#  implement basic hw switch functions


from __future__ import print_function
import element
import traffic
import setting


class Switch:
    def __init__(self, label, sw_type=setting.TYPE_HARDWARE):
        self.label = label
        self.sw_type = sw_type

        self.flow_table = {}
        self.table_size = 0

        self.default_action = [(setting.ACT_FWD, setting.CTRL)]

    def get_entry_list(self):
        entry_list = []
        for field in self.flow_table:
            for match_field in self.flow_table[field]:
                entry_list.append(self.flow_table[field][match_field])
        return entry_list

    def __repr__(self):
        return 'Switch()'

    def __str__(self):
        s = 's{}, type:{}'.format(self.label, self.sw_type)
        entry_list = self.get_entry_list()
        for entry in entry_list:        
            s = '{}\n{}'.format(s, entry.__str__())
        return s

    def set_sw_type(self, sw_type):
        self.sw_type = sw_type
        return 0

    def set_default_action(self, default_action):
        self.default_action = default_action
        return 0

    def delete_entry(self, entry):
        # print('**delete entry at s{}:\n{}'.format(self.label, entry))
        ret = self.flow_table[entry.field].pop(entry.match_field, None)
        if ret is None: 
            print('Error. No such key in the flow table. Ignore.')
        else:
            self.table_size -= 1
        # del self.flow_table[entry.field][entry.match_field]
        return 0

    def update(self, now=None):
        expire = []
        if now is not None:
            to_remove = []
            for field in self.flow_table:
                for match_field in self.flow_table[field]:
                    entry = self.flow_table[field][match_field]
                    if entry.ts+entry.timeout <= now:
                        to_remove.append(entry)
                        if (entry.flag is not None and 
                            entry.flag == setting.FLAG_REMOVE_NOTIFY):
                            expire.append(entry)

            for entry in to_remove:
                self.delete_entry(entry)

        max_size = setting.FLOW_TABLE_SIZE[self.sw_type]
        overflow = []
        if self.table_size >= max_size:
            entry_list = self.get_entry_list()
            if now is not None:
                # FIFO
                overflow = sorted(entry_list, key=lambda e: e.ts)[:(self.table_size-max_size)]
            else:
                # LRU: remove least used rules. TODO
                overflow = sorted(entry_list, key=lambda e: e.counter)[:(self.table_size-max_size)]
            for entry in overflow:
                self.delete_entry(entry)
        
        return [expire, overflow]

    def add_entry(self, entry):
        
        def add_fast_entry(entry):
            if entry.field in self.flow_table:
                self.flow_table[entry.field][entry.match_field] = entry
            else:
                self.flow_table[entry.field] = {entry.match_field: entry}
            return

        if entry.field in self.flow_table:
            if entry.match_field in self.flow_table[entry.field]:
                old_entry = self.flow_table[entry.field][entry.match_field]
                # exists old entry; update with the new entry
                if entry.priority >= old_entry.priority:
                    # print('**overwrite entry at s{}:\n{}'.format(self.label, entry))                    
                    self.flow_table[entry.field][entry.match_field] = entry
                return 0

        """update the flow table manually
        [expire, overflow] = self.update(now)"""
        add_fast_entry(entry)
        self.table_size += 1
        # print('**add entry at s{}:\n{}'.format(self.label, entry))
        return 0

    def get_match_entry(self, pkt):
        match_entry = element.Entry(None, -1, None, None)

        def comp_entry(new_entry, old_entry):
            if new_entry.priority > old_entry.priority:
                return new_entry
            elif new_entry.priority == old_entry.priority:  # TODO: ECMP
                return old_entry
            else:
                return old_entry

        # fast match (exact matching)
        pkt_attr = {
            setting.FIELD_TP: pkt.tp,
            setting.FIELD_DSTIP: pkt.dstip
        }

        for field in pkt_attr:
            if field in self.flow_table:
                attr = pkt_attr[field]
                if attr in self.flow_table[field]:
                    entry = self.flow_table[field][attr]
                    match_entry = comp_entry(entry, match_entry)

        # slow match (wildcard matching for dstip)
        if match_entry.priority == -1:
            for prefix in setting.FIELD_DSTPREFIX:
                field = setting.FIELD_DSTPREFIX[prefix]
                if field in self.flow_table:
                    attr = element.int2ip(element.get_ip_range(pkt.dstip, prefix)[0])
                    if attr in self.flow_table[field]:
                        entry = self.flow_table[field][attr]
                        match_entry = comp_entry(entry, match_entry)
        
        return match_entry

    def get_match_action(self, pkt, now=None):
        match_entry = self.get_match_entry(pkt)
        # print('**match entry: {}'.format(match_entry))
        if match_entry.action is None:
            return self.default_action
        else:
            match_entry.counter += 1
            if (now is not None and
                match_entry.ts is not None and 
                match_entry.timeout_type == setting.TIMEOUT_IDLE):
                
                match_entry.ts = now

            return match_entry.action

    def recv_pkt(self, pkt, now=None):
        action = self.get_match_action(pkt, now)  # action = [(type, value), ...]

        for act in action:
            act_type = act[0]
            if act_type == setting.ACT_TAG:
                pkt.label = act[1]
            elif act_type == setting.ACT_FWD:
                next_hop = act[1]
            else:
                raise NameError('Error. No such act type. Exit.')

        pkt.path.append(self.label)

        if next_hop == setting.CTRL:
            pkt.path.append(setting.CTRL)
        
        return [pkt, next_hop]


if __name__ == '__main__':
    label = 0
    sw = Switch(label)
    # basic tests
    entry = element.Entry(setting.FIELD_DSTIP, 32, '1.2.3.4',
                          [(setting.ACT_FWD, 1)])
    sw.add_entry(entry)
    assert sw.table_size == 1
    pkt = traffic.Packet(('0.0.0.0', '1.2.3.4'))
    [pkt, next_hop] = sw.recv_pkt(pkt)
    assert next_hop == 1
    entry = element.Entry(setting.FIELD_DSTPREFIX[24], 24, '1.2.3.0',
                          [(setting.ACT_FWD, 2)])
    sw.add_entry(entry)
    pkt = traffic.Packet(('0.0.0.0', '1.2.3.5'))
    [pkt, next_hop] = sw.recv_pkt(pkt)
    assert next_hop == 2
    
    setting.FLOW_TABLE_SIZE[setting.TYPE_HARDWARE] = 1
    [_, overflow] = sw.update()
    assert len(overflow) == 1
    assert sw.table_size == 1
    sw.delete_entry(element.Entry(setting.FIELD_DSTIP, 32, '1.1.1.1', 
                                  None))
    assert sw.table_size == 1

    setting.FLOW_TABLE_SIZE[setting.TYPE_HARDWARE] = 0
    sw.update()
    setting.FLOW_TABLE_SIZE[setting.TYPE_HARDWARE] = 3000

    # timeout tests
    entry = element.Entry(setting.FIELD_DSTIP, 32, '1.2.3.4',
                          [(setting.ACT_FWD, 1)], setting.FLAG_REMOVE_NOTIFY, 
                          0, 10, setting.TIMEOUT_IDLE)
    sw.add_entry(entry)
    pkt = traffic.Packet(('0.0.0.0', '1.2.3.4'))
    [pkt, next_hop] = sw.recv_pkt(pkt, 5)
    sw.update(10)
    assert sw.table_size == 1
    [expire, _] = sw.update(15)
    assert len(expire) == 1
    assert sw.table_size == 0
    
    # update tests
    for i in range(10):
        entry = element.Entry(setting.FIELD_DSTIP, 32, '1.2.3.4',
                            [(setting.ACT_FWD, 1)], setting.FLAG_REMOVE_NOTIFY, 
                            i, 10, setting.TIMEOUT_IDLE)
        sw.add_entry(entry)
        assert sw.table_size == 1

    for i in range(10):
        entry = element.Entry(setting.FIELD_DSTIP, 32, '1.2.3.{}'.format(i),
                            [(setting.ACT_FWD, 1)], setting.FLAG_REMOVE_NOTIFY, 
                            i, 10, setting.TIMEOUT_IDLE)
        sw.add_entry(entry)
    assert sw.table_size == 10
    [expire, _] = sw.update(10)
    assert sw.table_size == 9
    assert expire[0].ts == 0
    setting.FLOW_TABLE_SIZE[setting.TYPE_HARDWARE] = 8
    [_, overflow] = sw.update(10)
    assert overflow[0].ts == 1
    entry_list = sw.get_entry_list()
    assert len(entry_list) == 8

    """pressure tests
    """
    setting.FLOW_TABLE_SIZE[setting.TYPE_HARDWARE] = 1500
    for i in range(255):
        for j in range(255):
            entry = element.Entry(setting.FIELD_DSTIP, 32, '1.2.{}.{}'.format(i, j),
                                [(setting.ACT_FWD, 1)])
            sw.add_entry(entry)
