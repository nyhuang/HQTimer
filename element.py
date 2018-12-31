#  implement basic network functions


from __future__ import print_function
import setting


class Entry:
    def __init__(self, field, priority, match_field, action, flag=None,
                 ts=None, timeout=None, timeout_type=None):
        self.field = field
        self.priority = priority
        self.match_field = match_field
        self.action = action
        self.flag = flag

        self.counter = 0

        if ts is not None:
            self.ts = ts
            self.timeout = timeout
            self.timeout_type = timeout_type

    def __eq__(self, e):
        if not isinstance(e, type(self)):
            return NotImplemented
        return (self.field == e.field and 
                self.priority == e.priority and 
                self.match_field == e.match_field)

    def __repr__(self):
        return 'Entry()'

    def __str__(self):
        s = 'filed:{}, priority:{}, match field:{}, action:{}, flag:{}, counter:{}'.format(
            self.field, self.priority, self.match_field, self.action, self.flag, self.counter)
        if hasattr(self, 'ts'):
            s = '{}, ts:{}, timeout:{}, timeout type:{}'.format(
                s, self.ts, self.timeout, self.timeout_type)
        return s

    def print_entry(self, filename=None):
        print('field:%s, priority:%s, match field:%s, action:%s, cnt:%d' % (
              self.field, self.priority,
              self.match_field, self.action,
              self.counter), file=filename)
        return 0

    # def get_tag(self):
    #     return '{}:{}:{}'.format(self.field, self.priority, self.match_field)


def ip2int(addr):
    from struct import unpack
    from socket import inet_aton
    return unpack("!I", inet_aton(addr))[0]


def int2ip(addr):
    from struct import pack
    from socket import inet_ntoa
    return inet_ntoa(pack("!I", addr))


def get_ip_range(ip, mask):
    ipval = ip2int(ip)
    ipbin = '{0:032b}'.format(ipval)
    ipmax = int(ipbin[0:mask]+(32-mask)*'1', 2)
    ipmin = int(ipbin[0:mask]+(32-mask)*'0', 2)
    return [ipmin, ipmax]


def match_ip(match_field, ip):
    ip_range = get_ip_range(match_field[0], match_field[1])
    ipval = ip2int(ip)
    return ip_range[0] <= ipval <= ip_range[1]


def pdf2cdf_1d(pdf_mat):
    from copy import deepcopy
    cp = 0.0
    cdf_mat = deepcopy(pdf_mat)
    for i in range(len(cdf_mat)):
        cp += cdf_mat[i]
        cdf_mat[i] = cp
    assert abs(cdf_mat[-1]-1.0) < setting.DEFAULT_PRECISION
    return cdf_mat
    

def pdf2cdf(pdf_mat):  # list copy does not work for 2D list!
    from copy import deepcopy
    cp = 0.0
    cdf_mat = deepcopy(pdf_mat)
    row = len(cdf_mat)
    for i in range(row):
        col = len(cdf_mat[i])
        for j in range(col):
            cp += cdf_mat[i][j]
            cdf_mat[i][j] = cp
    assert abs(cdf_mat[-1][-1]-1.0) < setting.DEFAULT_PRECISION
    return cdf_mat


def sample_1d(cdf_mat):
    from random import random
    dice = random()
    for i in range(len(cdf_mat)):
        if dice < cdf_mat[i]:
            return i
    

def sample(cdf_mat):
    from random import random
    dice = random()
    row = len(cdf_mat)
    for i in range(row):
        col = len(cdf_mat[i])
        for j in range(col):
            if dice < cdf_mat[i][j]:
                return [i, j]


def test_float_list_identical_1d(l1, l2, precision=setting.DEFAULT_PRECISION):
    return (len(l1)==len(l2) and 
            [abs(l1[i]-l2[i])<precision for i in range(len(l1))])


def test_float_list_identical(l1, l2, precision=setting.DEFAULT_PRECISION):
    if len(l1)!=len(l2):
        return False
    for i in range(len(l1)):
        if not test_float_list_identical_1d(l1[i], l2[i], precision):
            return False
    return True


