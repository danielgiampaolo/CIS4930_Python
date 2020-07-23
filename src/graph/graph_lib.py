from ctypes import cdll, c_char_p, c_int, c_bool, POINTER


def load_c_graph_lib():
    # print("printing to environment to see correct include path")
    # print(os.environ)
    lib = cdll.LoadLibrary("./graph/libc_graph.so")
    # defining return types elsewhere
    # lib.add_node.restype = None
    # lib.add_node.argtypes = [POINTER(c_char_p), POINTER(c_char_p), c_char_p]
    return lib


# library available
c_lib = load_c_graph_lib()


# example
def c_add_node(response, new_node):
    current_nodes = response.session.get('nodes', [])
    num_nodes = len(current_nodes)

    # define library properties
    c_lib.add_node.restype = c_bool
    c_lib.add_node.argtypes = [c_char_p * num_nodes, c_int, c_char_p]

    # get string to proper form
    new_node_bytes = new_node.encode('utf-8')

    # parameters for C function
    c_curr_nodes = (c_char_p * num_nodes)()
    # also num_nodes & new_node

    # encoding array for passing into C
    node_bytes = []
    for i in range(num_nodes):
        node_bytes.append(current_nodes[i].encode('utf-8'))

    # put bytes into C container
    c_curr_nodes[:] = node_bytes

    print("current_nodes")
    print(current_nodes)
    print("new char** from current_nodes")
    print(list(c_curr_nodes))

    print("adding:")
    print(new_node)

    if new_node:
        add = c_lib.add_node(c_curr_nodes, num_nodes, new_node_bytes)

        if add:
            print("add returned as true")
            current_nodes.append(new_node)

            cur_edges = response.session.get('edges', [])

            response.session['nodes'] = current_nodes
            response.session['num_nodes'] = num_nodes + 1
            response.session['edges'] = cur_edges + [[new_node, new_node]]
            response.session['num_edges'] = len(cur_edges) + 1

    print("\nnew_nodes after:")
    print(list(current_nodes))


def c_delete_node(response):
    # get node (number) to delete
    to_delete = response.POST.get("deleteNode")

    cur_nodes = response.session.get('nodes', [])
    cur_edges = response.session.get('edges', [])

    # remove node at index
    deleted = cur_nodes.pop(int(to_delete) - 1)

    num_nodes = len(cur_nodes)
    num_edges = len(cur_edges)

    # define library properties
    c_lib.del_node.restype = None
    c_lib.del_node.argtypes = [c_char_p * num_nodes,  # pointer to nodes_array
                               # magic right below   # pointer to edges_array
                               (c_char_p * 2) * num_edges,
                               c_int,  # number of nodes
                               c_int,  # number of edges
                               c_char_p  # name of node deleted
                               ]

    # get parameters ready
    del_node_bytes = deleted.encode('utf-8')
    c_cur_nodes = (c_char_p * num_nodes)()
    c_cur_edges = ((c_char_p * 2) * num_edges)()
    # other parameters: # of nodes & # of edges

    # encoding arrays for putting into object created above
    node_bytes = []
    for i in range(num_nodes):
        node_bytes.append((cur_nodes[i] + '\0').encode('utf-8'))

    # put bytes into C container
    c_cur_nodes[:] = node_bytes

    for i in range(num_edges):
        print('encoding: ', cur_edges[i][0], cur_edges[i][1])
        c_cur_edges[i][0] = (cur_edges[i][0] + '\0').encode('utf-8')
        c_cur_edges[i][1] = (cur_edges[i][1] + '\0').encode('utf-8')
        # ¯\_(ツ)_/¯ idk

    print("c_cur_edges")
    for c_pairs in c_cur_edges:
        print(list(c_pairs))

    # things done in C library (mainly loops):
        # 1. delete edges with deleted node
        # 2. delete nodes with no connections

    # returns nothing
    c_lib.del_node(c_cur_nodes, c_cur_edges, num_nodes, num_edges, del_node_bytes)

    print("after C function")
    print("c_cur_edges")
    for c_pairs in c_cur_edges:
        print(list(c_pairs))
