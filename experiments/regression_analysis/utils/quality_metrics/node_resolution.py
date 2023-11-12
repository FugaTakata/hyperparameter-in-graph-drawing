# Third Party Library
from egraph import node_resolution

direction = "minimize"


def measure(eg_drawing):
    return node_resolution(eg_drawing)
