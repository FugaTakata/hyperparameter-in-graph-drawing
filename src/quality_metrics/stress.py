import numpy as np
import networkx as nx
from scipy.spatial.distance import pdist
from itertools import combinations


direction = 'minimize'


def quality_naive(nx_graph, pos, all_shortest_paths, K=1, L=1):
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


def quality(nx_graph, pos, all_shortest_paths, K=1, L=1):
    if all_shortest_paths is None:
        all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))
    dx = pdist([pos[i] for i in nx_graph.nodes])
    d = np.array([all_shortest_paths[i][j]
                 for i, j in combinations(nx_graph.nodes, 2)])
    # たぶん / 2 いらないけど互換性のため残す
    s = np.sum(((K / d ** 2) * (dx - L * d) ** 2) / 2)
    # assert np.isclose(s, quality_naive(nx_graph, pos, all_shortest_paths, K, L))
    return s
