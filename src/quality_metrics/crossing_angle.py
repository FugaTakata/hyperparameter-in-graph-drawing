# Third Party Library
import numpy as np

# First Party Library
from utils import edge_crossing_finder

direction = "minimize"


def quality(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder(nx_graph, pos)
    q = 0
    for (s1, t1), (s2, t2) in edge_crossing:
        ps1 = np.array(pos[s1])
        pt1 = np.array(pos[t1])
        e1 = ps1 - pt1
        ps2 = np.array(pos[s2])
        pt2 = np.array(pos[t2])
        e2 = ps2 - pt2
        angle = np.arccos(
            max(
                min(
                    1,
                    np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)),
                ),
                -1,
            )
        )

        q_c = max(abs(np.pi - angle - np.pi / 2), abs(angle - np.pi / 2)) / (
            np.pi / 2
        )

        if q < q_c:
            q = q_c

    return q
