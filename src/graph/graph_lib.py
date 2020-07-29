import enum
from ctypes import cdll, c_char_p, c_int, c_bool, POINTER, Structure


class Node(Structure):  # this structure is from Adithya (6 lines)
    _fields_ = [
        ('name', c_char_p),
        ('description', c_char_p),
        ('descriptionLines', c_int)
    ]

class State(Structure):
    _fields_ = [
        ('nodes', POINTER(Node)),
        ('edges', POINTER(c_char_p)),
        ('num_nodes', c_int),
        ('num_edges', c_int),
    ]


def load_c_graph_lib():
    lib = cdll.LoadLibrary("./graph/libc_graph.so")

    return lib


# library available by importing graph_lib
c_lib = load_c_graph_lib()

# define add_node
c_lib.add_node.restype = c_bool
c_lib.add_node.argtypes = [POINTER(State), c_char_p]

# define del_node
c_lib.del_node.restype = None
c_lib.del_node.argtypes = [POINTER(State)]


def init_nodes(nodes_to_c):  # this function is from Adithya (12 lines)
    print("init nodes: nodes_to_c")
    print(nodes_to_c)
    
    c_nodes = []
    for node in nodes_to_c:
        c_node = Node()
        c_node.name = node[0].encode('utf-8')
        c_node.description = node[1].encode('utf-8')
        c_node.descriptionLines = 1 # for the time being

        c_nodes.append(c_node)

    print("init nodes: c_nodes")
    for node in c_nodes:
        print(node.name, node.description)
    

    c_nodes_array = (Node * len(c_nodes))(*c_nodes)

    print("returning: c_nodes_array")
    print(c_nodes_array)
    for node in c_nodes_array:
        print("bruhhhhhhhhhhhhhhhhhhhhhhh")
        print(node.name, node.description)

    return c_nodes_array, len(c_nodes)


def init_state(session):
    cur_nodes = session.get('nodes', [])
    c_nodes, node_num = init_nodes(cur_nodes)

    cur_edges = session.get('edges', [])
    num_edges = len(cur_edges)

    edge_bytes = []  # name no longer accurate :'(
    for edge_from, edge_to, weight in cur_edges:
        from_ = c_char_p()
        to_ = c_char_p()
        weight_ = c_char_p()

        from_ = edge_from.encode('utf-8')
        to_ = edge_to.encode('utf-8')
        weight_ = (str(weight)).encode('utf-8')

        edge_bytes.append(from_)
        edge_bytes.append(to_)
        edge_bytes.append(weight_)

    c_edges = (c_char_p * ((num_edges * 3) + 1))(*edge_bytes) # wrong ?

    #  + 1 for a null array ? Testing printing

    print("init state: c_nodes")
    for node in c_nodes:
        print(node.name, node.description)

    print("init state: c_edges") # works
    for edge in c_edges:
        print(edge)

    state = State(c_nodes, c_edges, node_num, num_edges) # error here

    #print("state: nodes") # crashes? 
    #for node in state.nodes:
    #    print(node.name, node.description)
    # prints right, doesnt reach next print
    
    print("state: nodes") 
    for x in range(state.num_nodes):
        print(state.nodes[x].name, state.nodes[x].description)

    ##########################################################
    #print("state: edges") # now it does reach here
    #for edge in state.edges:
        #print(edge)

    #print("test") # same error, empty list element doesnt help
    ###########################################################

    #state.nodes = c_nodes  # type POINTER(Node)
    #state.num_nodes = node_num

    #state.edges = c_edges  # type POINTER(c_char)
    #state.num_edges = num_edges

    return state


# example
def c_add_node(response, node_name):
    # parameters needed for C function: State, new_node
    # initialize state for C
    cur_state = init_state(response.session)
    # get string to proper form
    new_node_bytes = node_name.encode('utf-8')

    # print("adding:")
    # print(new_node)

    # check for empty input box
    if node_name:
        add = c_lib.add_node(cur_state, new_node_bytes)

        if add:
            # print("add returned as true")
            cur_nodes = response.session.get('nodes', [])
            cur_edges = response.session.get('edges', [])

            cur_nodes.append([node_name, "Test add_node"])

            response.session['nodes'] = cur_nodes
            response.session['num_nodes'] = len(cur_nodes) + 1
            response.session['edges'] = cur_edges + [[node_name, node_name, 10]]
            response.session['num_edges'] = len(cur_edges) + 1


def c_delete_node(response):
    # get node (number) to delete
    to_delete = response.POST.get("deleteNode")

    cur_nodes = response.session.get('nodes', [])
    cur_edges = response.session.get('edges', [])

    # remove node at index
    deleted, _ = cur_nodes.pop(int(to_delete) - 1)

    # remove edges with removed node
    cur_edges = list(filter(lambda x: deleted not in x, cur_edges))
    # ISSUE: names might be unique but weights will not,
    # make sure this doesnt filter out this case:
    # deleted "1", example edge = [node1, node2, 1] (weight 1)
    # element 3 could happen to match, and be filtered

    # save changes to init state for C function
    response.session['nodes'] = cur_nodes
    response.session['edges'] = cur_edges

    # C state
    cur_state = init_state(response.session)


    # things done in C library (mainly loops):
    # 1. mark nodes with no connections
    # might look into:
        # Using malloc to create new array
        # to use less "filter" on python side

    # TODO:
    #  1. make C function also set the error messages from DG
    #  2. look into other performance options

    # C function use here:
    c_lib.del_node(cur_state)

    print("python")

    print("state nodes")
    print(cur_state.nodes[0])

    # get list without nodes marked for deletion (and decode)
    cur_nodes = [x.name.decode('utf-8') for x in cur_state.nodes if x.name]
    
    print("current nodes")
    print(cur_nodes)

    # decode edges and then put them in pairs
    cur_edges = [x.decode('utf-8') for x in cur_state.edges]
    cur_edges = list(zip(*[iter(cur_edges)]*3))
    
    print("current edges")
    print(cur_edges)

    # save new values
    response.session['nodes'] = cur_nodes
    response.session['edges'] = cur_edges
    response.session['num_nodes'] = len(cur_nodes)
    response.session['num_edges'] = len(cur_edges)


class Result(enum.Enum):
    No_Add = 0
    New_Edge = 1  # kind of redundant
    Add_From = 2  # 2/3/4 also imply 1
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
                                   c_int,  # number of nodes
                                   c_int,  # number of edges
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
            pass  # write error feedback reason
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
    # cur_nodes = response.session["nodes"]
    # cur_edges = response.session["edges"]
    # new_nodes = []
    # new_edges = []

    # currently using python version
    # Reason: Traversing POST request
    # Not Attempting (so far)

    # Note to Self:
    # look into... I cant even imagine what I would do right now

    pass
