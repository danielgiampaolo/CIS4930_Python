import csv
import ctypes

"""
read(data: string)
"""
def read(data):
    nodeList = csv.DictReader(data.split('\n'), delimiter=',')

    """
    Each row is expected to have the following:
        - Node
        - Link
        - Neighbor
    """

    edges = []
    nodes = set()
    for row in nodeList:
        edges.append([row['Node'], row['Neighbor']])
        nodes.add(row['Node'])
        nodes.add(row['Neighbor'])

    return (list(nodes), edges)

class PerfRead(ctypes.Structure):
    _fields_ = [("nodes", ctypes.c_char), # types incomplete
                ("edges", ctypes.c_char)]

def load():
    lib = ctypes.cdll.LoadLibrary("./csv_parser.so")
    #lib.read.argtypes = [ctypes.c_char]
    #lib.read.restype = ctypes.POINTER(PerfRead)
    # do any other setup
    return lib

def c_read(data):
    # notes to self (deleting when done)
    # data is a string as far as I am aware
    # plan:
    # have struct shared by python and C
    # pass string to C library
    # init struct in C library
        # options:
            # string stream to use delimiter
            # then initialize lots of pointers
        # error checking:
            # no idea
    # read struct in Python side
    
    lib = load()
    lib.init()

    # coming back later, surfing stack overflow

    read_data = PerfRead.in_dll(lib, 'Ext_Struct')
    nodes, edges = read_data

    return (nodes, edges)
