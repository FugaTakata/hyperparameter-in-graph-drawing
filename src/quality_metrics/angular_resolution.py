# Third Party Library
from egraph import angular_resolution

direction = "maximize"


def quality(eg_graph, eg_drawing):
    return -angular_resolution(eg_graph, eg_drawing)
