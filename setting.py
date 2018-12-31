# settings of network


"""
Constants
"""
SEED = 0

CTRL = -100
LOCAL = -101

TYPE_HARDWARE = 0
TYPE_SOFTWARE = 1

ACT_FWD = -1000
ACT_TAG = -1001

FIELD_DSTIP = -2000
FIELD_TP = -2001
FIELD_DSTPREFIX = {
    mask: -2002-mask for mask in range(32)
}
 
INST_ADD = -3000
INST_DELETE = -3001
INST_QUERY = -3002
INST_OBJ_ALL = -3003
INST_OBJ_TABLE = -3004
INST_OBJ_ENTRY = -3005

TIMEOUT_HARD = 0
TIMEOUT_IDLE = 1

FLAG_REMOVE_NOTIFY = -4000

MODE_DEFAULT = -5000
MODE_SPATH = -5001
MODE_HARD = -5002
MODE_IDLE = -5003
MODE_HYBRID = -5004

PREDICTOR_DEFAULT = -6000
PREDICTOR_SIMPLE = -6001
PREDICTOR_Q = -6002
PREDICTOR_DQN = -6003

INFO_PACKET_IN = -7000
INFO_FLOW_REMOVED = -7001
INFO_TABLE_SIZE = -7002

"""
Numerical settings
"""
DEFAULT_PRECISION = 1e-3
DEFAULT_TIMEOUT = 5e6  # 5s
DEFAULT_UPDATE = 1e6  # 1s
INF = float('inf')

"""Parameters for ITM
'Intelligent Timeout Master: Dynamic Timeout for SDN-based Data Centers'
"""
ITM_TINIT = 1e6  # 1s
ITM_TMAX = 10e6  # 10s
ITM_FB_START = 900
ITM_FB_PEAK = 1300
ITM_N = 10
ITM_T = 2e6  # 2s

"""Parameters for Q/DQN predictor
"""
Q_GAMMA = 0.99
Q_BATCH_SIZE = 64
Q_EPSILON_MAX = 1.0
Q_EPSILON_MIN = 0.01
Q_LAMBDA = 0.001
Q_MINT = 1e6
Q_MIDT = 5e6
Q_MAXT = 10e6

"""Switch settings
flow table size and forwarding delays cite from:
'OFLOPS: An Open Framework for OpenFlow Switch Evaluation.'
'DevoFlow: Scaling flow management for high-performance networks'
"""
FLOW_TABLE_SIZE = {TYPE_HARDWARE: 3000, TYPE_SOFTWARE: 1e9}
UNLIMITED_FLOW_TABLE = {TYPE_HARDWARE: INF, TYPE_SOFTWARE: INF}
LINK_RATE = 0.008  # us/B. 1Gbps link 
HARDWARE_FWD_DELAY = 5  # 4~5 us. ProCurve 5406zl 
SOFTWARE_FWD_DELAY = 35  # us. Open vSwitch
CONTROLLER_DELAY = 4000  # us. 

"""Sample topologies
"""
SIMPLE_BITREE = [
    [1, 2],
    [0, 3, 4],
    [0, 5, 6],
    [1],
    [1],
    [2],
    [2]
]

SIMPLE_CLOS = [
    [1, 2],
    [0, 3, 4, 5, 6],
    [0, 3, 4, 5, 6],
    [1, 2],
    [1, 2],
    [1, 2],
    [1, 2]
]

FIVE_STARS = [
    [1, 2, 3, 4, 5],
    [0, 2, 5],
    [0, 1, 3],
    [0, 2, 4],
    [0, 3, 5],
    [0, 4, 1]
]

"""bridge:
|\/|--|\/|
|/\|--|/\|
"""
BRIDGE = [
    [1, 2, 3],
    [0, 2, 4, 5],
    [0, 1, 3, 4],
    [0, 2, 4],
    [1, 2, 3, 8],
    [1, 6, 7, 8],
    [5, 7, 9],
    [5, 6, 8, 9],
    [4, 5, 7, 9],
    [6, 7, 8]
]
BRIDGE_REGIONS = {
    2: [0, 1, 2, 3, 4],
    7: [5, 6, 7, 8, 9]
}
BRIDGE_SOFT_LABELS_EDGE = [0, 3, 6, 9]
BRIDGE_SOFT_LABELS_CORE = [2, 7]

