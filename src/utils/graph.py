# Standard Library
import json

# Third Party Library
import networkx as nx

# First Party Library
from config.paths import get_dataset_path


def load_nx_graph(dataset_name, edge_weight):
    dataset_path = get_dataset_path(dataset_name=dataset_name)
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(
        nx_graph=nx.node_link_graph(graph_data), edge_weight=edge_weight
    )

    return nx_graph


def get_shortest_path_length(nx_graph):
    shortest_path_length = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    return shortest_path_length


def graph_preprocessing(nx_graph, edge_weight):
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
