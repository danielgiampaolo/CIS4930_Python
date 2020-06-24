from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

def index(request):
    return render(request, 'graph/index.html')

def node_list(request):
    return render(request, 'graph/node_list.html')