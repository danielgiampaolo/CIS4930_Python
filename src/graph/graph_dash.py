import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
from colour import Color
import pandas as pd
import plotly.graph_objs as go

from django_plotly_dash import DjangoDash

# Initialize Dash App
app = DjangoDash("dash_graph")
app.title = "NetView Graph"

# App Layout (their version of HTML)
app.layout = html.Div(id="graph-wrapper", children=[
  html.Span(id="callback-input", children=[])
])

# Callback that sets up the graph
# It uses a random span as the input, and outputs the figure into #graph-wrapper
# NOTE: "session_state" is set as request.session['django_plotly_dash'] in views.py
@app.expanded_callback(
    dash.dependencies.Output("graph-wrapper", "children"),
    [dash.dependencies.Input('callback-input', 'children')]
)
def update_graph_callback(_, session_state=None, **kwargs):
    if session_state is None:
        raise NotImplementedError("Cannot handle a missing session state")

    # grab session data (see structure.md)
    edges = session_state.get('edges', [])
    bold_edges = session_state.get('bold_edges', [])
    nodes = session_state.get('nodes', [])
    start = session_state.get('start')
    end = session_state.get('end')
    # print("start: " + start)
    # print("end: " + end)
    # misc
    max_weight = 1


    nodes_dict = dict()
    node_set = set()

    error = None

    # create networkx graph
    G = nx.Graph()


    # add edges to graph
    # NOTE: if we allow float-based weights, change below
    for [node1, node2, weight] in edges:
        G.add_edge(node1, node2, weight=int(weight))
        max_weight = max(int(weight), max_weight)
        nodes_dict[node1] = "No data"

    # setup nodes (remove later)
    # for edge in edges:
    #     from_node = nodes_dict.get(edge[0], [])
    #     from_node.append(edge[1])
    #     nodes_dict[edge[0]] = from_node

    #     node_set.add(edge[0])
    #     node_set.add(edge[1])

    # setup nodes
    for [node_name, *lines] in nodes:
        nodes_dict[node_name] = lines

    # set node attributes based on nodes_dict
    nx.set_node_attributes(G, nodes_dict, 'description')

    #Build path
    if start != '' and end != '':
        try:
            path = nx.shortest_path(G,source=start,target=end)
            path_edges = set(zip(path,path[1:]))
            a_path = []
            for p_edge in path_edges:
                # print(p_edge[0])
                a_path.append([p_edge[0],p_edge[1]])
            #print(a_path)
            bold_edges = a_path
        except nx.exception.NetworkXNoPath:
            error = "Could not find path between %s and %s" % (start, end)

    # set layout for graph
    pos = nx.drawing.layout.spring_layout(G, k=0.15, iterations=20)

    # enable below for shell based layout (circular)
    # pos = nx.drawing.layout.shell_layout(G, [list(node_set)])

    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    traceRecode = []
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 50, 'color': 'LightSkyBlue'})

    ######
    #print(G.nodes())
    ######

    # add nodes into trace
    index = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        hovertext = str('<br />'.join([
            "Name: %s" % node,
            *G.nodes[node].get('description', 'unknown')
        ]))
        text = node
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1

    traceRecode.append(node_trace)


    colors = list(Color('lightcoral').range_to(Color('darkred'), max(1, len(G.edges()))))
    colors = ['rgb' + str(x.rgb) for x in colors]

    # add edges into trace
    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']

        weight = 1

        node_list = list(edge)
        if node_list in bold_edges or node_list[::-1] in bold_edges:
            weight = 5
            marker_color = dict(color='green')
        else:
            weight = 2.5
            marker_color = dict(color=colors[index])
        # if you want thickness based on weight, enable commented line below
        # weight = float(G.edges[edge]['weight']) / max_weight * 10

        trace = go.Scatter(
            x=tuple([x0, x1, None]),
            y=tuple([y0, y1, None]),
            mode='lines',
            line={ 'width': weight },
            marker=marker_color,
            line_shape='spline',
            opacity=1
        )

        traceRecode.append(trace)

        index = index + 1

    figure = {
        "data": traceRecode,
        "layout": go.Layout(
            title='Network Graph Visualization',
            showlegend=False,
            hovermode='closest',
            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            height=600,
            clickmode='event+select',
            annotations=[
                dict(
                    text=G.edges[edge]['weight'],
                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2,
                    axref='x',
                    ayref='y',
                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4,
                    xref='x',
                    yref='y',
                    showarrow=False,
                    arrowhead=3,
                    arrowsize=4,
                    arrowwidth=1,
                    opacity=0.8
                ) for edge in G.edges
            ]
        )
    }

    return [
        dcc.Graph(
            id='graph',
            figure=figure
        ),
        html.Div(id="boomer", style={'color': 'red', 'fontFamily': 'arial', 'marginTop': '16px'}, children=[error]),
        html.Span(id="callback-input", children=[])
    ]

