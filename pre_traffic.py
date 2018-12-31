#  pre-serialize pcap file


import traffic
import element
import setting
import network
import ruleset


def pre_pcap(pcap_filelist, pkl_file, max_flownum=None, json_file=None):
    print('serialize {} into {}'.format(pcap_filelist, pkl_file))
    t = traffic.Traffic()
    for pcap_file in pcap_filelist:
        print('processing {}...'.format(pcap_file))
        pkts = traffic.pcap2pkts(pcap_file)
        t.add_pkts(pkts)
        flownum = t.flownum[-1]
        print('flow number: {}'.format(flownum))
        if max_flownum is not None and flownum > max_flownum:
            break
    t.serialize(pkl_file)
    print('target flow number: {}; real flow number: {}'.format(max_flownum, t.flownum[-1]))
    print('total number of packets: {}'.format(len(t.pkts)))
    if json_file is not None:
        t.print_traffic_data(json_file)
    return



def pre_single(pkl_file):
    print('single: transform {} into {}'.format(pkl_file, setting.SINGLE_TRAFFIC_LOGFILE))

    topo = setting.SINGLE
    sw_list = setting.SINGLE_SW_LIST

    n = network.Network(topo)
    n.generate_real_traffic(pkl_file, sw_list)
    n.traffic.serialize(setting.SINGLE_TRAFFIC_LOGFILE)
    n.traffic.print_traffic_data(setting.SINGLE_TRAFFIC_DATA)

    print('flow number: {}'.format(n.traffic.flownum[-1]))
    return


def pre_slice_pcap():
    for i in range(25):
        start = 1+i*1000000
        end = (i+1)*1000000
        print('editcap -r tf real{}-{}.pcap {}-{} -F pcap &'
              .format(i, i+1, start, end))
    return


def pre_real_pcap():
    # [0, ~15000000] pkts
    fdir = './pcap_file/'
    pcap_filelist = ['{}real{}-{}.pcap'.format(fdir, i, i+1) for i in range(0, 25)]
    pkl_file = 'real10k.pkl'
    json_file = 'real10k.json'
    max_flownum = 101000

    pre_pcap(pcap_filelist, pkl_file, max_flownum, json_file)
    return


def pre_rule():
    print('single: generating rule set...')

    traffic_pkl = setting.SINGLE_TRAFFIC_LOGFILE
    rate_arr = [0.1*i for i in range(1, 10)]
    for rate in rate_arr:
        ruleset_pkl = 'single_rule_{}.pkl'.format(rate)
        print(ruleset_pkl)
        rs = ruleset.Ruleset()
        rs.generate_ruleset_from_traffic(traffic_pkl, 24, rate)
        element.serialize(rs, ruleset_pkl)
    return


def pre_classbench_rule():
    print('generating classbench rule set...')

    rs = ruleset.Ruleset()
    rs.generate_ruleset_from_classbench(setting.CB_RULE, setting.CB_TRACE, 
                                        minpri=8)
    cnt = 0
    tot = len(rs.ruleset)
    for (priority, _) in rs.ruleset:
        if priority == 32: cnt += 1
    print(cnt)
    print(tot)

    element.serialize(rs, setting.CB_RULE_PKL)

    return


def pre_classbench_trace():
    print('generating classbench trace...')

    with open(setting.CB_TRACE, 'r') as f:
        lines = f.readlines()
        lines = [l.rstrip('\n').split('\t') for l in lines]
        tf = traffic.Traffic()
        pkts = []
        for l in lines:
            srcip = element.int2ip(int(l[0]))
            dstip = element.int2ip(int(l[1]))
            srcport = int(l[2])
            dstport = int(l[3])
            protocol = int(l[4])
            p = traffic.Packet((srcip, dstip, srcport, dstport, protocol))
            # modify src and dst
            p.src = 0
            p.dst = 2
            pkts.append(p)
        tf.add_pkts(pkts)
    element.serialize(tf, setting.CB_TRACE_PKL)
    
    return


def pre_brain(pkl_file):
    print('generating brain rule and trace...')

    print('brain: transform {} into {}'.format(pkl_file, setting.BRAIN_TRAFFIC_LOGFILE))

    topo = setting.BRAIN

    n = network.Network(topo)
    n.generate_real_traffic(pkl_file)
    n.traffic.serialize(setting.BRAIN_TRAFFIC_LOGFILE)
    n.traffic.print_traffic_data(setting.BRAIN_TRAFFIC_DATA)

    print('flow number: {}'.format(n.traffic.flownum[-1]))

    print('brain: generating rule set...')

    traffic_pkl = setting.BRAIN_TRAFFIC_LOGFILE
    ruleset_pkl = setting.BRAIN_RULE_PKL
    rs = ruleset.Ruleset()
    rs.generate_ruleset_from_traffic(traffic_pkl, 24, 0.5)
    element.serialize(rs, ruleset_pkl)

    return


def test_pre_traffic():
    pcap_filelist = ['sample.pcap']
    pkl_file = 'sample.pkl'

    pre_pcap(pcap_filelist, pkl_file, json_file='sample.json')

    return
    

if __name__ == '__main__':
    test_pre_traffic()
