import csv
import ctypes
from ctypes import cdll, c_int, c_char_p, POINTER, Structure,byref

# Copy-Pasted from Enzo, Committed by Adrian
# For reference: 79 lines

class PerfRead(Structure):
    def __init__(self):
        self.nodes = None
        self.edges = None

    _fields_ = [("nodes", ctypes.POINTER(ctypes.c_char_p)),  # Temporary
                ("edges", ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))),
                ("node_size", c_int),
                ("edge_size", c_int)]

class DescRead(Structure):
    def __init__(self):
        self.desc = None
    _fields_ = [("desc", ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))),
                ("nodes_read", c_int),
                ("desc_num", POINTER(c_int))]

"""
read(data: string)
"""

def read(data):

    lib = load_library()
    data_bytes = data.encode("utf8")
    test = PerfRead()
    lib.read(data_bytes, byref(test))
    edges = []
    nodes = []

    for x in range(0, test.node_size):
        nodes.append([test.nodes[x].decode('utf8')])

    for x in range(0, test.edge_size):
        edges.append([test.edges[x][0].decode('utf8').strip(), test.edges[x][2].decode('utf8').strip(),test.edges[x][1].decode('utf8').strip()])
    lib.dealloc_read(test)
    return (list(nodes), edges)

def read_desc(data):

    lib = load_library()
    data_bytes = data.encode("utf8")
    test = DescRead()
    lib.read_desc(data_bytes, byref(test))
    nodes = []

    for x in range(0, test.nodes_read):
        nodes.append([test.desc[x][0].decode('utf8').strip()])
        for y in range(1, test.desc_num[x]):
            nodes[x].append(test.desc[x][y].decode('utf8').strip())

    lib.dealloc_desc(byref(test))
    return nodes

def load_library():
  lib = cdll.LoadLibrary('./graph/libc_graph.so')

  lib.read.restype = None
  lib.read.argtypes = [c_char_p, POINTER(PerfRead)]

  lib.read_desc.restype = None
  lib.read_desc.argtypes = [c_char_p, POINTER(DescRead)]

  lib.dealloc_read.restype = None
  lib.dealloc_read.argtypes = [POINTER(PerfRead)]

  lib.dealloc_desc.restype = None
  lib.dealloc_desc.argtypes = [POINTER(DescRead)]

  return lib