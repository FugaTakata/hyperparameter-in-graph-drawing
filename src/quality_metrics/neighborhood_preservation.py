# Third Party Library
from egraph import neighborhood_preservation

direction = "maximize"


def quality(eg_graph, eg_drawing):
    return neighborhood_preservation(eg_graph, eg_drawing)
