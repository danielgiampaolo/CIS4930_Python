from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .forms import nodeInput
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from . import csv_parser, image_builder, graph_lib
import re

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
        "start": request.session.get('start', ''),
        "end": request.session.get('end', '')
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
    print(response.POST.get('start'))
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

    node_names = [node_info[0] for node_info in currentNodes]

    # getting all updated nodes first
    for field, node in response.POST.items():
        nodeField = re.search(r"^node(\d+)$", field)
        edgeField = re.search(r"^edge(\d+)(\w+)$", field)

        if nodeField:
            currentNode_num = int(nodeField.group(1))
            current_node_val = response.POST.get("node%d" % currentNode_num)

            old_node = currentNodes[currentNode_num - 1]

            # added check to ensure the name is new
            if node not in node_names or (current_node_val == node_names[currentNode_num - 1]):
                # [([node] + old_node[1:])] = get new name, keep old description
                updatedNodes = updatedNodes + [([node] + old_node[1:])]
            else:
                updatedNodes = updatedNodes + [old_node]
                messages.add_message(response, messages.ERROR, "Name conflict for %s. No changes made." % old_node[0], extra_tags="node_error")

        elif edgeField:
            number = int(edgeField.group(1))
            f_type = edgeField.group(2)

            if "from" in f_type:
                # only work on "from" fields. if this exists, others are guaranteed
                to_node = response.POST.get("edge%dto" % number).strip()
                new_weight = response.POST.get("edge%dweight" % number).strip()

                old_weight = currentEdges[number - 1][2]

                if new_weight != "" and new_weight.isnumeric():
                    new_weight = int(new_weight)

                    if new_weight != old_weight:
                        old_weight = new_weight

                # please refer to me as the king of unreadable one-liners
                updatedEdges = updatedEdges + [[new if new in node_names else old for (new, old) in zip((node, to_node), currentEdges[number - 1][:-1])] + [old_weight]]

                if not updatedEdges[-1][0] == node:
                    messages.add_message(response, messages.ERROR, 'Node "%s" does not exist.' % node, extra_tags="edge_error")

                if not updatedEdges[-1][1] == to_node:
                    messages.add_message(response, messages.ERROR, 'Node "%s" does not exist.' % to_node, extra_tags="edge_error")

    # Not assuming I will see all the node fields before the edges.
    # Maybe I could.
    # Doing this to compare the new edge names to all the new node names.
    # With all updated nodes,
    # I will check that the changes in edges are limited to existing nodes.

    # renaming edges from changed nodes
    for old_node_info, new_node_info in zip(currentNodes, updatedNodes):

        old_name = old_node_info[0]
        new_name = new_node_info[0] # if info[1] is equal to above's, it might not exist

        # find mismatched names
        if not old_name == new_name:
            # rename edge end points
            updatedEdges = [[new_name if f == old_name else f, new_name if t == old_name else t, w] for (f, t, w) in updatedEdges]

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
        messages.add_message(response, messages.INFO, "Node added: %s" % newNode, extra_tags="node_info")
    else:
        messages.add_message(response, messages.ERROR, "Node not added, node already exists" % newNode, extra_tags="node_error")

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

    messages.add_message(response, messages.INFO, "Node deleted: %s" % nodeDeleted, extra_tags="node_info")


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


def clearAll(response):
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

            request.session['edges'] = edges
            request.session['nodes'] = nodes
            request.session['num_nodes'] = len(nodes)
            request.session['num_edges'] = len(edges)
            print("Parsed correctly :)")
            print(list(edges))
            print(list(nodes))
        except csv_parser.CsvParsingException:
            messages.add_message(request, messages.ERROR, 'An error occurred while parsing the csv file.', extra_tags="edge_error")
        except Exception as e:
            print(e)
            return JsonResponse({
                'message': 'Something went wrong >:('
            })

    elif file_content == 'nodes':
        # Code done by Enzo, committed by Adrian, Lines: 15
        raw_bytes = uploaded.read()
        raw_data = raw_bytes.decode("utf-8")
        try:
            descs = csv_parser.read_desc(raw_data)
        except Exception as e:
            print(e)
            return JsonResponse({
                'message': 'Something went wrong >:('
            })
        # Bit where the new node desc is saved. If node doesnt exist we ignore the description

        currentNodes = request.session.get('nodes', [])
        for node, *desc in descs: # [[name, desc1, desc2], [...]]
            for x in range(0,len(currentNodes)):
                if currentNodes[x][0].strip() == node.strip():
                    currentNodes[x] = [currentNodes[x][0]] + desc
        request.session['nodes'] = currentNodes

    return


def csv_download(request):
    # CSV Headers: Node, Link, Neighbor
    headers = ('Node', 'Link', 'Neighbor')

    result = [','.join(headers)]
    edges = request.session.get('edges', [])

    for edge in edges:
        # as you can see, the link isn't carried over.
        # someone should fix that.
        result.append(','.join((edge[0], edge[2], edge[1])))

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
    weight = request.POST.get('newedgeweight').strip()

    if from_node and to_node:
        try:
            graph_lib.c_add_edge(request.session, from_node, to_node, weight)
            messages.add_message(request, messages.INFO, 'Edge added: ' + from_node + ' to ' + to_node, extra_tags="edge_info")
        except graph_lib.EdgeExistsException:
            messages.add_message(request, messages.ERROR, 'That edge exists already!', extra_tags="edge_error")
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'An unknown error occurred.', extra_tags="edge_error")
            print("something wrong :(", e)

def add_path(response):
    # if node has no connection to destination node, graph will break.
    # caught in image_builder, but makes it a refresh late on page...
    # not sure how to refresh sidebar_base, when graph_base is re-rendered.

    from_node = response.POST.get('start')
    to_node = response.POST.get('end')

    response.session['start'] = from_node
    response.session['end'] = to_node