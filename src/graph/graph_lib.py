import enum
from ctypes import cdll, c_char_p, c_int, c_bool, POINTER, Structure, create_string_buffer, cast


# Exceptions
class EdgeExistsException(Exception):
    pass

# Structures
class Node(Structure):  # this structure is from Adithya (6 lines)
    _fields_ = [
        ('name', c_char_p),
        ('description', POINTER(c_char_p)),
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

# define add_edge
c_lib.add_edge.restype = c_int
c_lib.add_edge.argtypes = [POINTER(State), c_char_p, c_char_p]

# define del_edge
c_lib.del_edge.restype = None
c_lib.del_edge.argtypes = [POINTER(State), c_char_p, c_char_p, ]


def init_nodes(nodes_to_c):  # this function is from Adithya (12 lines)

    c_nodes = []
    for [name, *description] in nodes_to_c:
        c_node = Node()

        mutable_name = create_string_buffer(name.encode('utf-8'))
        c_node.name = cast(mutable_name,c_char_p)

        line_count = len(description)

        if line_count == 0: 
            c_node.description = (c_char_p * 1)("".encode('utf-8'))
            # it threw errors before so x * 1 -> *just works*
            # possibly fits data type after that
        else:
            c_node.description = (c_char_p * line_count)(*[line.encode('utf-8') for line in description])

        c_node.descriptionLines = line_count

        c_nodes.append(c_node)

    c_nodes_array = (Node * len(c_nodes))(*c_nodes)

    return c_nodes_array, len(c_nodes)


def init_state(session):
    cur_nodes = session.get('nodes', [])
    c_nodes, node_num = init_nodes(cur_nodes)

    cur_edges = session.get('edges', [])
    num_edges = len(cur_edges)

    edge_bytes = []
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

    c_edges = (c_char_p * ((num_edges * 3)))(*edge_bytes)

    state = State(c_nodes, c_edges, node_num, num_edges)

    # important: DOESNT WORK
    # print("state: nodes")
    # for node in state.nodes:
    #    print(node.name, node.description)
    # prints right, doesnt reach next print

    # works (will leave as example)
    #print("state: nodes")
    #for x in range(state.num_nodes):
    #    print(state.nodes[x].name)
    #
    #print("state: edges")
    #for x in range(state.num_edges):
    #    print(state.edges[3 * x], state.edges[3 * x + 1], state.edges[3 * x + 2])

    return state


# example
def c_add_node(response, node_name):
    # print("adding:")
    # print(new_node)

    # check for empty input box
    if node_name:
        # initialize state for C
        cur_state = init_state(response.session)
        # get string to proper form
        new_node_bytes = node_name.encode('utf-8')

        add = c_lib.add_node(cur_state, new_node_bytes)

        if add:
            # print("add returned as true")
            cur_nodes = response.session.get('nodes', [])
            cur_edges = response.session.get('edges', [])

            cur_nodes.append([node_name, "Node created from sidebar"])

            response.session['nodes'] = cur_nodes
            response.session['num_nodes'] = len(cur_nodes)
            response.session['edges'] = cur_edges + [[node_name, node_name, 10]]
            response.session['num_edges'] = len(cur_edges)


def c_delete_node(response):
    # get node (number) to delete
    to_delete = response.POST.get("deleteNode")

    cur_nodes = response.session.get('nodes', [])
    cur_edges = response.session.get('edges', [])

    # remove node at index
    deleted = cur_nodes.pop(int(to_delete) - 1)
    deleted_name, _ = deleted

    # remove edges with removed node (attempt to exclude weight below)
    cur_edges = list(filter(lambda x: deleted_name not in x[:2], cur_edges))

    # save changes to init state for C function
    response.session['nodes'] = cur_nodes
    response.session['edges'] = cur_edges
    response.session['num_nodes'] = len(cur_nodes)
    response.session['num_edges'] = len(cur_edges)

    # C state
    state = init_state(response.session)

    # TODO:
    #  1. make C function also set the error messages from DG

    # C function use here:
    c_lib.del_node(state)

    node_count = range(state.num_nodes)

    nodes = [
        [state.nodes[x].name.decode('utf-8')] +
        [state.nodes[x].description[i].decode('utf-8') for i in range(state.nodes[x].descriptionLines)]
        for x in node_count if state.nodes[x].name
    ]

    # decode edges and then put them in pairs
    edge_count = range(state.num_edges * 3)
    cur_edges = [state.edges[x].decode('utf-8') for x in edge_count]
    cur_edges = list(zip(*[iter(cur_edges)] * 3))

    # save new values
    response.session['nodes'] = nodes
    response.session['edges'] = cur_edges
    response.session['num_nodes'] = len(nodes)
    response.session['num_edges'] = len(cur_edges)


class Result(enum.Enum):
    No_Add = 0
    New_Edge = 1  # kind of redundant
    Add_From = 2  # 2/3/4 also imply 1
    Add_To = 3
    Add_Both = 4


def c_add_edge(session, from_node, to_node, weight):
    cur_state = init_state(session)

    from_node_bytes = from_node.encode('utf-8')
    to_node_bytes = to_node.encode('utf-8')

    op = c_lib.add_edge(cur_state, from_node_bytes, to_node_bytes)

    if op == Result.No_Add.value:
        raise EdgeExistsException
    else:
        cur_nodes = session.get('nodes', [])
        cur_edges = session.get('edges', [])

        cur_edges.append([from_node, to_node, weight])

        # doing enum.value is wack
        if op == Result.Add_From.value:
            cur_nodes.append([from_node, "Node created when adding edge"])

        elif op == Result.Add_To.value:
            cur_nodes.append([to_node, "Node created when adding edge"])

        elif op == Result.Add_Both.value:
            cur_nodes.append([from_node, "Node created when adding edge"])
            cur_nodes.append([to_node, "Node created when adding edge"])

    # save
    session['nodes'] = cur_nodes
    session['edges'] = cur_edges
    session['num_nodes'] = len(cur_nodes)
    session['num_edges'] = len(cur_edges)


def c_delete_edge(response):
    edges = response.session.get('edges', [])

    to_delete = response.POST.get("deleteEdge")

    # edge clicked for deletion is gone
    (deleted_from, deleted_to, _) = edges.pop(int(to_delete) - 1)

    # save to initialize C state
    response.session['edges'] = edges
    response.session['num_edges'] = len(edges)

    state = init_state(response.session)

    # put bytes into C container
    from_node_bytes = deleted_from.encode('utf-8')
    to_node_bytes = deleted_to.encode('utf-8')

    # checking connections
    c_lib.del_edge(state, from_node_bytes, to_node_bytes)

    node_count = range(state.num_nodes)
    nodes = [
        [state.nodes[x].name.decode('utf-8')] +
        [state.nodes[x].description[i].decode('utf-8') for i in range(state.nodes[x].descriptionLines)]
        for x in node_count if state.nodes[x].name
    ]
    # cur_edges = [x.decode('utf-8') for x in cur_state.edges]
    edges = [state.edges[x].decode('utf-8') for x in range(state.num_edges * 3)]
    edges = list(zip(*[iter(edges)] * 3))

    # save
    response.session['nodes'] = nodes
    response.session['edges'] = edges
    response.session['num_nodes'] = len(nodes)
    response.session['num_edges'] = len(edges)


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
