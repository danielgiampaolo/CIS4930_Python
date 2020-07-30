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
    nodes = set()
    for row in nodeList:
        edges.append([row['Node'], row['Neighbor']])
        nodes.add(row['Node'])
        nodes.add(row['Neighbor'])

    return (list(nodes), edges)
