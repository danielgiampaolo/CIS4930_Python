from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

# third parameter is a map, key = name, value = information
def index(request):

    # get vertices (or anything) from session info here
    # then fill "sidebar_context.html"

    graph_data = {
        "bottom": "text",
        "nodes": ["a", "b"],
        "edges": ["a to b"],
        "type": "Undirected",
    }

    return render(request, 'index.html', graph_data)