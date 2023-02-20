# Standard Library
from itertools import combinations

# Third Party Library
import networkx as nx
import numpy as np
from scipy.spatial.distance import pdist

direction = "minimize"


def quality(nx_graph, pos, all_shortest_paths, K=1, L=1):
    if all_shortest_paths is None:
        all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))
    dx = pdist([pos[i] for i in nx_graph.nodes])
    d = np.array(
        [all_shortest_paths[i][j] for i, j in combinations(nx_graph.nodes, 2)]
    )

    s = np.sum(((K / d**2) * (dx - L * d) ** 2) / 2)

    return s
