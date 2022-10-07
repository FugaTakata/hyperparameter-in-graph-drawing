import numpy as np
import networkx as nx


# minimize
def ideal_edge_length(nx_graph, pos):
    s = 0
    for source, target, data in nx_graph.edges(data=True):
        weight = data['weight'] if 'weight' in data and data['weight'] != 0 else 1
        shortest_path_length = nx.shortest_path_length(
            nx_graph, source, target, data['weight'] if 'weight' in data else None)

        lij = shortest_path_length * weight
        dist = np.linalg.norm(np.array(pos[source]) - np.array(pos[target]))
        s += ((dist - lij) / lij) ** 2

    return s
