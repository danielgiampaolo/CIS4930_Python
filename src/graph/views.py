from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"]) # now only GET & POST allowed
def index(request):

    # get vertices (or anything) from session info here
    # then fill "sidebar_context.html"
    
    test_fill_data = {
        "nodes": request.session.get('nodes', []),  # need to save elsewhere
        "edges": request.session.get('edges', []),
        "type": "Undirected",
    }

    # this way of accessing a session variable
    # gives us a default value if it doesnt exist
    # var = req.session.get('something', default) default being any value

    # delete -> del req.session['something']

    graph_data = {
        "bottom": "text",
        "nodes": ["test1", "test2"],
        "edges": ["a to b"],
        "type": "Undirected",
    }



    # TODO:
    #  1. See if its possible to modify the things above like a text box
    #  2. Add button for update, & get information from "text box" ^^
    #  3. Add a background color to sidebar, a nice soft color :)
    #  4. Start looking into how to access sessions

    return render(request, 'index.html', graph_data)