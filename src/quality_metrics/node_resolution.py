# Third Party Library
import numpy as np
from scipy.spatial.distance import pdist

direction = "maximize"


def quality(pos):
    dx = pdist(list(pos.values()))
    target_resolution = 1 / np.sqrt(len(pos))
    dmax = dx.max()
    dmin = dx.min()
    q = min(1, dmin / (target_resolution * dmax))

    return q
