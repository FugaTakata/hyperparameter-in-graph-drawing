import numpy as np
import networkx as nx


direction = 'minimize'


# minimize
def quality(nx_graph, pos, all_shortest_paths, K=1, L=1):
    if all_shortest_paths is None:
        all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))
    s = 0
    node_ids = sorted([node_id for node_id in pos])
    for i, sid in enumerate(node_ids):
        for tid in node_ids[i + 1:]:
            norm = np.linalg.norm(np.array(pos[sid]) - np.array(pos[tid]))
            dij = all_shortest_paths[sid][tid]
            lij = L * dij
            kij = K / dij ** 2
            e = (kij * ((norm - lij) ** 2)) / 2

            s += e
    return s