def serialize(o, pkl_file):
    from pickle import dump, HIGHEST_PROTOCOL
    with open(pkl_file, 'wb') as obj:
        dump(o, obj, HIGHEST_PROTOCOL)


def de_serialize(pkl_file):
    from pickle import load
    with open(pkl_file, 'rb') as obj:
        o = load(obj)
    return o


def shortest_pathes(topo, src, exclude_points=None):
    spathes = {}

    try:
        from Queue import PriorityQueue
    except ImportError:
        from queue import PriorityQueue

    q = PriorityQueue()
    visit = set()
    dis = {}
    if exclude_points is not None:
        exset = set(exclude_points)
    else:
        exset = set()
    
    class Node:
        def __init__(self, d, label, path):
            self.d = d
            self.label = label
            self.path = path
    
        def __cmp__(self, n):
            if self.d == n.d:
                return cmp(len(self.path), len(n.path))
            else:
                return cmp(self.d, n.d)

    now = Node(0, src, [[src]])
    dis[src] = 0
    spathes[src] = [[src]]
    q.put(now)

    while not q.empty():
        now = q.get()
        if now.label in visit:
            continue
        visit.add(now.label)
        for new_label in topo[now.label]:
            if new_label in exset or new_label in visit:
                continue
            new_d = now.d+1  # default as 1
            new_path = [p+[new_label] for p in now.path]
            if new_label not in dis or new_d < dis[new_label]:
                dis[new_label] = new_d
                spathes[new_label] = new_path
                q.put(Node(new_d, new_label, new_path))
            elif new_d == dis[new_label]:
                spathes[new_label] += new_path
                new_path = spathes[new_label]
                q.put(Node(new_d, new_label, new_path))
            
    return spathes


def get_shortest_pathes(topo, exclude_points=None):
    all_spathes = {label: {} for label in range(len(topo))}
    for src in range(len(topo)):
        spathes = shortest_pathes(topo, src, exclude_points)
        all_spathes[src] = spathes
    return all_spathes


def zipf(burst_max, exp=1):
    pdf_mat = [1.0/(n**exp) for n in range(1, burst_max+1)]
    s = sum(pdf_mat)
    pdf_mat = [1.0*p/s for p in pdf_mat]
    cdf_mat = pdf2cdf_1d(pdf_mat) 
    # print(pdf_mat); print(cdf_mat)
    return sample_1d(cdf_mat)+1


def get_cdf(data_list):
    cnt = {}
    s = len(data_list)
    for d in data_list:
        if d in cnt:
            cnt[d] += 1
        else:
            cnt[d] = 1
    cp = 0.0
    xlist = []        
    cplist = []
    for x in sorted(cnt):
        cp += 1.0 * cnt[x] / s
        xlist.append(x)
        cplist.append(cp)
    return [xlist, cplist]


if __name__ == '__main__':
    ip = '1.2.3.4'
    assert ip == int2ip(ip2int(ip))
    ipval = 65535
    assert ipval == ip2int(int2ip(ipval))
    
    assert match_ip(('1.2.3.4', 24), '1.2.3.0')
    assert match_ip(('1.2.3.4', 24), '1.2.3.255')
    
    pdf_mat = [0.2]*5
    cdf_mat = pdf2cdf_1d(pdf_mat)
    ans = [0.2*i for i in range(5)]
    assert test_float_list_identical_1d(cdf_mat, ans)

    pdf_mat = [[0.1, 0.1], [0.2, 0.2], [0.4]]
    cdf_mat = pdf2cdf(pdf_mat)
    ans = [[0.1, 0.2], [0.4, 0.6], [1.0]]
    assert test_float_list_identical(cdf_mat, ans)

    topo = setting.FIVE_STARS
    spathes = shortest_pathes(topo, 1, [0])
    assert spathes == {1: [[1]], 2: [[1, 2]], 3: [[1, 2, 3]], 4: [[1, 5, 4]], 5: [[1, 5]]}
    
    data_list = [2, 1, 3, 3, 4]
    [xlist, cplist] = get_cdf(data_list)
    assert xlist == [1, 2, 3, 4]
    assert cplist == [0.2, 0.4, 0.8, 1.0]