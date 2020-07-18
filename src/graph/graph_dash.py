import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
from colour import Color
import pandas as pd
import plotly.graph_objs as go

from django_plotly_dash import DjangoDash

app = DjangoDash("dash_graph")
app.title = "NetView Graph"


edges = pd.read_csv('../test/test_nodes.csv')

nodes = dict()
node_set = set()

for index in range(0, len(edges)):
  from_node = nodes.get(edges['Node'][index], [])
  from_node.append(edges['Neighbor'][index])
  nodes[edges['Node'][index]] = from_node

  node_set.add(edges['Node'][index])
  node_set.add(edges['Neighbor'][index])

G = nx.from_pandas_edgelist(edges, 'Node', 'Neighbor', edge_attr=['Node', 'Neighbor', 'Link'], create_using=nx.DiGraph())

nx.set_node_attributes(G, nodes, 'connecting_to')

pos = nx.drawing.layout.spring_layout(G, k=0.15, iterations=20)
# pos = nx.drawing.layout.shell_layout(G, [list(node_set)])

for node in G.nodes:
  G.nodes[node]['pos'] = list(pos[node])


traceRecode = []
node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                        hoverinfo="text", marker={'size': 50, 'color': 'LightSkyBlue'})

index = 0
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    hovertext = "Connected to (fwd): " + str(','.join(G.nodes[node]['connecting_to']))
    text = node
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['hovertext'] += tuple([hovertext])
    node_trace['text'] += tuple([text])
    index = index + 1

traceRecode.append(node_trace)

colors = list(Color('lightcoral').range_to(Color('darkred'), len(G.edges())))
colors = ['rgb' + str(x.rgb) for x in colors]

index = 0
for edge in G.edges:
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    weight = 1
    # weight = float(G.edges[edge]['Link']) / max(edges['Link']) * 10
    trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                       mode='lines',
                       line={'width': weight},
                       marker=dict(color=colors[index]),
                       line_shape='spline',
                       opacity=1)
    traceRecode.append(trace)
    index = index + 1

figure = {
    "data": traceRecode,
    "layout": go.Layout(title='Interactive Transaction Visualization', showlegend=False, hovermode='closest',
                        margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                        xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                        yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                        height=600,
                        clickmode='event+select',
                        annotations=[
                            dict(
                                ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                showarrow=True,
                                arrowhead=3,
                                arrowsize=4,
                                arrowwidth=1,
                                opacity=1
                            ) for edge in G.edges]
                        )}


app.layout = html.Div(children=[
  html.H1(children="Hello Dash"),

  html.Div(children='''

  '''),

  dcc.Graph(
    id='example-graph',
    figure=figure
  )
])
