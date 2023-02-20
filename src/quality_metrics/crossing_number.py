# First Party Library
from utils import edge_crossing_finder

direction = "minimize"


def quality(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder(nx_graph, pos)
    s = len(edge_crossing)

    return s
