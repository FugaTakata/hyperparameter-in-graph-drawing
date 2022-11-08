import numpy as np
import networkx as nx


direction = 'minimize'


def quality(nx_graph, pos, all_shortest_paths):
    if all_shortest_paths is None:
        all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))
    s = 0
    for source, target in nx_graph.edges:
        lij = all_shortest_paths[source][target]
        dist = np.linalg.norm(np.array(pos[source]) - np.array(pos[target]))
        s += ((dist - lij) / lij) ** 2

    return s
