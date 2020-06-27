from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from . import csv_parser, image_builder
import json

def index(request):
    return HttpResponse("Hello, world. You're at the graph index.")

def sample_form(request):
    return render(request, 'index.html', {
        'nodes': request.session.get('nodes', []),
        'edges': request.session.get('edges', [])
    })

def clear_session(request):
    request.session.flush()

    return HttpResponseRedirect('/test_form')

def csv_upload(request):
    if request.method != 'POST':
        return HttpResponse("You weren't supposed to do that. This is a POST endpoint.")

    # request is guaranteed to be POST
    uploaded = request.FILES.get('csv-file')

    if uploaded == None:
        return JsonResponse({
            'message': 'No file found.'
        })

    if uploaded.content_type not in ['text/csv', 'application/vnd.ms-excel']:
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

    # return JsonResponse({
    #     'message': 'yeet (no errors so far)',
    #     'num_nodes': request.session['num_nodes'],
    #     'num_edges': request.session['num_edges'],
    #     'nodes': request.session['nodes'],
    #     'edges': request.session['edges'],
    # })
    return HttpResponseRedirect('/test_form')

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

def remove_node(request):
    if request.method != "POST":
        return JsonResponse({
            "message": "This is not a POST request."
        })

    remove_nodes = request.POST.getlist('nodes', [])
    current_nodes = request.session.get('nodes', [])
    current_edges = request.session.get('edges', [])

    request.session['nodes'] = list(filter(lambda x: x not in remove_nodes, current_nodes))
    request.session['edges'] = list(filter(lambda x: x[0] not in remove_nodes and x[1] not in remove_nodes, current_edges))
    # you just got one-lined

    return HttpResponseRedirect('/test_form')

def add_edge(request):
    if request.method != "POST":
        return JsonResponse({
            "message": "This is not a POST request."
        })

    from_node = request.POST.get('edge_from')
    to_node = request.POST.get('edge_to')

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



def remove_edge(request):
    if request.method != "POST":
        return JsonResponse({
            "message": "This is not a POST request."
        })

    remove_edges = request.POST.getlist('edges', [])
    current_edges = request.session.get('edges', [])
    rm_formatted = []

    for edge in remove_edges:
        rm_formatted.append(edge.split(", "))

    request.session['edges'] = list(filter(lambda x: x not in rm_formatted, current_edges))

    new_nodes = set()
    for (x, y) in request.session['edges']:
        new_nodes.add(x)
        new_nodes.add(y)

    request.session['nodes'] = list(new_nodes)

    return HttpResponseRedirect('/test_form')

# dont do this in production (security risk)
# debug only
def view_session(request):
    result = {}
    for key, value in request.session.items():
        result[key] = (value)
        # result.append('{} => {}'.format(key, str(value)))

    return JsonResponse({'result': result})
