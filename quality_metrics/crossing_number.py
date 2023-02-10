from utils import edge_crossing_finder_naive, edge_crossing_finder
from itertools import combinations


direction = 'minimize'


def quality_naive(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder_naive(nx_graph, pos)

    s = 0
    node_ids = sorted([node_id for node_id in edge_crossing])
    for i, sid in enumerate(node_ids):
        for tid in node_ids[i + 1:]:
            if edge_crossing[sid][tid]:
                s += 1

    return s


def quality(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder(nx_graph, pos)
    s = len(edge_crossing)
    # assert s == quality_naive(nx_graph, pos)
    return s
