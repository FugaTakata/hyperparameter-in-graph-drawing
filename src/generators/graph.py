# Third Party Library
from egraph import Graph


def egraph_graph(nx_graph):
    eg_graph = Graph()

    eg_indices = {}
    for u in nx_graph.nodes:
        eg_indices[u] = eg_graph.add_node(u)
    for u, v in nx_graph.edges:
        eg_graph.add_edge(eg_indices[u], eg_indices[v], (u, v))

    return eg_graph, eg_indices
