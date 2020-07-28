import enum
from ctypes import cdll, c_char_p, c_int, c_bool, POINTER


def load_c_graph_lib():

    lib = cdll.LoadLibrary("./graph/libc_graph.so")
    # can define return types here
    # c_lib.add_node.restype = c_bool

    # defining arguments types elsewhere
    # c_lib.add_node.argtypes = [c_char_p * num_nodes, c_int, c_char_p]
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
        node_bytes.append((current_nodes[i] + '\0').encode('utf-8'))

    # put bytes into C container
    c_curr_nodes[:] = node_bytes

    #print("current_nodes")
    #print(current_nodes)
    #print("new char** from current_nodes")
    #print(list(c_curr_nodes))

    #print("adding:")
    #print(new_node)

    if new_node:
        add = c_lib.add_node(c_curr_nodes, num_nodes, new_node_bytes)

        if add:
            #print("add returned as true")
            current_nodes.append(new_node)

            cur_edges = response.session.get('edges', [])

            response.session['nodes'] = current_nodes
            response.session['num_nodes'] = num_nodes + 1
            response.session['edges'] = cur_edges + [[new_node, new_node]]
            response.session['num_edges'] = len(cur_edges) + 1

    #print("\nnew_nodes after:")
    #print(list(current_nodes))


def c_delete_node(response):
    # get node (number) to delete
    to_delete = response.POST.get("deleteNode")

    cur_nodes = response.session.get('nodes', [])
    cur_edges = response.session.get('edges', [])

    # remove node at index
    deleted = cur_nodes.pop(int(to_delete) - 1)

    # remove edges with removed node
    cur_edges = list(filter(lambda x: deleted not in x, cur_edges))

    num_nodes = len(cur_nodes)
    num_edges = len(cur_edges)

    # TODO
    #  1. Look into initializing the function only once
    #       a. Perhaps a boolean for this function

    # define library properties
    c_lib.del_node.restype = None
    c_lib.del_node.argtypes = [c_char_p * num_nodes,  # pointer to nodes_array
                               c_char_p * (num_edges * 2), # pointer to edges_array
                               c_int,  # number of nodes
                               c_int,  # number of edges
                               c_char_p  # name of node deleted
                               ]

    # get parameters ready
    del_node_bytes = deleted.encode('utf-8')
    c_cur_nodes = (c_char_p * num_nodes)()
    c_cur_edges = (c_char_p * (num_edges * 2))()
    # other parameters: # of nodes & # of edges

    # encoding arrays for putting into object created above
    node_bytes = []
    for i in range(num_nodes):
        node_bytes.append((cur_nodes[i] + '\0').encode('utf-8'))

    edge_bytes = []
    for i in range(num_edges):
        edge_bytes.append((cur_edges[i][0] + '\0').encode('utf-8'))
        edge_bytes.append((cur_edges[i][1] + '\0').encode('utf-8'))
        # ¯\_(ツ)_/¯ idk
        # doing 1D array because I dont know how to pass 2D array to C
        # it crashes when I try reading what I set up

    # put bytes into C container
    c_cur_nodes[:] = node_bytes
    c_cur_edges[:] = edge_bytes

    # things done in C library (mainly loops):
        # 1. mark nodes with no connections
    # might look into:
        # Using malloc to create new array
        # to use less "filter" on python side

    # TODO:
    #  1. make C function also set the error messages from DG
    #  2. look into other performance options

    # print("testing removing a node")
    # print(c_cur_edges)

    # C function use here:
    c_lib.del_node(c_cur_nodes, c_cur_edges, num_nodes, num_edges, del_node_bytes)

    # get list without nodes marked for deletion (and decode)
    cur_nodes = [x.decode('utf-8') for x in c_cur_nodes if x]
    # decode edges and then put them in pairs
    cur_edges = [x.decode('utf-8') for x in c_cur_edges]
    cur_edges = list(zip(cur_edges[::2], cur_edges[1::2]))

    print("after del_node")
    print("current nodes")
    print(cur_nodes)
    print("current edges")
    print(cur_edges)

    # save new values
    response.session['nodes'] = cur_nodes
    response.session['edges'] = cur_edges
    response.session['num_nodes'] = len(cur_nodes)
    response.session['num_edges'] = len(cur_edges)

class Result(enum.Enum):
    No_Add = 0
    New_Edge = 1 # kind of redundant
    Add_From = 2 # 2/3/4 also imply 1
    Add_To = 3
    Add_Both = 4


