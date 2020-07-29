from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import nodeInput
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from . import csv_parser, image_builder, graph_lib


@require_http_methods(["GET", "POST"])  # only GET & POST allowed
def index(request):
    # get data from session here
    graph_data = {
        "nodes": request.session.get('nodes', []),
        "edges": request.session.get('edges', []),
        "type": request.session.get('type', 'Undirected'),
        "num_nodes": request.session.get('num_nodes', 0),
        "num_edges": request.session.get('num_edges', 0),
        "misc": request.session.get('misc', {})
    }

    if request.method == "POST":
        return handle_graph_post(request)

    # else, handle GET
    return render(request, 'index.html', graph_data)


def handle_graph_post(response):
    #num_nodes = response.session.get('num_nodes', 0)
    #num_edges = response.session.get('num_edges', 0)
    #cur_nodes = response.session.get('nodes', [])
    #cur_edges = response.session.get('edges', [])
    # prev_post = response.session.get('prev', {}) could be used for "undo"
    misc = response.session.get('misc', {})

    form = nodeInput(response.POST)

    # print("printing POST")
    # print(response.POST)

    if form.is_valid():
        if response.POST.get("update"):
            updateFields(response)

        elif response.POST.get("addNode"):
            new_node_field = form.cleaned_data['newNode']
            graph_lib.c_add_node(response, new_node_field)

            #addNode(response, cur_nodes, num_nodes, cur_edges, num_edges, form)

        elif response.POST.get("addEdge"):
            graph_lib.c_add_edge(response)

            #add_edge(response)

            # was inside add_edge, up for review
            #return HttpResponseRedirect('/test_form')
            # commented out because it caused an error when here
            # testing removing it atm

        elif response.POST.get("deleteNode"):
            graph_lib.c_delete_node(response)

            #delNode(response, cur_nodes, num_nodes, cur_edges)

        elif response.POST.get("deleteEdge"):
            graph_lib.c_delete_edge(response)
            #delEdge(response, cur_edges, num_edges, cur_nodes)

        elif response.POST.get("open-upload"):
            misc['upload_open'] = True
            response.session['misc'] = misc

        elif response.POST.get("close-upload"):
            misc['upload_open'] = False
            response.session['misc'] = misc

        elif response.POST.get("upload-csv"):
            csv_upload(response)
            misc['upload_open'] = False
            response.session['misc'] = misc

        elif response.POST.get("clear"):
            response.session['nodes'] = []
            response.session['edges'] = []
            response.session['num_edges'] = 0
            response.session['num_nodes'] = 0
            response.session['misc'] = {}

        # store previous post. for reasons.
        # response.session['prev'] = response.POST

        # update plotly_dash's session state
        edges = response.session['edges']
        nodes = response.session['nodes']

        # TODO: add bold_edges here
        response.session['django_plotly_dash'] = {
            "edges": edges,
            "nodes": nodes,
        }

        return redirect('/')  # make a GET after changing session data

    else:

        # tell user something went wrong.
        # Error checking
        # Form validation
        # Etc.

        return redirect('/')


