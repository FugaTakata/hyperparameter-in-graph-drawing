# Third Party Library
from egraph import crossing_number

direction = "minimize"


def measure(eg_graph, eg_drawing, eg_crossings):
    return crossing_number(eg_graph, eg_drawing, eg_crossings)
