from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from . import csv_parser, image_builder
import json

def index(request):
    return HttpResponse("Hello, world. You're at the graph index.")

def sample_form(request):
    return render(request, 'index.html', {})

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

    return JsonResponse({
        'message': 'yeet (no errors so far)',
        'num_nodes': request.session['num_nodes'],
        'num_edges': request.session['num_edges'],
        'nodes': request.session['nodes'],
        'edges': request.session['edges'],
    })

def graph(request):
    try:
        nodes = request.session['nodes']
        edges = request.session['edges']
    except KeyError:
        print(request.session)
        return JsonResponse({
            'message': 'whats the big idea?! (data not found in session)'
        })

    if edges == None or nodes == None:
        return JsonResponse({
            'message': 'whats the big idea?! (data is None)'
        })

    (result, image) = image_builder.build_image(nodes, edges)

    if result == 0:
        return HttpResponse(image, content_type='image/png')

    # something went wrong
    return JsonResponse({
        'message': 'something went wrong'
    })

# dont do this in production (security risk)
# debug only
def view_session(request):
    result = {}
    for key, value in request.session.items():
        result[key] = (value)
        # result.append('{} => {}'.format(key, str(value)))

    print(result)

    return JsonResponse({'result': result})
