# Third Party Library
from egraph import ideal_edge_lengths

direction = "minimize"


def measure(eg_graph, eg_drawing, eg_distance_matrix):
    return ideal_edge_lengths(eg_graph, eg_drawing, eg_distance_matrix)
