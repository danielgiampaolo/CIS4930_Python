from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from .forms import nodeInput


@require_http_methods(["GET", "POST"]) # only GET & POST allowed
def index(request):

    # get vertices (or anything) from session info here
    graph_data = {
        "nodes": request.session.get('nodes', ['test1', 'test2']),  # need to save in POST
        "edges": request.session.get('edges', []),
        "type": request.session.get('type', 'Undirected'),
    }

    if request.method == "POST":
        return handle_graph_post(request)

    # else, handle GET
    return render(request, 'index.html', graph_data)


def handle_graph_post(response):
    form = nodeInput(response.POST)
    print("printing POST")
    print(response.POST)

    graph_data = {
        "nodes": response.session.get('nodes', ['test1', 'test2']),  # need to save in POST
        "edges": response.session.get('edges', []),
        "type": response.session.get('type', 'Undirected'),
    }

    print("verifying form")

    if form.is_valid():
        print("printing form")
        print(form)
        print("printing cleaned data")
        print(form.cleaned_data)

        return render(response, 'index.html', graph_data)
        #request.session['nodes']
    else:
        return render(response, 'index.html', graph_data)