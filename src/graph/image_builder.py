import networkx as nx
import io
import matplotlib
import matplotlib.pyplot as plt

def build_image(nodes, edges):
    try:
        network_graph = nx.Graph()
        matplotlib.use('Agg')

        for [node1, node2] in edges:
            print('edge betweent %s and %s' % (node1, node2))
            network_graph.add_edge(node1, node2)

        # node_adjacencies = []
        # node_text = []
        # node_link_qty = []

        # for node, adjacencies in enumerate(network_graph.adjacency()):
        #     node_adjacencies.append(len(adjacencies[1]))
        #     node_text.append('# of connections: ' + str(len(adjacencies[1])))
        #     node_link_qty.append([adjacencies[0], len(adjacencies[1])])

        nx.spring_layout(network_graph, k=0.15, iterations=20)
        nx.draw(network_graph, with_labels=True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        return (0, buf)
    except nx.NetworkXException as e:
        print('networkxexpception:', e)
        return (1, "NetworkX Exception")
    except Exception as e:
        print(e)
        return (1, "Something went wrong")
