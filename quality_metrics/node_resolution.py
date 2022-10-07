import numpy as np


# maximize
# ノードのユークリッド距離として定義される。stressなどと一致させるために正規化するらしいけど多分必要ない
def node_resolution(pos):
    nodes = sorted([node_id for node_id in pos])
    r = float('inf')
    ds = []
    for i, sid in enumerate(nodes):
        for tid in nodes[i + 1:]:
            dist = np.linalg.norm(np.array(pos[sid]) - np.array(pos[tid]))
            ds.append(dist)
            if dist < r:
                r = dist
    return r
