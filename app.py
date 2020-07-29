from ctypes import cdll, c_int, c_char_p, POINTER, Structure

class Node(Structure):
  _fields_ = [
    ('Name', c_char_p),
    ('Description', POINTER(c_char_p)),
    ('DescriptionLines', c_int)
  ]

def main():
  print("trying to use library!")
  lib = load_library()

  # message = "What is this?".encode('utf-8')
  # buffer = create_string_buffer(len(message))
  # lib.cipher(message, buffer, len(message))

  # print('got the following: "%s"' % buffer.raw.decode('utf-8'))

  # print()

  sample_nodes = [
    [
      'Node one',
      [
        'Line 1',
        'Line 2'
      ]
    ],
    [
      'Node two',
      [
        'Line 3',
        'Line 4'
      ]
    ]
  ]

  c_nodes = []
  for node in sample_nodes:
    c_node = Node()
    c_node.Name = node[0].encode('utf-8')
    c_node.Description = (c_char_p * len(node[1]))(*[line.encode('utf-8') for line in node[1]])
    c_node.DescriptionLines = len(node[1])

    c_nodes.append(c_node)

  c_nodes_array = (Node * len(c_nodes))(*c_nodes)

  lib.rename_node(c_nodes_array, len(c_nodes))
  print("nani??")


def load_library():
  lib = cdll.LoadLibrary('./libnetview.so')

  # set types
  lib.cipher.restype = None
  lib.cipher.argtypes = [POINTER(Node), c_int]

  lib.rename_node.restype = None
  lib.rename_node.argtypes = []

  return lib


if __name__ == "__main__":
  main()
