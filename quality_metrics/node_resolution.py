import numpy as np
from scipy.spatial.distance import pdist, squareform


direction = 'maximize'


def quality_naive(pos):
    sorted_node_ids = sorted([node_id for node_id in pos])
    target_resolution = 1 / np.sqrt(len(sorted_node_ids))
    dmax = -float('inf')
    dmin = float('inf')

    for i, sid in enumerate(sorted_node_ids):
        xs = np.array(pos[sid])
        for tid in sorted_node_ids[i:]:
            xt = np.array(pos[tid])
            dist = np.linalg.norm(xs - xt)
            if dmax < dist:
                dmax = dist
            if sid == tid:
                continue

            if dist < dmin:
                dmin = dist

    q = min(1, dmin / (target_resolution * dmax))

    return q


def quality(pos):
    dx = pdist(list(pos.values()))
    target_resolution = 1 / np.sqrt(len(pos))
    dmax = dx.max()
    dmin = dx.min()
    q = min(1, dmin / (target_resolution * dmax))
    # assert np.isclose(q, quality_naive(pos))
    return q
