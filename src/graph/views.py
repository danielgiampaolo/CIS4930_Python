from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

# third parameter is a map, key = name, value = information
def index(request):

    # get vertices (or anything) from session info here
    # then fill "sidebar_context.html"

    graph_data = {
        "bottom": "text",
        "nodes": ["test1", "test2"],
        "edges": [["a", "b"], ["b" , "a"]],
        "type": "Undirected",
    }

    # TODO:
    #  1. See if its possible to modify the things above like a text box
    #  2. Add button for update, & get information from "text box" ^^
    #  3. Add a background color to sidebar, a nice soft color :)
    #  4. Start looking into how to access sessions

    return render(request, 'index.html', graph_data)