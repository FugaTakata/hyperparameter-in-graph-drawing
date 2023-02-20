# Third Party Library
import numpy as np
from sklearn.neighbors import NearestNeighbors

direction = "maximize"


def quality_naive(nx_graph, pos):
    q = float("inf")

    for edge in nx_graph.edges:
        i, j = edge
        xi = np.array(pos[i])
        xj = np.array(pos[j])

        cij = (xi + xj) / 2
        rij = np.linalg.norm(xi - xj) / 2

        for node in nx_graph.nodes:
            xk = np.array(pos[node])
            if rij == 0:
                continue
            q_c = np.linalg.norm(xk - cij) / rij

            if q_c < q:
                q = q_c

    q = min(1, q)
    return q


def quality(nx_graph, pos):
    pos_list = [pos[i] for i in nx_graph.nodes]
    neighbors = NearestNeighbors(
        n_neighbors=1, algorithm='ball_tree').fit(pos_list)
    q = float("inf")
    for (i, j) in nx_graph.edges:
        xi = np.array(pos[i])
        xj = np.array(pos[j])

        cij = (xi + xj) / 2
        rij = np.linalg.norm(xi - xj) / 2
        if rij == 0:
            continue
        d, _ = neighbors.kneighbors([cij])
        q_c = d[0][0] / rij

        if q_c < q:
            q = q_c

    q = min(1, q)
    # assert q == quality_naive(nx_graph, pos)
    return q
