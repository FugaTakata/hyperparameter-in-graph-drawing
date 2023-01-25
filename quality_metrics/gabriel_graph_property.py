# Third Party Library
import numpy as np

direction = "maximize"


def quality(nx_graph, pos):
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