def c_add_edge(response):
    from_node = response.POST.get('newedgefrom').strip()
    to_node = response.POST.get('newedgeto').strip()

    if from_node and to_node:
        # start business after checking valid new edges

        cur_nodes = response.session.get('nodes', [])
        cur_edges = response.session.get('edges', [])

        # TODO
        #  1. Look into initializing the function only once
        #       a. Perhaps a boolean for this function

        num_nodes = len(cur_nodes)
        num_edges = len(cur_edges)

        # define library properties
        c_lib.add_edge.restype = c_int
        c_lib.add_edge.argtypes = [c_char_p * num_nodes,  # pointer to nodes_array
                                   c_char_p * (num_edges * 2),  # pointer to edges_array
                                   c_int,     # number of nodes
                                   c_int,     # number of edges
                                   c_char_p,  # name of new to_node
                                   c_char_p,  # name of new from_node
                                   ]

        c_nodes = (c_char_p * num_nodes)()
        c_edges = (c_char_p * (num_edges * 2))()

        node_bytes = []
        for node in cur_nodes:
            node_bytes.append((node + '\0').encode('utf-8'))

        edge_bytes = []
        for edge_from, edge_to in cur_edges:
            edge_bytes.append((edge_from + '\0').encode('utf-8'))
            edge_bytes.append((edge_to + '\0').encode('utf-8'))

        # put bytes into C container
        c_nodes[:] = node_bytes
        c_edges[:] = edge_bytes
        from_node_bytes = from_node.encode('utf-8')
        to_node_bytes = to_node.encode('utf-8')

        # TODO
        #  1. Remember to add feedback error msg

        # sorry for the long function calls, should use structs
        op = c_lib.add_edge(c_nodes, c_edges, num_nodes, num_edges,
                       from_node_bytes, to_node_bytes)

        if op == Result.No_Add:
            pass # write error feedback reason
        else:
            cur_edges.append([from_node, to_node])

            # print("op equals =", op)

            # doing enum.value is wack
            if op == Result.Add_From.value:
                cur_nodes.append(from_node)

            elif op == Result.Add_To.value:
                cur_nodes.append(to_node)

            elif op == Result.Add_Both.value:
                cur_nodes.append(from_node)
                cur_nodes.append(to_node)

        print("after add_edge:")
        print("nodes:")
        print(cur_nodes)
        print("edges:")
        print(cur_edges)

        # save
        response.session['nodes'] = cur_nodes
        response.session['edges'] = cur_edges
        response.session['num_nodes'] = len(cur_nodes)
        response.session['num_edges'] = len(cur_edges)

def c_delete_edge(response):
    cur_nodes = response.session.get('nodes', [])
    cur_edges = response.session.get('edges', [])

    edge_deleted = response.POST.get("deleteEdge")

    # edge clicked for deletion is gone
    (deleted_from, deleted_to) = cur_edges.pop(int(edge_deleted) - 1)

    num_nodes = len(cur_nodes)
    num_edges = len(cur_edges)

    # define library properties
    c_lib.del_edge.restype = None
    c_lib.del_edge.argtypes = [c_char_p * num_nodes,  # pointer to nodes_array
                               c_char_p * (num_edges * 2),  # pointer to edges_array
                               c_int,  # number of nodes
                               c_int,  # number of edges
                               c_char_p,  # deleted "from"
                               c_char_p,  # deleted "to"
                               ]

    c_nodes = (c_char_p * num_nodes)()
    c_edges = (c_char_p * (num_edges * 2))()

    # appending the null character might be unnecessary, didnt try it

    node_bytes = []
    for node in cur_nodes:
        node_bytes.append((node + '\0').encode('utf-8'))

    edge_bytes = []
    for edge_from, edge_to in cur_edges:
        edge_bytes.append((edge_from + '\0').encode('utf-8'))
        edge_bytes.append((edge_to + '\0').encode('utf-8'))

    # put bytes into C container
    c_nodes[:] = node_bytes
    c_edges[:] = edge_bytes
    from_node_bytes = deleted_from.encode('utf-8')
    to_node_bytes = deleted_to.encode('utf-8')

    # after the desired edge was removed
    # in C, iterate over edges to
    # find connections for remaining nodes
    # if no connections are found for a node
    # it is marked for deletion
    # and deleted in python
    # for extra work, allocation of new edge array
    # could be done in C, if enough hands/time

    # checking connections
    c_lib.del_edge(c_nodes, c_edges, num_nodes, num_edges,
                        from_node_bytes, to_node_bytes)

    # get list without nodes marked for deletion (and decode)
    cur_nodes = [x.decode('utf-8') for x in c_nodes if x]
    # decode edges and then put them in pairs
    cur_edges = [x.decode('utf-8') for x in c_edges]
    cur_edges = list(zip(cur_edges[::2], cur_edges[1::2]))

    print("after del_node")
    print("current nodes")
    print(cur_nodes)
    print("current edges")
    print(cur_edges)

    # save
    response.session['nodes'] = cur_nodes
    response.session['edges'] = cur_edges
    response.session['num_nodes'] = len(cur_nodes)
    response.session['num_edges'] = len(cur_edges)

def c_update_names(response):
    #cur_nodes = response.session["nodes"]
    #cur_edges = response.session["edges"]
    #new_nodes = []
    #new_edges = []

    # currently using python version
    # Reason: Traversing POST request
    # Not Attempting (so far)

    # Note to Self:
    # look into... I cant even imagine what I would do right now

    pass




