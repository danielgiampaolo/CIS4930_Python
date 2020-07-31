from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import nodeInput
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from . import csv_parser, image_builder, graph_lib

# temporary test method (add to urls manually)
def test(request):
    return JsonResponse({
        'session': {
            'num_edges': request.session.get('num_edges', 0),
            'num_nodes': request.session.get('num_nodes', 0),
            'nodes': request.session.get('nodes', []),
            'edges': request.session.get('edges', []),
        }
    })

@require_http_methods(["GET", "POST"])  # only GET & POST allowed
def index(request):
    # get data from session here
    graph_data = {
        "nodes": request.session.get('nodes', []),
        "edges": request.session.get('edges', []),
        "type": request.session.get('type', 'Undirected'),
        "num_nodes": request.session.get('num_nodes', 0),
        "num_edges": request.session.get('num_edges', 0),
        "misc": request.session.get('misc', {}),
        "node_error": request.session.get('node_error', ''),
        "edge_error": request.session.get('edge_error', ''),
        "path_error": request.session.get('path_error', ''),
        "file_content": request.session.get('file_content', ''),
        "start": request.session.get('start', ''),
        "end": request.session.get('end', '')
    }

    if request.method == "POST":
        return handle_graph_post(request)

    # update plotly_dash's session state
    # TODO: add bold_edges here
    request.session['django_plotly_dash'] = {
        "edges": request.session.get('edges', []),
        "nodes": request.session.get('nodes', []),
    }

    # else, handle GET
    return render(request, 'index.html', graph_data)


def handle_graph_post(response):
    # prev_post = response.session.get('prev', []) could be used for "undo"
    misc = response.session.get('misc', {})

    form = nodeInput(response.POST)

    if form.is_valid():
        if response.POST.get("update"):
            updateFields(response)

        elif response.POST.get("addNode"):
            new_node_field = form.cleaned_data['newNode']
            graph_lib.c_add_node(response, new_node_field)

            #addNode(response, cur_nodes, num_nodes, cur_edges, num_edges, form)

        elif response.POST.get("addEdge"):
            add_edge(response)
        
        elif response.POST.get("addPath"):
            add_path(response)

        elif response.POST.get("deleteNode"):
            graph_lib.c_delete_node(response)

            #delNode(response, cur_nodes, num_nodes, cur_edges)

        elif response.POST.get("deleteEdge"):
            graph_lib.c_delete_edge(response)
            #delEdge(response, cur_edges, num_edges, cur_nodes)

        elif response.POST.get("open-upload"):
            response.session['file_content'] = response.POST.get("open-upload")
            misc['upload_open'] = True
            response.session['misc'] = misc

        elif response.POST.get("close-upload"):
            misc['upload_open'] = False
            response.session['misc'] = misc

        elif response.POST.get("upload-csv"):
            csv_upload(response)
            misc['upload_open'] = False
            response.session['misc'] = misc
            response.session['file_content'] = ''

        elif response.POST.get("clear"):
            clearAll(response)

        # store previous post. for reasons.
        # response.session['prev'] = response.POST

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
    from_node = response.POST.get('start')
    to_node = response.POST.get('end')
    response.session['start'] = from_node
    response.session['end'] = to_node

    # opportunity to optimize here
    # to reduce checks with smarter
    # algorithms/data_structure/etc

    # getting all updated nodes first
    for field, node in response.POST.items():

        if "node" in field and field != "newNode":
            # added check to ensure the name is new
            if not node in updatedNodes:
                old_node = currentNodes[int(field[4:]) - 1]
                updatedNodes = updatedNodes + [node, old_node[1:]]
                response.session['node_error'] = ''
            else:
                old_node = currentNodes[int(field[4:]) - 1]
                updatedNodes = updatedNodes + [old_node]
                response.session['node_error'] = old_node + " not changed, new name conflicts with existing node!"

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
                old_from, old_to, old_weight = currentEdges[int(number) - 1]

                # possible errors when re-mapping edges
                # New Note: When weights are added to POST,
                # update below to new weights (do checks if necessary w/e)

                if node in currentNodes and to_node in currentNodes:  # ok
                    updatedEdges = updatedEdges + [[node, to_node, old_weight]]

                elif (not node in currentNodes) and to_node in currentNodes:
                    updatedEdges = updatedEdges + [[old_from, to_node, old_weight]]

                elif node in currentNodes and (not to_node in currentNodes):
                    updatedEdges = updatedEdges + [[node, old_to, old_weight]]

                else:  # both not in currentNodes
                    updatedEdges = updatedEdges + [[old_from, old_to, old_weight]]

    # renaming edges from changed nodes
    for old_node_info, new_node_info in zip(currentNodes, updatedNodes):
        print(new_node_info)
        print(old_node_info)

        old_name = old_node_info
        new_name = new_node_info

        # find mismatched names
        if not old_name == new_name:
            # rename edge end points
            for edge_index, edge_pair in enumerate(updatedEdges):
                edge_from, edge_to, weight = edge_pair

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
        response.session['node_error'] = 'Node Added: ' + newNode
    else:
        response.session['node_error'] = "Node not added, node already exists!"

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
    response.session['node_error'] = 'Node Deleted: ' + nodeDeleted


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
    response.session['start'] = ''
    response.session['end'] = ''

    return HttpResponse("Hello, world. You're at the graph index.")


def csv_upload(request):
    # request is guaranteed to be POST
    file_content = request.session['file_content']
    uploaded = request.FILES.get('csv-file')
    if file_content == 'edges':
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
    elif file_content == 'nodes':
        print('Nodes selected')

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
        start = request.session['start']
        end = request.session['end']
    except KeyError:
        return JsonResponse({
            'message': 'whats the big idea?! (data not found in session)'
        })

    if edges is None or nodes is None:
        return JsonResponse({
            'message': 'whats the big idea?! (data is None)'
        })

    (result, image) = image_builder.build_image(nodes, edges, start, end)

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

    from_node = request.POST.get('newedgefrom').strip()
    to_node = request.POST.get('newedgeto').strip()
    weight = 10 # TODO: when merging weights, fix
    
    if from_node and to_node:
        try:
            graph_lib.c_add_edge(request.session, from_node, to_node, weight)
        except graph_lib.EdgeExistsException:
            print("edge exists already!")
        # TODO: Re-enable in production; disabled for stack-trace
        # except Exception as e:
        #     print("something wrong :(", e)

def add_path(response):
    # if node has no connection to destination node, graph will break.
    # caught in image_builder, but makes it a refresh late on page...
    # not sure how to refresh sidebar_base, when graph_base is re-rendered.

    from_node = response.POST.get('start')
    to_node = response.POST.get('end')

    response.session['start'] = from_node
    response.session['end'] = to_node