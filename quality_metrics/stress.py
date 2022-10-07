import numpy as np
import networkx as nx


# minimize
def stress(nx_graph, pos, K=1, L=1):
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))
    s = 0
    node_ids = sorted([node_id for node_id in pos])
    for i, sid in enumerate(node_ids):
        for tid in node_ids[i + 1:]:
            norm = np.linalg.norm(np.array(pos[sid]) - np.array(pos[tid]))
            dij = shortest_paths[sid][tid]
            lij = L * dij
            kij = K * dij
            e = (kij * ((norm - lij) ** 2)) / 2

            s += e
    return s
