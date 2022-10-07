from utils import gravity_center
import numpy as np


# maximize
def aspect_ratio(pos):
    gravity_centered_pos = []
    gx, gy = gravity_center(pos)
    for node_id in pos:
        x, y = pos[node_id]
        gravity_centered_pos.append([x - gx, y - gy])
    gravity_centered_pos = np.array(gravity_centered_pos)
    _, s, _ = np.linalg.svd(gravity_centered_pos, full_matrices=True)
    a = max(s)
    b = min(s)

    return b / a
