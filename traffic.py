#  implement basic traffic elemtns


from __future__ import print_function
import element


def synflow2pkt(src, dst, burst_max=1, exp=1, pktsize=1500, dup=1):
    from random import randint
    pkt_set = []
    srcip = '{}.{}.{}.{}'.format(randint(0, 255),
                                 randint(0, 255),
                                 src,
                                 randint(0, 255))
    dstip = '{}.{}.{}.{}'.format(randint(0, 255),
                                 randint(0, 255),
                                 dst,
                                 randint(0, 255))
    srcport = randint(1, 65535)
    dstport = randint(1, 65535)
    protocol = 6
    for _ in range(element.zipf(burst_max, exp, )):
        for _ in range(dup):
            p = Packet((srcip, dstip, srcport, dstport, 6), pktsize)  # TCP packets
            pkt_set.append(p)
    return pkt_set


def pcap2pkts(pcap_file):
    pkts = []
    import dpkt
    from socket import inet_aton, inet_ntoa
    with open(pcap_file, 'rb') as f:
        for [ts, pkt] in dpkt.pcap.Reader(f):
            try:
                eth = dpkt.ethernet.Ethernet(pkt)
                if isinstance(eth.data, dpkt.ip.IP):
                    ip = eth.data
                    size = ip.len+18  # plus Ethernet header
                    srcip = inet_ntoa(ip.src)
                    dstip = inet_ntoa(ip.dst)
                    if isinstance(ip.data, dpkt.tcp.TCP):
                        tcp = ip.data
                        protocol = 6
                        srcport = tcp.sport
                        dstport = tcp.dport
                    elif isinstance(ip.data, dpkt.udp.UDP):
                        udp = ip.data
                        protocol = 17
                        srcport = udp.sport
                        dstport = udp.dport
                    else:
                        continue
                else:
                    continue
                pkts.append(Packet((srcip, dstip, srcport, dstport, protocol), size, ts))
            except:
                print('Warning. Invalid packet. Drop it.')

    return pkts


class Packet:
    #  tp = (srcip, dstip, srcport, dstport, protocol, ...)
    def __init__(self, tp, size=1500, ts=None):  # maximum Ethernet frame
        self.tp = tp
        self.size = size
        self.ts = ts  # real world timestamp

        self.label = None
        self.path = []

        if tp is not None:
            self.srcip = tp[0]
            self.dstip = tp[1]

            self.src = int(self.srcip.split('.')[2])
            self.dst = int(self.dstip.split('.')[2])

            if len(tp) == 5:
                self.srcport = tp[2]
                self.dstport = tp[3]
                self.protocol = tp[4]

    def __repr__(self):
        return 'Packet()'

    def __str__(self):
        return '{}({})'.format(self.tp, self.size)

    def print_pkt(self, filename=None):
        print('{}({})'.format(self.tp, self.size), file=filename)
        return 0


class Traffic:
    def __init__(self, pcap_file=None):
        self.pkts = []

        self.flowsize = {}
        self.flownum = []

        if pcap_file is not None:
            pkts = pcap2pkts(pcap_file)
            self.add_pkts(pkts)

    def get_size(self):
        return len(self.pkts)

    def add_pkts(self, pkts):
        self.pkts += pkts
        for pkt in pkts:
            tp = pkt.tp  # define a flow
            if tp in self.flowsize:
                self.flowsize[tp] += pkt.size
            else:
                self.flowsize[tp] = pkt.size
            self.flownum.append(len(self.flowsize)) 
        return 0

    def serialize(self, pkl_file):
        from pickle import dump, HIGHEST_PROTOCOL
        with open(pkl_file, 'wb') as obj:
            dump(self, obj, HIGHEST_PROTOCOL)

    def print_traffic(self, filename=None):
        for pkt in self.pkts:
            pkt.print_pkt(filename)

    def print_traffic_data(self, json_file):
        from json import dumps
        with open(json_file, 'w') as f:
            flowsize_str = {}
            for tp in self.flowsize:
                flowsize_str[str(tp)] = self.flowsize[tp]
            data = {
                'pktnum': len(self.pkts), 
                'flownum': self.flownum,
                'flowsize': flowsize_str
            }
            print(dumps(data), file=f)
        return


if __name__ == '__main__': 
    pkt_set = synflow2pkt(1, 10, 10)
    for pkt in pkt_set:
        assert int(pkt.srcip.split('.')[2]) == 1
        assert int(pkt.dstip.split('.')[2]) == 10
        # pkt.print_pkt()

    t = Traffic('sample.pcap')
    t.print_traffic()
    # print(t.flowsize); print(t.flownum)
    assert t.get_size() == 101
    assert t.flownum[-1] == 12
    t.print_traffic_data('sample.json')
    from json import loads
    with open('sample.json', 'r') as f:
        data = loads(f.readline())
        print(data['pktnum'])
        print(data['flownum'])
        print(data['flowsize'])