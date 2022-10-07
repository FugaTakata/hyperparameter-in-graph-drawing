from utils import edge_crossing_finder
import numpy as np


# maximization
def crossing_angle_maximization(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder(nx_graph, pos)
    s = 0
    for s1, t1, attr1 in nx_graph.edges(data=True):
        id1 = attr1['id']
        for s2, t2, attr2 in nx_graph.edges(data=True):
            id2 = attr2['id']
            if edge_crossing[id1][id2] or edge_crossing[id2][id1]:
                e1 = np.array(pos[s1]) - np.array(pos[t1])
                e2 = np.array(pos[s2]) - np.array(pos[t2])
                s += np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))

    return s
