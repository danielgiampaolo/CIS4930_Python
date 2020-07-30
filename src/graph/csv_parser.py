import csv

"""
read(data: string)
"""
def read(data):
    nodeList = csv.DictReader(data.split('\n'), delimiter=',')

    """
    Each row is expected to have the following:
        - Node
        - Link
        - Neighbor
    """

    edges = []
    nodes_set = set()
    for row in nodeList:
        edges.append([row['Node'], row['Neighbor'], row['Link']])
        nodes_set.add(row['Node'])
        nodes_set.add(row['Neighbor'])

    # TODO: remove/update later
    nodes = []
    i = 1
    for node in list(nodes_set):
        data = [node]

        if i % 2 == 0:
            data.append('line1')
            data.append('line2')

        nodes.append(data)
        i = i + 1

    return (nodes, edges)
