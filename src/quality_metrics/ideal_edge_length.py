# Third Party Library
import numpy as np

# First Party Library
from utils import graph

direction = "minimize"


def quality(nx_graph, pos, shortest_path_length):
    if shortest_path_length is None:
        shortest_path_length = graph.get_shortest_path_length(
            nx_graph=nx_graph
        )
    s = 0
    for source, target in nx_graph.edges:
        lij = shortest_path_length[source][target]
        dist = np.linalg.norm(np.array(pos[source]) - np.array(pos[target]))
        s += ((dist - lij) / lij) ** 2

    return s