def updateFields(response):
    currentNodes = response.session["nodes"]
    currentEdges = response.session["edges"]
    updatedNodes = []
    updatedEdges = []

    # opportunity to optimize here
    # to reduce checks with smarter
    # algorithms/data_structure/etc

    # getting all updated nodes first
    for field, node in response.POST.items():

        if "node" in field and field != "newNode":
            # added check to ensure the name is new
            if not node in updatedNodes:
                updatedNodes = updatedNodes + [node]
            else:
                old_node = currentNodes[int(field[4:]) - 1]
                updatedNodes = updatedNodes + [old_node]

            if field[4:] == len(currentNodes):
                break
                # attempt to stop extra iterations

    # Not assuming I will see all the node fields before the edges.
    # Maybe I could.
    # Doing this to compare the new edge names to all the new node names.
    # With all updated nodes,
    # I will check that the changes in edges are limited to existing nodes.

    for field, node in response.POST.items():

        if "edge" in field and (not field == "newedgeto" and not field == "newedgefrom"):

            if "from" in field:
                number = field[4:-4]  # start after edge, exclude from => number used
                to_node = response.POST.get("edge" + number + "to")
                old_from = currentEdges[int(number) - 1][0]
                old_to = currentEdges[int(number) - 1][1]

                # possible errors when re-mapping edges

                if node in currentNodes and to_node in currentNodes:  # ok
                    updatedEdges = updatedEdges + [[node, to_node]]

                elif (not node in currentNodes) and to_node in currentNodes:
                    updatedEdges = updatedEdges + [[old_from, to_node]]

                elif node in currentNodes and (not to_node in currentNodes):
                    updatedEdges = updatedEdges + [[node, old_to]]

                else:  # both not in currentNodes
                    updatedEdges = updatedEdges + [[old_from, old_to]]

    # renaming edges from changed nodes
    for old_name, new_name in zip(currentNodes, updatedNodes):
        # find mismatched names
        if not old_name == new_name:
            # rename edge end points
            for edge_index, edge_pair in enumerate(updatedEdges):
                edge_from, edge_to = edge_pair

                if edge_from == old_name:
                    updatedEdges[edge_index][0] = new_name

                if edge_to == old_name:
                    updatedEdges[edge_index][1] = new_name

    # make current = updated
    response.session["nodes"] = updatedNodes
    response.session["edges"] = updatedEdges


def addNode(response, cur_nodes, num_nodes, cur_edges, num_edges, form):
    response.session['num_nodes'] = num_nodes + 1

    newNode = form.cleaned_data['newNode']

    if newNode not in cur_nodes:
        response.session['edges'] = cur_edges + [[newNode, newNode, 10]]
        response.session['num_edges'] = num_edges + 1
        cur_nodes = cur_nodes + [[form.cleaned_data['newNode']]]
        response.session['nodes'] = cur_nodes

    # since we are not rendering the "form" on html
    # updating the context is necessary
    # I dont know why I am using forms anymore

    # create node field
    # form.addNode(node_name, form.cleaned_data['newNode'])


def delNode(response, cur_nodes, num_nodes, current_edges):
    # get node to delete
    nodeDeleted = response.POST.get("deleteNode")

    # remove node at index
    deleting = cur_nodes.pop(int(nodeDeleted) - 1)

    # remove edges that point to or from that node
    current_edges = list(filter(lambda x: deleting not in x, current_edges))

    # necessary, to not modify and iterate at the same time (I think)
    check_nodes = cur_nodes.copy()

    # check all nodes and make sure they still have edges pointing to them
    for node in check_nodes:

        # checking edges for ends pointing to the a given node
        for from_node, to_node in current_edges:
            if from_node == node or to_node == node:
                break
                # if we find an edge point with the same name, good
        else:
            # if we didnt find anything...
            try:
                cur_nodes.remove(node)
            except ValueError:
                pass  # try block, just in case

    # save new values
    response.session['nodes'] = cur_nodes
    response.session['edges'] = current_edges
    response.session['num_edges'] = len(current_edges)
    response.session['num_nodes'] = len(cur_nodes)


