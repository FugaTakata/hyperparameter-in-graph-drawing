# Third Party Library
from egraph import aspect_ratio

direction = "maximize"


def measure(eg_drawing):
    return aspect_ratio(eg_drawing)
