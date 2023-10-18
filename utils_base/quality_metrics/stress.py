# Third Party Library
from egraph import stress

direction = "minimize"


def measure(eg_drawing, eg_distance_matrix):
    return stress(eg_drawing, eg_distance_matrix)
