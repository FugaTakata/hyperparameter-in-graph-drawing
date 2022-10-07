import numpy as np
import math


# maximize
# すべてのノードについて、あるノードに入射するエッジ同士のなす角度が最も小さいもの
def angular_resolution(nx_graph, pos):
    edges = {}
    for s, t in nx_graph.edges:
        if s not in edges:
            edges[s] = {}
        if t not in edges:
            edges[t] = {}
        edges[s][t] = True
        edges[t][s] = True

    ls = 0
    for s in pos:
        if s not in edges:
            continue
        l = 2 * math.pi
        ts = sorted([node_id for node_id in edges[s]])
        for i, t1 in enumerate(ts):
            e1 = np.array(pos[s]) - np.array(pos[t1])
            for t2 in ts[i + 1:]:
                if t1 == t2 or s == t1 or s == t2:
                    continue
                e2 = np.array(pos[s]) - np.array(pos[t2])
                angle = math.acos(
                    np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))
                if angle < l:
                    l = angle
        ls += l
    return ls
