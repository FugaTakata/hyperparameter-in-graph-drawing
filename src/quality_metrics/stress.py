# Third Party Library
from egraph import all_sources_bfs, stress

# First Party Library
from config import const

direction = "maximize"


def quality(eg_graph, eg_drawing, eg_distance_matrix=None):
    if eg_distance_matrix is None:
        eg_distance_matrix = all_sources_bfs(eg_graph, const.EDGE_WEIGHT)
    return -stress(eg_drawing, eg_distance_matrix)
