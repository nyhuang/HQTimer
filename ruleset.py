#  OpenFlow rule set


from __future__ import print_function
import element, setting


"""generate exact and wildcard matching rules based on dst IP
""" 
class Ruleset:
    def __init__(self):
        self.rules = {}
        self.ruleset = set()
        self.depset = {}

    def get_depset(self, maxdep):
        for ri in self.ruleset:
            self.depset[ri] = []
            if ri[0] == 32: continue
            ri_range = element.get_ip_range(ri[1], ri[0])
            for rj in self.ruleset:
                if rj[0] < ri[0] or rj == ri: continue
                rj_range = element.get_ip_range(rj[1], rj[0])
                if ri_range[1] < rj_range[0] or rj_range[1] < ri_range[0]:
                    continue
                else:
                    self.depset[ri].append(rj)
                    if len(self.depset[ri]) > maxdep:
                        break
        return

    def generate_ruleset_from_traffic(self, traffic_pkl, mask=24, rate=0, maxdep=setting.INF):
        traffic = element.de_serialize(traffic_pkl)
        from random import random
        for pkt in traffic.pkts:
            if pkt.dstip in self.rules: continue
            dice = random()
            if dice <= rate:
                dstprefix = element.int2ip(element.get_ip_range(pkt.dstip, mask)[0])
                self.rules[pkt.dstip] = (24, dstprefix)
                self.ruleset.add((24, dstprefix))
            else:
                self.rules[pkt.dstip] = (32, pkt.dstip)
                self.ruleset.add((32, pkt.dstip))
        
        self.get_depset(maxdep)

        return

    def generate_ruleset_from_classbench(self, classbench_rule, classbench_trace, 
                                         maxdep=setting.INF, minpri=0):
        with open(classbench_rule, 'r') as f:
            lines = f.readlines()
            lines = [l.rstrip('\n').split('\t') for l in lines]
            for l in lines:
                [dstip, priority_str] = l[1].split('/')
                priority = int(priority_str)
                # remove rules with very low priority
                if priority < minpri:
                    self.ruleset.add((32, dstip))
                else:   
                    self.ruleset.add((priority, dstip))

        with open(classbench_trace, 'r') as f:
            lines = f.readlines()
            lines = [l.rstrip('\n').split('\t') for l in lines]
            for l in lines:
                dstip_int = int(l[1])
                dstip = element.int2ip(dstip_int)
                all_dstprefix = {mask: element.int2ip(element.get_ip_range(dstip, mask)[0])
                                 for mask in range(33)}
                for mask in range(32, minpri-1, -1):
                    if (mask, all_dstprefix[mask]) in self.ruleset:
                        self.rules[dstip] = (mask, all_dstprefix[mask])
                        break

                # fail to match
                if dstip not in self.rules:
                    self.rules[dstip] = (32, dstip)
                    self.ruleset.add((32, dstip))

        self.get_depset(maxdep)
                
        return


if __name__ == '__main__':
    rs = Ruleset()
    rs.generate_ruleset_from_traffic('sample.pkl')

    print(rs.rules)
    print(rs.ruleset)
    print(rs.depset)

    rs = Ruleset()
    rs.generate_ruleset_from_classbench('test_rule', 'test_rule_trace', minpri=8)

    print(rs.rules)
    print(rs.ruleset)
    print(rs.depset)

