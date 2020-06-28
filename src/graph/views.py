from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from .forms import nodeInput
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from . import csv_parser, image_builder


@require_http_methods(["GET", "POST"])  # only GET & POST allowed
def index(request):
    # get vertices (or anything) from session info here
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
    num_nodes = response.session.get('num_nodes', 0)
    num_edges = response.session.get('num_edges', 0)
    cur_nodes = response.session.get('nodes', [])
    cur_edges = response.session.get('edges', [])
    misc = response.session.get('misc', {})

    form = nodeInput(response.POST)

    print("printing POST")
    print(response.POST)

    if form.is_valid():
        if response.POST.get("update"):
            updateFields(response, form)

        elif response.POST.get("addNode"):
            addNode(response, cur_nodes, num_nodes, cur_edges, num_edges, form)

        elif response.POST.get("addEdge"):
            add_edge(response)
            # addEdge(response, cur_edges, num_edges, form)

        elif response.POST.get("deleteNode"):
            delNode(response, cur_nodes, num_nodes, cur_edges)

        elif response.POST.get("deleteEdge"):
            pass
            delEdge(response, cur_edges, num_edges, cur_nodes)

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
            response.session['misc'] =  {}

        return redirect('/')  # make a GET after changing session data

    else:

        # tell user something went wrong.
        # Error checking
        # Form validation
        # Etc.

        return redirect('/')


def updateFields(response, form):
    currentNodes = response.session["nodes"]
    currentEdges = response.session["edges"]
    updatedNodes = []
    updatedEdges = []

    # opportunity to optimize here
    # to reduce checks with smarter
    # algorithms/data_structure/etc

    for field, node in response.POST.items():

        if "node" in field and field != "newNode":
            updatedNodes = updatedNodes + [node]

        if "edge" in field and ((not field == "newedgeto") and (not field == "newedgefrom")):

            if "from" in field:
                number = field[4:-4]  # start after edge, exclude from => number used
                to_node = response.POST.get("edge" + number + "to")

                updatedEdges = updatedEdges + [[node, to_node]]

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

    # renaming nodes from changed edges
    for old_pair, new_pair in zip(currentEdges, updatedEdges):
        old_edge_from, old_edge_to = old_pair
        new_edge_from, new_edge_to = new_pair

        # find mismatched node pairs (edges)
        if not old_edge_from == new_edge_from and not new_edge_from in updatedNodes:
            for node_index, node in enumerate(currentNodes):
                if node == old_edge_from:
                    updatedNodes[node_index] = new_edge_from
                    break

        if not old_edge_to == new_edge_to and not new_edge_to in updatedNodes:
            for node_index, node in enumerate(currentNodes):
                if node == old_edge_to:
                    updatedNodes[node_index] = new_edge_to
                    break

    # what if both are changed? Well... I would be mad. >:(
    # unless... node rename wins when both renamed

    # issues to check if they exist
    # what if they change to a name that doesnt exist
    # what if edges change to different nodes (feature ?)

    # make current = updated
    response.session["nodes"] = updatedNodes
    response.session["edges"] = updatedEdges


def addNode(response, cur_nodes, num_nodes, cur_edges, num_edges, form):
    response.session['num_nodes'] = num_nodes + 1

    newNode = form.cleaned_data['newNode']

    if newNode not in cur_nodes:
        response.session['edges'] = cur_edges + [[newNode, newNode]]
        response.session['num_edges'] = num_edges + 1
        cur_nodes = cur_nodes + [form.cleaned_data['newNode']]
        response.session['nodes'] = cur_nodes

    # since we are not rendering the "form" on html
    # updating the context is necessary
    # I dont know why I am using forms anymore

    # create node field
    # form.addNode(node_name, form.cleaned_data['newNode'])


def delNode(response, cur_nodes, num_nodes, current_edges):
    response.session['num_nodes'] = num_nodes - 1

    nodeDeleted = response.POST.get("deleteNode")

    deleting = cur_nodes[int(nodeDeleted) - 1]

    print('deleting ', deleting)

    del cur_nodes[int(nodeDeleted) - 1]

    response.session['nodes'] = cur_nodes
    response.session['edges'] = list(filter(lambda x: deleting not in x, current_edges))
    response.session['num_edges'] = len(response.session['edges'])


def delEdge(response, cur_edges, num_edges, cur_nodes):
    response.session['num_edges'] = num_edges - 1

    edgeDeleted = response.POST.get("deleteEdge")[-1]

    (x, y) = cur_edges[int(edgeDeleted) - 1]

    del cur_edges[int(edgeDeleted) - 1]

    response.session['edges'] = cur_edges

    # if x == y:
    response.session['nodes'] = list(filter(lambda z: x != z and y != z, cur_nodes))
    response.session['num_nodes'] = len(response.session['nodes'])
    # else:
    #     if [x, x] not in cur_edges:
    #         cur_edges = cur_edges + [[x, x]]
    #     if [y, y] not in cur_edges:
    #         cur_edges = cur_edges + [[y, y]]

    #     response.session['edges'] = cur_edges
    #     response.session['num_edges'] = len(cur_edges)


def clearAll(response):
    response.session['nodes'] = []
    response.session['num_nodes'] = 0
    response.session['num_edges'] = 0
    response.session['edges'] = []

    return HttpResponse("Hello, world. You're at the graph index.")


def csv_upload(request):
    # request is guaranteed to be POST
    uploaded = request.FILES.get('csv-file')

    if uploaded == None:
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


def graph(request):
    try:
        nodes = request.session['nodes']
        edges = request.session['edges']
    except KeyError:
        return JsonResponse({
            'message': 'whats the big idea?! (data not found in session)'
        })

    if edges == None or nodes == None:
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
            print('creating edge from %s to %s' % (from_node, to_node))

            request.session['nodes'] = current_nodes
            request.session['edges'] = current_edges

    return HttpResponseRedirect('/test_form')
