# Standard Library
from itertools import combinations

# Third Party Library
import numpy as np
from scipy.spatial.distance import pdist

# First Party Library
from utils import graph

direction = "minimize"


def quality(nx_graph, pos, shortest_path_length, K=1, L=1):
    if shortest_path_length is None:
        shortest_path_length = graph.get_shortest_path_length(
            nx_graph=nx_graph
        )
    dx = pdist([pos[i] for i in nx_graph.nodes])
    d = np.array(
        [
            shortest_path_length[i][j]
            for i, j in combinations(nx_graph.nodes, 2)
        ]
    )

    s = np.sum(((K / d**2) * (dx - L * d) ** 2) / 2)

    return s
