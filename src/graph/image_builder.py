import networkx as nx
import io
import matplotlib
import matplotlib.pyplot as plt

def build_image(nodes, edges):
    try:
        network_graph = nx.Graph()
        matplotlib.use('Agg')

        for [node1, node2,wght] in edges:
            network_graph.add_edge(node1, node2,weight=wght)

        # node_adjacencies = []
        # node_text = []
        # node_link_qty = []

        # for node, adjacencies in enumerate(network_graph.adjacency()):
        #     node_adjacencies.append(len(adjacencies[1]))
        #     node_text.append('# of connections: ' + str(len(adjacencies[1])))
        #     node_link_qty.append([adjacencies[0], len(adjacencies[1])])

        labels = nx.get_edge_attributes(network_graph, 'weight')
        options = {'label_pos': 0.5, 'width':2, 'font_size':15}
        pos = nx.spring_layout(network_graph, k=0.3, iterations=20)
        nx.draw(network_graph,pos, with_labels=True,**options)



        nx.draw_networkx_edge_labels(network_graph, pos, edge_labels=labels, **options)

        figure = plt.gcf()
        figure.set_size_inches(16, 9)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.clf()
        buf.seek(0)

        return (0, buf)
    except nx.NetworkXException as e:
        print('networkxexpception:', e)
        return (1, "NetworkX Exception")
    except Exception as e:
        print(e)
        return (1, "Something went wrong")
