import networkx as nx
import io
import matplotlib
import matplotlib.pyplot as plt
import csv
import json
import uuid

"""
read(data: string)
"""
def read(data):
    try:
        parsed_nodes = []
        parsed_edges = []
        network_graph = nx.Graph()
        matplotlib.use('Agg')


        nodes = csv.DictReader(data.split('\n'), delimiter=',')
        for node in nodes:
            network_graph.add_edge(node['Node'], node['Neighbor'])

        node_adjacencies = []
        node_text = []
        node_link_qty = []

        for node, adjacencies in enumerate(network_graph.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append('# of connections: ' + str(len(adjacencies[1])))
            node_link_qty.append([adjacencies[0], len(adjacencies[1])])

        nx.spring_layout(network_graph, k=0.15, iterations=20)
        nx.draw(network_graph, with_labels=True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        resp = {'status': 'k'}

        return buf
    except nx.NetworkXException as e:
        print('networkxexpception:', e)
        return "NetworkX Exception"
    except Exception as e:
        print(e)
        return "Something went wrong"