BRIDGE_TRAFFIC_MAT = [[0 for _ in range(10)] for _ in range(10)]  
BRIDGE_TRAFFIC_MAT[0][6] = BRIDGE_TRAFFIC_MAT[6][0] = \
BRIDGE_TRAFFIC_MAT[0][9] = BRIDGE_TRAFFIC_MAT[9][0] = \
BRIDGE_TRAFFIC_MAT[3][6] = BRIDGE_TRAFFIC_MAT[6][3] = \
BRIDGE_TRAFFIC_MAT[3][9] = BRIDGE_TRAFFIC_MAT[9][3] = 0.125

BRIDGE_TRAFFIC_LOGFILE = 'bridge.pkl'
BRIDGE_TRAFFIC_DATA = 'bridge.json'

"""single
0-1-2
"""
SINGLE = [
    [1],
    [0, 2],
    [1]
]
SINGLE_TRAFFIC_MAT = [[0 for _ in range(3)] for _ in range(3)]
SINGLE_TRAFFIC_MAT[0][2] = 1.0
SINGLE_SW_LIST = [0, 2]
SINGLE_TRAFFIC_LOGFILE = 'single.pkl'
SINGLE_TRAFFIC_DATA = 'single.json'
SINGLE_RULE_PKL = 'single_rule_0.2.pkl'


"""germany50
50 nodes and 88 links
'SNDlib10'
"""
GE50 = [
    [29, 48, 46],
    [47, 34, 49],
    [31, 8, 37],
    [31, 11, 43, 32, 20],
    [35, 44, 22, 5],
    [32, 21, 22, 4, 25],
    [38, 7, 22],
    [6, 15],
    [11, 13, 2],
    [16, 33, 23],
    [14, 35, 44, 25],
    [3, 31, 13, 8],
    [14, 29],
    [31, 11, 8, 25, 49],
    [12, 10, 48],
    [27, 7],
    [28, 9, 19, 18],
    [24, 30],
    [25, 16, 19, 49],
    [44, 25, 16, 18],
    [3, 43],
    [43, 27, 22, 5],
    [21, 6, 4, 5, 39],
    [28, 9, 42, 24],
    [33, 23, 42, 45, 17],
    [10, 13, 5, 19, 18],
    [30, 34],
    [43, 21, 15],
    [29, 44, 16, 23, 46],
    [12, 0, 28],
    [45, 17, 26],
    [3, 11, 13, 32, 2],
    [3, 31, 43, 5],
    [9, 24],
    [1, 26, 40, 37, 41],
    [10, 4, 39],
    [48, 38],
    [34, 2, 49, 41],
    [48, 6, 36, 39],
    [35, 38, 22],
    [34, 41],
    [34, 40, 37],
    [23, 46, 24],
    [3, 32, 20, 21, 27],
    [10, 28, 4, 19],
    [24, 47, 30, 49],
    [0, 28, 42],
    [45, 1],
    [14, 0, 38, 36],
    [13, 18, 45, 1, 37]
]
GE50_SOFT_LABELS = {
    'edge': [0, 1, 6, 2, 11, 26, 30, 35, 39, 41, 
             49, 48, 47, 46, 45, 40, 36, 32, 22, 16,
             3, 7, 9, 10, 8, 4],  # 26 senders
    1: [25],
    2: [44, 13],
    3: [49, 3, 44],
    4: [34, 3, 28, 22],
    5: [24, 34, 3, 22, 14]
}
GE50_REGIONS = {
    1: {
        25: range(50)
    },
    2: {44: [0, 4, 6, 7, 9, 10, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23,
             24, 25, 27, 28, 29, 33, 35, 36, 38, 39, 42, 44, 45, 46, 48],
        13: [1, 2, 3, 5, 8, 11, 13, 20, 26, 30, 31, 32, 34, 37, 40, 41,
             43, 47, 49]
    },
    3: {49: [1, 2, 17, 18, 24, 26, 30, 33, 34, 37, 40, 41, 45, 47, 49],
        3: [3, 5, 8, 11, 13, 15, 20, 21, 22, 27, 31, 32, 43],
        44: [0, 4, 6, 7, 9, 10, 12, 14, 16, 19, 23, 25, 28, 29, 35, 36,
             38, 39, 42, 44, 46, 48]
    },
    4: {34: [1, 2, 26, 30, 34, 37, 40, 41, 45, 47, 49], 
        3: [3, 5, 8, 11, 13, 20, 31, 32, 43], 
        28: [0, 9, 10, 12, 14, 16, 17, 18, 19, 23, 24, 25, 28, 29, 33, 42,
             44, 46, 48],  # 25 is moved from Region 22 to Region 28
        22: [4, 6, 7, 15, 21, 22, 27, 35, 36, 38, 39]
    },
    5: {24: [9, 16, 17, 18, 19, 23, 24, 30, 33, 42, 45, 47, 49],
        34: [1, 2, 26, 34, 37, 40, 41], 
        3: [3, 8, 11, 13, 20, 31, 32, 43], 
        22: [4, 5, 6, 7, 15, 21, 22, 25, 27, 36, 38, 39], 
        14: [0, 10, 12, 14, 28, 29, 35, 44, 46, 48]
    }
}
GE50_TRAFFIC_MAT = [[0.0]*len(GE50) for _ in range(len(GE50))]
sw_list = GE50_SOFT_LABELS['edge']
p = 1.0/(len(sw_list)**2-len(sw_list))
for src in sw_list:
    for dst in sw_list:
        if src == dst: continue
        GE50_TRAFFIC_MAT[src][dst] = p

