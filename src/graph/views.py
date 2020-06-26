from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from .forms import nodeInput


@require_http_methods(["GET", "POST"]) # only GET & POST allowed
def index(request):

    # get vertices (or anything) from session info here
    graph_data = {
        "nodes": request.session.get('nodes', []),  # need to save in POST
        "edges": request.session.get('edges', []),
        "type": request.session.get('type', 'Undirected'),
        "num_nodes": request.session.get('num_nodes', 0),
        "num_edges": request.session.get('num_edges', 0),
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

    form = nodeInput(response.POST)

    print("printing POST")
    print(response.POST)

    print("verifying form")
    print(form.is_valid())

    if form.is_valid():
        if response.POST.get("update"):
            pass
        elif response.POST.get("addNode"):
            print("addNode button pressed")
            print("adding node...")

            # book keeping
            response.session['num_nodes'] = num_nodes + 1

            # the new node is...
            node_name = "node" + str(num_nodes + 1)

            # since we are not rendering the "from" on html
            # updating the context is also necessary
            # I dont know why I am using forms anymore
            # spagetti, spagetto, [redacted]

            cur_nodes = cur_nodes + [form.cleaned_data['newNode']]

            response.session['nodes'] = cur_nodes

            # this would be better if we rendered the form like
            # {{ form }}, less unnecessary bookkeeping


            # create node field
            form.addNode(node_name, form.cleaned_data['newNode'])

        elif response.POST.get("addEdge"):

            #increase num of edges
            response.session['num_edges'] = num_edges + 1

            #set naming convention unsure if this is correct
            edge_vert1 = "edge" + str(num_edges*2 + 1) + "from"
            edge_vert2 = "edge" + str(num_edges*2 + 2) +"to"

            #Updated session of nodes
            cur_edges = cur_edges + [[response.POST.get("newedgefrom") ,response.POST.get("newedgeto")]]

            response.session['edges'] = cur_edges

            #Add to form looks like it worked fine
            form.addEdge(edge_vert1, form.cleaned_data['newedgefrom'], edge_vert2, form.cleaned_data['newedgeto'])

        elif response.POST.get("deleteNode"):
            response.session['num_nodes'] = num_nodes - 1

            nodeDeleted  = response.POST.get("deleteNode")[-1]

            node_name = "node"+nodeDeleted

            del cur_nodes[int(nodeDeleted)-1]

            response.session['nodes'] = cur_nodes

            form.delNode(node_name)

        elif response.POST.get("deleteEdge"):
            response.session['num_edges'] = num_edges - 1

            edgeDeleted = response.POST.get("deleteEdge")[-1]

            edge_vert1 = "edge" + str(int(edgeDeleted)*2) + "from"
            edge_vert2 = "edge" + str(int(edgeDeleted)*2 +1) + "to"

            del cur_edges[int(edgeDeleted) - 1]

            response.session['edges'] = cur_edges

            form.delEdge(edge_vert1,edge_vert2)

        #print("printing form")
        #print(form)
        print("printing form fields")
        print(form.fields)
        print("printing cleaned data")
        print(form.cleaned_data)

        graph_data = {
            "nodes": response.session.get('nodes', []),  # save later
            "edges": response.session.get('edges', []),
            "type": response.session.get('type', 'Undirected'),
            "num_nodes": num_nodes,
            "num_edges": num_edges,
        }


        return render(response, 'index.html', graph_data)

    else:
        graph_data = {
            "nodes": response.session.get('nodes', []),  # save later
            "edges": response.session.get('edges', []),
            "type": response.session.get('type', 'Undirected'),
            "num_nodes": num_nodes,
            "num_edges": num_edges,
        }
        return render(response, 'index.html', graph_data)

def get_post_data(request):
    num_nodes = request.session.get('num_nodes', 0)
    num_edges = request.session.get('num_edges', 0)

    return None