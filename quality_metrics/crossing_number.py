from utils import edge_crossing_finder


direction = 'minimize'


# minimize
def quality(nx_graph, pos, edge_crossing=None):
    if edge_crossing is None:
        edge_crossing = edge_crossing_finder(nx_graph, pos)

    s = 0
    node_ids = sorted([node_id for node_id in edge_crossing])
    for i, sid in enumerate(node_ids):
        for tid in node_ids[i + 1:]:
            if edge_crossing[sid][tid]:
                s += 1

    return s
