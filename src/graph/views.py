from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render


# third parameter is a map, key = name, value = information
def index(request):

    # get vertices (or anything) from session info here
    # then fill "sidebar_context.html"
    if request.POST:
        print(request.POST)
        graph_data = {
            "bottom": "text",
            "nodes": ["test1", "test2"],
            "edges": [["a", "b"], ["b", "a"]],
            "type": "Undirected",
        }
        return render(request, 'index.html', graph_data)

    else:
        graph_data = {
            "bottom": "text",
            "nodes": ["test1", "test2"],
            "edges": [["a", "b"], ["b" , "a"]],
            "type": "Undirected",
        }

        # TODO:
        #  1. See if its possible to modify the things above like a text box DONE?
        #  2. Add button for update, & get information from "text box" ^^ DONE (Possible cause of labels with the for element dont delete them!)
        #  3. Add a background color to sidebar, a nice soft color :) (Choose whatever you think is good)
        #  4. Start looking into how to access sessions (GL with this i dunno)
        #  To view info sent through the post command, click any update or add button and look at the terminal running the server it should send the new info

        return render(request, 'index.html', graph_data)