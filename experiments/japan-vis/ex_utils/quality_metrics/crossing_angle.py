# Third Party Library
from egraph import crossing_angle

direction = "minimize"


def measure(eg_graph, eg_drawing, eg_crossings, crossing_number):
    mean_crossing_angle = (
        crossing_angle(eg_graph, eg_drawing, eg_crossings) / crossing_number
    )
    return -mean_crossing_angle
