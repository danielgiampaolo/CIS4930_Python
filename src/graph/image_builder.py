import networkx as nx
import io
import matplotlib
import matplotlib.pyplot as plt

def build_image(nodes, edges, start, end):
    try:
        network_graph = nx.Graph()
        matplotlib.use('Agg')

        for [node1, node2] in edges:
            network_graph.add_edge(node1, node2)

        # node_adjacencies = []
        # node_text = []
        # node_link_qty = []

        # for node, adjacencies in enumerate(network_graph.adjacency()):
        #     node_adjacencies.append(len(adjacencies[1]))
        #     node_text.append('# of connections: ' + str(len(adjacencies[1])))
        #     node_link_qty.append([adjacencies[0], len(adjacencies[1])])

        pos = nx.spring_layout(network_graph, k=0.1, iterations=50)
        nx.draw(network_graph,pos, with_labels=True)

        #start = 'node 1'
        #end = 'node 34'
        if start in nodes and end in nodes:
            try:
                path = nx.shortest_path(network_graph,source=start,target=end)
                print(path)
                path_edges = set(zip(path,path[1:]))    
                nx.draw_networkx_nodes(network_graph,pos,nodelist=path,node_color='g')
                nx.draw_networkx_edges(network_graph,pos,edgelist=path_edges,edge_color='g',width=10)
                #request.session['path_error'] = "Path Drawn: " + start + " to " + end
            except nx.NetworkXException as e:
                print('networkxexpception:', e)
                #request.session['path_error'] = "No path exists between " + start + " and " + end
        plt.axis('equal')

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
