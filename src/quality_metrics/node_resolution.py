# Third Party Library
from egraph import node_resolution

direction = "maximize"


def quality(eg_graph, eg_drawing):
    return node_resolution(eg_graph, eg_drawing)
