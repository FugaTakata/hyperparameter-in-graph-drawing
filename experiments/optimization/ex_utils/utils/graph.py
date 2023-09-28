# Standard Library
import json
from pathlib import Path

# Third Party Library
import networkx as nx
from egraph import Graph


def load_nx_graph(dataset_path: Path):
    with open(dataset_path) as f:
        graph_data = json.load(f)
    return nx.node_link_graph(graph_data)


def nx_graph_preprocessing(nx_graph, edge_weight):
    nx_graph = nx.Graph(nx_graph)

    nx_graph = nx_graph.to_undirected()
    nx_graph.remove_edges_from(list(nx.selfloop_edges(nx_graph)))

    largest_cc = max(nx.connected_components(nx_graph), key=len)
    largest_cc_graph = nx_graph.subgraph(largest_cc)

    new_graph = nx.Graph()
    nodes = [str(node_id) for node_id in largest_cc_graph.nodes]
    new_graph.add_nodes_from(nodes)

    for i, edge in enumerate(largest_cc_graph.edges):
        new_graph.add_edge(
            str(edge[0]), str(edge[1]), weight=edge_weight, id=str(i)
        )

    return new_graph


def egraph_graph(nx_graph):
    eg_graph = Graph()

    eg_indices = {}
    for u in nx_graph.nodes:
        eg_indices[u] = eg_graph.add_node(u)
    for u, v in nx_graph.edges:
        eg_graph.add_edge(eg_indices[u], eg_indices[v], (u, v))

    return eg_graph, eg_indices
