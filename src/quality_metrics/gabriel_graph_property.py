# Third Party Library
from egraph import gabriel_graph_property

direction = "maximize"


def quality(eg_graph, eg_drawing):
    return gabriel_graph_property(eg_graph, eg_drawing)
