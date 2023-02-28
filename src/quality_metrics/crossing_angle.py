# Third Party Library
from egraph import crossing_angle, crossing_edges

direction = "minimize"


def quality(eg_graph, eg_drawing, eg_crossings=None):
    if eg_crossings is None:
        eg_crossings = crossing_edges(eg_graph, eg_drawing)
    return crossing_angle(eg_graph, eg_drawing, eg_crossings)
