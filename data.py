from __future__ import print_function
from time import time
import json
import element


class Data:
    def __init__(self):
        self.start = time()

        self.delay = {'flownum': [], 'delay': []}
        self.totentry = {'flownum': [], 'totentry': []}
        self.overflow = {'flownum': [], 'overflow': []}
        self.pktin = {'flownum': [], 'pktin': []}
        self.totinstall = {'flownum': [], 'totinstall': []}
        self.pktnum = {'flownum': [], 'pktnum': []}

        self.fct = {}
        self.threshold = 102400  # 100KB
        self.burst_fct = {}
        self.tail_fct = {}
        self.install_num = {}

    def record(self, flownum, delay, totentry, overflow, pktin, totinstall, pktnum):
        self.delay['flownum'].append(flownum)
        self.delay['delay'].append(delay)
        self.totentry['flownum'].append(flownum)
        self.totentry['totentry'].append(totentry)
        self.overflow['flownum'].append(flownum)
        self.overflow['overflow'].append(overflow)
        self.pktin['flownum'].append(flownum)
        self.pktin['pktin'].append(pktin)
        self.totinstall['flownum'].append(flownum)
        self.totinstall['totinstall'].append(totinstall)
        self.pktnum['flownum'].append(flownum)
        self.pktnum['pktnum'].append(pktnum)
        return

    def record_fct(self, tp, pkttime, flowsize):
        if tp in self.fct:
            self.fct[tp] += pkttime
        else:
            self.fct[tp] = pkttime

        if flowsize > self.threshold:
            if tp in self.tail_fct:
                self.tail_fct[tp] += pkttime
            else:
                self.tail_fct[tp] = pkttime
        else:
            if tp in self.burst_fct:
                self.burst_fct[tp] += pkttime
            else:
                self.burst_fct[tp] = pkttime
        return

    def record_install_num(self, install_num):
        self.install_num = install_num

    def get_install_num_cdf(self):
        install_num_list = self.install_num.values()
        [xlist, cplist] = element.get_cdf(install_num_list)
        cdf = {'x': xlist, 'y': cplist}

        return cdf

    def print_checkpoint(self, fnum, filename=None):
        with open(filename, 'a') as f:
            print('{} {}'.format(time()-self.start, fnum), file=f)
        return

    def get_fct_cdf(self, fct):
        delay_list = fct.values()
        [xlist, cplist] = element.get_cdf(delay_list)
        cdf = {'x': xlist, 'y': cplist}

        return cdf

    def print_data(self, fileprefix):
        with open(fileprefix+'_overflow.json', 'w') as f:
            print(json.dumps(self.overflow), file=f)
        with open(fileprefix+'_pktin.json', 'w') as f:
            print(json.dumps(self.pktin), file=f)
        with open(fileprefix+'_totinstall.json', 'w') as f:
            print(json.dumps(self.totinstall), file=f)
        with open(fileprefix+'_pktnum.json', 'w') as f:
            print(json.dumps(self.pktnum), file=f)
        tail_fct_cdf = self.get_fct_cdf(self.tail_fct)
        with open(fileprefix+'_tail_fct_cdf.json', 'w') as f:
            print(json.dumps(tail_fct_cdf), file=f)
        install_num_cdf = self.get_install_num_cdf()
        with open(fileprefix+'_install_cdf.json', 'w') as f:
            print(json.dumps(install_num_cdf), file=f)
        
        return