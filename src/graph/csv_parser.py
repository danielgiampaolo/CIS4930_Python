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
    nodes_set = set()
    for row in nodeList:
        edges.append([row['Node'], row['Neighbor'], row['Link']])
        nodes_set.add(row['Node'])
        nodes_set.add(row['Neighbor'])

    # TODO: remove/update later
    nodes = []
    i = 1
    for node in list(nodes_set):
        data = [node]

        if i % 2 == 0:
            data.append('line1')
            data.append('line2')

        nodes.append(data)
        i = i + 1

    return (nodes, edges)


class PerfRead(ctypes.Structure):
    _fields_ = [("nodes", ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))),  # Temporary
                ("edges", ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))))]


def load():
    lib = ctypes.cdll.LoadLibrary("./csv_parser.so")
    lib.read.argtypes = [ctypes.c_char_p]
    # lib.read.restype = ctypes.POINTER(PerfRead)
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

    print("testing C init of csv parser")
    lib.init()

    read_data = PerfRead.in_dll(lib, 'Ext_Struct')
    nodes, edges = read_data

    print("nodes:")
    print(list(nodes))
    print("edges:")
    print(list(edges))

    # coming back later, surfing stack overflow

    print("testing C \"read\" function of csv parser")
    # call read at some point
    cur_data = ctypes.c_char_p()
    data_bytes = data.encode("utf8")
    cur_data[:] = data_bytes
    lib.read(cur_data)  # maybe just data_bytes also works

    read_data = PerfRead.in_dll(lib, 'Ext_Struct')
    nodes, edges = read_data

    print("nodes:")
    print(list(nodes))
    print("edges:")
    print(list(edges))

    # return (nodes, edges)