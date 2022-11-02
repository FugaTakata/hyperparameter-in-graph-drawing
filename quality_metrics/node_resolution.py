import numpy as np
from math import sqrt


direction = 'minimize'


# minimize
# ノードのユークリッド距離として定義される。stressなどと一致させるために正規化するらしいけど多分必要ない
def quality(pos):
    nodes = sorted([node_id for node_id in pos])
    target_resolution = 1 / sqrt(len(nodes))
    dmax = -float('inf')
    dmin = float('inf')
    dist_map = {}

    for i, sid in enumerate(nodes):
        dist_map[sid] = {}
        for tid in nodes[i:]:
            dist_map[sid][tid] = np.linalg.norm(
                np.array(pos[sid]) - np.array(pos[tid]))
            if dmax < dist_map[sid][tid]:
                dmax = dist_map[sid][tid]
            if sid == tid:
                continue

            if dist_map[sid][tid] < dmin:
                dmin = dist_map[sid][tid]

    vr = 1 - (dmin / (target_resolution * dmax))

    return vr
