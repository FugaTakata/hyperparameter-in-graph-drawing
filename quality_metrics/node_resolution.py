import numpy as np


direction = 'maximize'


def quality(pos, distances):
    sorted_node_ids = sorted([node_id for node_id in pos])
    target_resolution = 1 / np.sqrt(len(sorted_node_ids))
    dmax = -float('inf')
    dmin = float('inf')

    for i, sid in enumerate(sorted_node_ids):
        for tid in sorted_node_ids[i:]:
            if dmax < distances[sid][tid]:
                dmax = distances[sid][tid]
            if sid == tid:
                continue

            if distances[sid][tid] < dmin:
                dmin = distances[sid][tid]

    q = min(1, dmin / (target_resolution * dmax))

    return q
