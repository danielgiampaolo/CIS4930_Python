import csv
import ctypes
from ctypes import cdll, c_int, c_char_p, POINTER, Structure,byref

class PerfRead(ctypes.Structure):
        def __init__(self):
            self.nodes = None
            self.edges = None

        _fields_ = [("nodes", ctypes.POINTER(ctypes.c_char_p)),  # Temporary
                    ("edges", ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))),
                    ("node_size", c_int),
                    ("edge_size", c_int)]

"""
read(data: string)
"""

def read(data):

    print(data)
    lib = load_library()
    data_bytes = data.encode("utf8")
    test = PerfRead()
    print("Going")
    lib.read(data_bytes,byref(test))
    print("Pringing edge 1")
    print(test.edges[0][1])
    edges = []
    nodes = []

    for x in range(0,test.node_size):
        nodes.append(test.nodes[x].decode('utf8'))

    # Need to add test.edges[x][1].decode('utf8') for weight 
    for x in range(0,test.edge_size):
        edges.append([test.edges[x][0].decode('utf8'),test.edges[x][2].decode('utf8')])

    return (list(nodes), edges)


def load():

    lib = ctypes.cdll.LoadLibrary("libc_graph.so")
    lib.read.argtypes = [ctypes.c_char_p, PerfRead]
    print("Returned Lib")
    #lib.read.restype = ctypes.POINTER(PerfRead)
    # do any other setup
    return lib

def load_library():
  lib = cdll.LoadLibrary('./graph/libnetview.so')
  print(lib)
  print("I printed the library")
  # set types

  lib.read.restype = None
  lib.read.argtypes = [c_char_p, POINTER(PerfRead)]

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


    print("nodes:")
    print(List(nodes))
    print("edges:")
    print(List(edges))

    # coming back later, surfing stack overflow

    print("testing C \"read\" function of csv parser")
    # call read at some point
    cur_data = ctypes.c_char_p()
    data_bytes = data.encode("utf8")
    cur_data[:] = data_bytes
    lib.read(cur_data) # maybe just data_bytes also works

    read_data = PerfRead.in_dll(lib, 'Ext_Struct')
    nodes, edges = read_data

    
    print("nodes:")
    print(List(nodes))
    print("edges:")
    print(List(edges))

    #return (nodes, edges)
