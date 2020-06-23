from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .csv_parser import read

def index(request):
    return HttpResponse("Hello, world. You're at the graph index.")

def sample_form(request):
    return render(request, 'index.html', {})

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

    resp = read(raw_data)

    # set session somewhere here?

    return JsonResponse({
        'input': raw_data,
        'output': resp
    })
