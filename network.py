#  implement basic network functions


from __future__ import print_function
import element
import traffic
import switch
import controller
import setting


class Network:
    def __init__(self, topo, soft_labels=None, ruleset_pkl=None):
        self.topo = topo
        
        self.switch_num = len(topo)
        self.switches = []
        for label in range(self.switch_num):
            self.switches.append(switch.Switch(label))

        self.soft_labels = soft_labels
        if soft_labels is None:
            self.soft_labels = []            
        for label in self.soft_labels:
            self.switches[label].set_sw_type(setting.TYPE_SOFTWARE)

        self.controller = controller.Controller(topo, soft_labels, ruleset_pkl)
        self.traffic = traffic.Traffic()

    def generate_random_traffic(self, traffic_mat, total, burst_max=1, exp=1, pktsize=1500):
        self.traffic = traffic.Traffic()
        pkts = []
        cdf_mat = element.pdf2cdf(traffic_mat)
        for _ in range(total):
            [src, dst] = element.sample(cdf_mat)
            pkts += traffic.synflow2pkt(src, dst, burst_max, exp, pktsize)
        self.traffic.add_pkts(pkts)
        return 0
    
    def generate_sample_traffic(self, dup=1):
        self.traffic = traffic.Traffic()
        pkts = []
        flow_set = [[i, j] for i in range(self.switch_num) 
            for j in range(self.switch_num)]
        for flow in flow_set:
            pkts += traffic.synflow2pkt(flow[0], flow[1], dup=dup)
        self.traffic.add_pkts(pkts)
        return 0

    def traffic_mapping(self, old_pkts, sw_list=None):
        from random import randint, choice
        
        # *.*.sub.* -> *.*.dst.*
        syn_pkts = []
        tp2tp = {}
        subnet2subnet = {}
        if sw_list is None:
            sw_list = range(self.switch_num)

        for pkt in old_pkts:
            old_tp = pkt.tp
            old_src_split = old_tp[0].split('.')
            old_dst_split = old_tp[1].split('.')
            old_src_sub = int(old_src_split[2])
            old_dst_sub = int(old_dst_split[2])
            
            new_tp = list(old_tp)
            new_src_sub = None
            new_dst_sub = None

            if old_tp in tp2tp:
                new_tp = tp2tp[old_tp]
            else:
                if (old_src_sub, old_dst_sub) in subnet2subnet:
                    (new_src_sub, new_dst_sub) = subnet2subnet[(old_src_sub, old_dst_sub)]
                else:
                    new_src_sub = choice(sw_list)
                    new_dst_sub = choice(filter(lambda x:x!=new_src_sub, sw_list))
                    subnet2subnet[(old_src_sub, old_dst_sub)] = (new_src_sub, new_dst_sub)
                new_tp[0] = '{}.{}.{}.{}'.format(old_src_split[0],
                                                 old_src_split[1],
                                                 new_src_sub,
                                                 old_src_split[3])
                new_tp[1] = '{}.{}.{}.{}'.format(old_dst_split[0],
                                                 old_dst_split[1],
                                                 new_dst_sub,
                                                 old_dst_split[3])
                new_tp = tuple(new_tp)
                tp2tp[old_tp] = new_tp
            
            syn_pkts.append(traffic.Packet(new_tp, pkt.size))
        
        # for t in tp2tp: print('%s:%s' % (t, tp2tp[t]))
        # for n in subnet2subnet: print('%s:%s' % ((element.int2ip(n[0]), element.int2ip(n[1])), subnet2subnet[n]))
        return syn_pkts

    def generate_real_traffic(self, filename, sw_list=None):  # sw_list: senders 
        # real pcap/pkl -> syn traffic 
        self.traffic = traffic.Traffic()
        if filename.find('.pcap') != -1:
            real_traffic = traffic.Traffic(filename)
        elif filename.find('.pkl') != -1:
            real_traffic = element.de_serialize(filename)
        else:
            raise NameError('Error. Not a valid input file format. Return')
            return
        real_pkts = real_traffic.pkts
        syn_pkts = self.traffic_mapping(real_pkts, sw_list)
        self.traffic.add_pkts(syn_pkts)
        return

    def generate_log_traffic(self, pkl_file):  # traffic pkl -> traffic
        self.traffic = element.de_serialize(pkl_file)
        return 

    # network modular is responsible for some control functions of controller
    def process_ctrl_messages(self, instractions):
        ret = {}
        for inst in instractions:
            (act, obj, cont) = inst
            if act == setting.INST_ADD:
                sw = self.switches[obj]
                sw.add_entry(cont)

            elif act == setting.INST_DELETE:
                sw = self.switches[obj]
                sw.delete_entry(cont)

            elif act == setting.INST_QUERY:
                if obj == setting.INST_OBJ_ALL:
                    num = 0  
                    for sw in self.switches:
                        num += sw.table_size
                    ret[setting.INST_OBJ_ALL] = num
                elif obj == setting.INST_OBJ_TABLE:
                    sw = self.switches[cont]
                    num = sw.table_size
                    ret[setting.INST_OBJ_TABLE] = num
                elif obj == setting.INST_OBJ_ENTRY:
                    sw = self.switches[cont]
                    ret[setting.INST_OBJ_ENTRY] = sw.get_entry_list()
                else:
                    raise NameError('Error. No such command')
        return ret


if __name__ == '__main__':
    n = Network([[1, 2], [0, 2], [0]])
    n.generate_sample_traffic()
    n.traffic.print_traffic()
    print()
    
    n.generate_random_traffic([[0, 0.1, 0.1], [0.2, 0, 0], [0.6, 0, 0]], 10)
    n.traffic.print_traffic()
    print()
    
    n = Network([[1], [0]])
    flownum = 10
    n.generate_random_traffic([[0, 0.5], [0.5, 0]], flownum, 10)
    n.traffic.print_traffic()
    assert n.traffic.flownum[-1] == flownum
    print()
    
    topo = setting.BRIDGE
    soft_labels = setting.BRIDGE_SOFT_LABELS_CORE
    n = Network(topo, soft_labels)
    n.generate_random_traffic(setting.BRIDGE_TRAFFIC_MAT, 50)
    n.traffic.print_traffic()

    n.generate_real_traffic('sample.pcap', soft_labels)
    n.traffic.print_traffic()