def delEdge(response, cur_edges, num_edges, cur_nodes):
    response.session['num_edges'] = num_edges - 1

    # the value of POST[deleteEdge] should be just a number
    edgeDeleted = response.POST.get("deleteEdge")

    # could use list.pop()
    (deleted_from, deleted_to) = cur_edges[int(edgeDeleted) - 1]

    del cur_edges[int(edgeDeleted) - 1]

    # trying to find nodes to delete by checking
    # if there are edges left with their names

    # checking edges for ends pointing to the same as "deleted_from"
    for from_node, to_node in cur_edges:
        if from_node == deleted_from or to_node == deleted_from:
            break
            # if we find an edge point with the same name, good
    else:
        # if we didnt find anything...
        try:
            cur_nodes.remove(deleted_from)
        except ValueError:
            pass  # try block, just in case

    # now checking "deleted_to"
    for from_node, to_node in cur_edges:
        if from_node == deleted_to or to_node == deleted_to:
            break
    else:
        try:
            cur_nodes.remove(deleted_to)
        except ValueError:
            pass

    response.session['edges'] = cur_edges
    response.session['nodes'] = cur_nodes
    response.session['num_nodes'] = len(cur_nodes)
    response.session['num_edges'] = len(cur_edges)

    # if x == y:
    # response.session['nodes'] = list(filter(lambda z: x != z and y != z, cur_nodes))
    # response.session['num_nodes'] = len(response.session['nodes'])
    # else:
    #     if [x, x] not in cur_edges:
    #         cur_edges = cur_edges + [[x, x]]
    #     if [y, y] not in cur_edges:
    #         cur_edges = cur_edges + [[y, y]]

    #     response.session['edges'] = cur_edges
    #     response.session['num_edges'] = len(cur_edges)


def clear_all(response):
    response.session['nodes'] = []
    response.session['num_nodes'] = 0
    response.session['num_edges'] = 0
    response.session['edges'] = []

    return HttpResponse("Hello, world. You're at the graph index.")


def csv_upload(request):
    # request is guaranteed to be POST
    uploaded = request.FILES.get('csv-file')

    # modified "==" to "is" because pycharm complained
    if uploaded is None:
        print('Upload used, but no file found.')
        return JsonResponse({
            'message': 'No file found.'
        })

    if uploaded.content_type not in ['text/csv', 'application/vnd.ms-excel']:
        print('Was not CSV file')
        return JsonResponse({
            'message': 'not csv file (we got %s)' % uploaded.content_type
        })

    raw_bytes = uploaded.read()
    raw_data = raw_bytes.decode("utf-8")

    try:
        (nodes, edges) = csv_parser.read(raw_data)
        # use C version here
        # but actually no

    except Exception as e:
        print(e)
        return JsonResponse({
            'message': 'Something went wrong >:('
        })

    request.session['edges'] = edges
    request.session['nodes'] = nodes
    request.session['num_nodes'] = len(nodes)
    request.session['num_edges'] = len(edges)

    return


def csv_download(request):
    # CSV Headers: Node, Link, Neighbor
    headers = ('Node', 'Link', 'Neighbor')

    result = [','.join(headers)]
    edges = request.session.get('edges', [])

    for edge in edges:
        # as you can see, the link isn't carried over.
        # someone should fix that.
        result.append(','.join((edge[0], '0', edge[1])))

    return HttpResponse('\n'.join(result), content_type="text/csv")


def graph(request):
    try:
        nodes = request.session['nodes']
        edges = request.session['edges']
    except KeyError:
        return JsonResponse({
            'message': 'whats the big idea?! (data not found in session)'
        })

    if edges is None or nodes is None:
        return JsonResponse({
            'message': 'whats the big idea?! (data is None)'
        })

    (result, image) = image_builder.build_image(nodes, edges)

    if result == 0:
        x = HttpResponse(image, content_type='image/png')
        image.close()
        return x

    # something went wrong
    return JsonResponse({
        'message': 'something went wrong'
    })


def add_edge(request):
    if request.method != "POST":
        return JsonResponse({
            "message": "This is not a POST request."
        })

    from_node = request.POST.get('newedgefrom')
    to_node = request.POST.get('newedgeto')

    current_nodes = request.session.get('nodes', [])
    current_edges = request.session.get('edges', [])

    if [from_node, to_node] not in current_edges:
        if (from_node.strip()) and (to_node.strip()):
            if from_node not in current_nodes:
                current_nodes.append(from_node)
            if to_node not in current_nodes:
                current_nodes.append(to_node)
            current_edges.append([from_node, to_node])

            request.session['nodes'] = current_nodes
            request.session['edges'] = current_edges
            request.session['num_edges'] = len(current_edges)
            request.session['num_nodes'] = len(current_nodes)
