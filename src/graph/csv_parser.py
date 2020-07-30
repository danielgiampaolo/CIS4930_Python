import csv
import ctypes
from ctypes import cdll, c_int, c_char_p, POINTER, Structure,byref

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
    print(data)
    lib = load_library()
    data_bytes = data.encode("utf8")
    test = DescRead()
    print("Going")
    lib.read_desc(data_bytes,byref(test))
    print("Returned")
    nodes = []

    for x in range(0,test.nodes_read):
        nodes.append([test.desc[x][0].decode('utf8'), []])
        for y in range(1,test.desc_num[x]):
            nodes[x][1].append(test.desc[x][y].decode('utf8'))

    

def load_library():
  lib = cdll.LoadLibrary('./graph/libnetview.so')
  print(lib)
  print("I printed the library")
  # set types

  lib.read.restype = None
  lib.read.argtypes = [c_char_p, POINTER(PerfRead)]

  lib.read_desc.restype = None
  lib.read_desc.argtypes = [c_char_p, POINTER(DescRead)]

  return lib