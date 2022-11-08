import networkx as nx
import numpy as np


direction = 'maximize'


# すべてのノードについて、あるノードに入射するエッジ同士のなす角度が最も小さいものをもとに評価
def quality(nx_graph, pos):
    sorted_node_ids = sorted(nx_graph.nodes)
    min_angle = float('inf')

    # calc min angle formed by (i, j) and (j, k)
    for sid in sorted_node_ids:
        neighbors = sorted(nx_graph.neighbors(sid))
        pj = np.array(pos[sid])
        for i, n1 in enumerate(neighbors):
            pi = np.array(pos[n1])
            e1 = pi - pj
            for n2 in neighbors[i+1:]:
                pk = np.array(pos[n2])
                e2 = pj - pk
                angle = np.arccos(
                    np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))
                angle = min(np.pi - angle, angle)
                if angle < min_angle:
                    min_angle = angle

    max_degree = -float('inf')

    for id in sorted_node_ids:
        degree = int(nx_graph.degree(id))
        if max_degree < degree:
            max_degree = degree

    q = min_angle / ((2 * np.pi) / max_degree)

    return q
