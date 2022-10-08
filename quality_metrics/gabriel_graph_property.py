import numpy as np


# minimize
# エッジを直径とした円の内部にノードを含まないようにしたい。
# エッジを直径とした円の内部にある点について、円の中心に近いほどでかいエネルギーを持つ
def gabriel_graph_property(nx_graph, pos):
    s = 0
    for e in nx_graph.edges:
        e1, e2 = e
        x1 = np.array(pos[e1])
        x2 = np.array(pos[e2])
        rij = np.linalg.norm(x1 - x2) / 2
        cij = (np.array(x1) + np.array(x2)) / 2
        for node_id in nx_graph.nodes:
            if e1 == node_id or e2 == node_id:
                continue
            s += max(0, rij -
                     np.linalg.norm(np.array(pos[node_id] - cij))) ** 2

    return s