GE50_TRAFFIC_LOGFILE = 'ge50.pkl'
GE50_TRAFFIC_DATA = 'ge50.json'

GE50_BURST_TRAFFIC_LOGFILE = 'burst.pkl'
GE50_BURST_TRAFFIC_DATA = 'burst.json'
GE50_TAIL_TRAFFIC_LOGFILE = 'tail.pkl'
GE50_TAIL_TRAFFIC_DATA = 'tail.json'

"""brain
161 nodes and 166 links
"""
BRAIN = [
    [2, 3, 9, 1, 12, 11, 13, 7, 8, 127, 6, 33, 4, 66, 5, 10],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [19, 47, 21, 23, 85, 28, 30, 27, 20, 16, 24, 32, 29, 31, 15, 26, 25, 17, 22, 18],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [14],
    [47, 42, 37, 44, 115, 43, 39, 34, 40, 0, 41, 45, 35, 46, 36, 38],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [33],
    [61, 62, 58, 59, 48, 52, 65, 63, 33, 64, 14, 85, 53, 115, 54, 56, 55, 60, 51, 50, 57, 49],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [47],
    [72, 73, 74, 75, 71, 84, 79, 67, 68, 69, 80, 81, 115, 127, 78, 0, 76, 77, 70, 82, 83],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [66],
    [47, 99, 14, 96, 98, 127, 104, 103, 102, 86, 92, 97, 100, 94, 95, 90, 93, 101, 88, 87, 91, 89],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [85],
    [107, 106, 111, 85, 110, 105, 114, 108, 112, 113, 109, 127],
    [104],
    [104],
    [104],
    [104],
    [104],
    [104],
    [104],
    [104],
    [104],
    [104],
    [117, 120, 119, 124, 126, 47, 33, 118, 66, 121, 122, 116, 125, 123],
    [115],
    [115],
    [115],
    [115],
    [115],
    [115],
    [115],
    [115],
    [115],
    [115],
    [115],
    [144, 155, 133, 134, 141, 158, 148, 85, 132, 138, 137, 136, 135, 0, 149, 150, 154, 151, 152, 153, 140, 157, 66, 139, 142, 143, 145, 146, 147, 128, 130, 131, 104, 156, 160, 159, 129],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127],
    [127]
]
BRAIN_SOFT_LABELS_CORE = [1, 15, 34, 48, 67, 86, 105, 116, 128]
BRAIN_SOFT_LABELS_EDGE = [label for label in range(len(BRAIN)) 
                          if label not in [0, 14, 33, 47, 66, 85, 104, 115, 127]]
BRAIN_REGIONS = {
    1: range(0, 14),
    15: range(14, 33),
    34: range(33, 47),
    48: range(47, 66),
    67: range(66, 85),
    86: range(85, 104),
    105: range(104, 115),
    116: range(115, 127),
    128: range(127, 161)
}
BRAIN_TRAFFIC_MAT = [[0.0]*len(BRAIN) for _ in range(len(BRAIN))]
sw_list = BRAIN_SOFT_LABELS_EDGE
p = 1.0/(len(sw_list)**2-len(sw_list))
for src in sw_list:
    for dst in sw_list:
        if src == dst: continue
        BRAIN_TRAFFIC_MAT[src][dst] = p

BRAIN_TRAFFIC_LOGFILE = 'brain.pkl'
BRAIN_TRAFFIC_DATA = 'brain.json'
BRAIN_RULE_PKL = 'brain_rule.pkl'


"""Classbench constants
"""
CB_RULE = 'fwrule'
CB_TRACE = 'fwrule_trace'
CB_RULE_PKL = 'cbrule.pkl'
CB_TRACE_LOGFILE = 'cbtrace.pkl'
