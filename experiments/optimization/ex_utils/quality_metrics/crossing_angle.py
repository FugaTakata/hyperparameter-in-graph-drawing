# Third Party Library
from egraph import crossing_angle

direction = "minimize"


def measure(eg_graph, eg_drawing, eg_crossings):
    return crossing_angle(eg_graph, eg_drawing, eg_crossings)
