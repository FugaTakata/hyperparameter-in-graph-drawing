from scipy.spatial import Delaunay
import numpy as np
import networkx as nx


def generate_delaunay_triangulation_graph(pos, edge_weight=1):
    index_id_map = {}
    pos_array = []
    for index, node_id in enumerate(pos):
        positions = pos[node_id]
        position = [positions[0], positions[1]]
        pos_array.append(position)
        index_id_map[index] = node_id

    pos_ndarray = np.array(pos_array)
    delaunay = Delaunay(pos_ndarray)

    delaunay_triangulation_graph = nx.Graph()

    nodes = [node_id for node_id in pos]
    delaunay_triangulation_graph.add_nodes_from(nodes)

    weighted_edges = []
    for n in delaunay.simplices:
        n0 = n[0]
        n1 = n[1]
        n2 = n[2]
        weighted_edges.append(
            (index_id_map[n0], index_id_map[n1], edge_weight))
        weighted_edges.append(
            (index_id_map[n0], index_id_map[n2], edge_weight))
        weighted_edges.append(
            (index_id_map[n1], index_id_map[n2], edge_weight))
    delaunay_triangulation_graph.add_weighted_edges_from(weighted_edges)

    return delaunay_triangulation_graph


def jaccard_similarity_sum(nx_graph, nx_shape_graph):
    j_s_sum = 0
    for node in nx_graph.nodes:
        g_n = [n for n in nx_graph.neighbors(node)]
        s_n = [n for n in nx_shape_graph.neighbors(node)]
        and_n = list(set(g_n) & set(s_n))
        or_n = list(set(g_n + s_n))

        j_s_sum += len(and_n) / len(or_n)

    return j_s_sum / len(nx_graph.nodes)


direction = 'maximize'


# maximize
def quality(nx_graph, pos, edge_weight=1):
    nx_shape_graph = generate_delaunay_triangulation_graph(pos, edge_weight)

    return jaccard_similarity_sum(nx_graph, nx_shape_graph)
