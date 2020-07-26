from ctypes import cdll, c_char_p, c_char, POINTER, byref
import os


def load_c_graph_lib():
    #print("printing to environment to see correct include path")
    #print(os.environ)
    lib = cdll.LoadLibrary("./graph/libc_graph.so")
    # defining return types elsewhere
    #lib.add_node.restype = None
    #lib.add_node.argtypes = [POINTER(c_char_p), POINTER(c_char_p), c_char_p]
    return lib


# library available
c_lib = load_c_graph_lib()


# example
def c_add_node(response, new_node):
    #current_nodes = response.session.get('nodes', [])
    current_nodes = ["1","2"]
    num_nodes = len(current_nodes)

    c_lib.add_node.restype = None
    c_lib.add_node.argtypes = [c_char_p*num_nodes, c_char_p*num_nodes, c_char_p]

    new_node_bytes = new_node.encode('utf-8')

    # it just works
    c_curr_nodes = (c_char_p * num_nodes)()
    new_nodes = (c_char_p * num_nodes)()
    # adding one to len for null char

    node_bytes = []
    for i in range(num_nodes):
        node_bytes.append(current_nodes[i].encode('utf-8'))

    c_curr_nodes[:] = node_bytes

    print("current_nodes")
    print(current_nodes)
    print("new char* from current_nodes")
    print(list(c_curr_nodes))
    print("length of c_curr_nodes")
    print(len(c_curr_nodes))
    print("Testing modification of arrays in C")
    print("new_nodes before:")
    print(list(new_nodes))

    print("adding:")
    print(new_node)

    c_lib.add_node(c_curr_nodes, new_nodes, new_node_bytes)

    print("new_nodes after:")
    print(list(new_nodes))

# def c_test():
#    c_msg = msg.encode("cp437")
#    c_key = key.encode("cp437")
#    buf = create_string_buffer(len(msg))
#    lib.cipher(c_msg, c_key, buf, len(key), len(c_msg))
