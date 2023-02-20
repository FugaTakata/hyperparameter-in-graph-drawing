from utils import edge_crossing_finder_naive, edge_crossing_finder
import numpy as np
from itertools import combinations


direction = 'minimize'


def quality_naive(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder_naive(nx_graph, pos)
    sorted_edges = sorted(nx_graph.edges(data=True),
                          key=lambda x: int(x[2]['id']))
    q = 0

    for i, (s1, t1, attr1) in enumerate(sorted_edges):
        id1 = attr1['id']
        ps1 = np.array(pos[s1])
        pt1 = np.array(pos[t1])
        e1 = ps1 - pt1
        for s2, t2, attr2 in sorted_edges[i + 1:]:
            id2 = attr2['id']
            if edge_crossing[id1][id2] or edge_crossing[id2][id1]:
                ps2 = np.array(pos[s2])
                pt2 = np.array(pos[t2])
                e2 = ps2 - pt2
                angle = np.arccos(
                    max(min(1, np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))), -1))

                q_c = max(abs(np.pi - angle - np.pi/2),
                          abs(angle - np.pi/2))/(np.pi/2)

                if q < q_c:
                    q = q_c

    return q


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
            max(min(1, np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))), -1))

        q_c = max(abs(np.pi - angle - np.pi/2),
                  abs(angle - np.pi/2))/(np.pi/2)

        if q < q_c:
            q = q_c

    # assert q == quality_naive(nx_graph, pos)
    return q
