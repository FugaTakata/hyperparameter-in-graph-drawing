import networkx as nx
from egraph import Graph, Coordinates, Rng, SparseSgd
import json
from tulip import tlp


def generate_egraph_graph(nx_graph):
    eg_graph = Graph()

    indices = {}
    for u in nx_graph.nodes:
        indices[u] = eg_graph.add_node(u)
    for u, v in nx_graph.edges:
        eg_graph.add_edge(indices[u], indices[v], (u, v))

    return eg_graph, indices


def generate_tulip_graph(nx_graph):
    tlp_graph = tlp.newGraph()
    nx_tlp_node_map = {}

    for u in nx_graph.nodes:
        tlp_node = tlp_graph.addNode({'nx_id': u})
        nx_tlp_node_map[str(u)] = tlp_node

    for u, v in nx_graph.edges:
        tlp_graph.addEdge(nx_tlp_node_map[str(u)], nx_tlp_node_map[str(v)], {})

    return tlp_graph


# グラフの生成・読み込み
def generate_graph_from_nx_graph(nx_graph):
    graph = Graph()

    indices = {}
    for u in nx_graph.nodes:
        indices[u] = graph.add_node(u)
    for u, v in nx_graph.edges:
        graph.add_edge(indices[u], indices[v], (u, v))

    return graph, indices


def graph_preprocessing(nx_graph, edge_weight=1):
    nx_graph = nx.Graph(nx_graph)

    # グラフを無向グラフに
    nx_graph = nx_graph.to_undirected()

    # エッジの自己ループを除去
    nx_graph.remove_edges_from(list(nx.selfloop_edges(nx_graph)))

    # 最大連結成分を用いる
    largest_cc = max(nx.connected_components(nx_graph), key=len)
    largest_cc_graph = nx_graph.subgraph(largest_cc)

    new_graph = nx.Graph()
    nodes = [str(node_id) for node_id in largest_cc_graph.nodes]
    new_graph.add_nodes_from(nodes)

    # エッジにidと重みを追加
    for i, edge in enumerate(largest_cc_graph.edges):
        new_graph.add_edge(str(edge[0]), str(
            edge[1]), weight=edge_weight, id=str(i))

    return new_graph


def load_nx_graph(dataset_path, edge_weight=1):
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(
        nx.node_link_graph(graph_data), edge_weight=edge_weight)

    return nx_graph


# グラフの描画
def draw_graph(graph, indices, params, seed=0):
    drawing = Coordinates.initial_placement(graph)
    for u, i in indices.items():
        print(drawing.x(i), drawing.y(i))
    rng = Rng.seed_from(seed)  # random seed
    sgd = SparseSgd(
        graph,
        lambda _: params['edge_length'],  # edge length
        params['number_of_pivots'],  # number of pivots
        rng,
    )
    scheduler = sgd.scheduler(
        params['number_of_iterations'],  # number of iterations
        params['eps'],  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    def step(eta):
        sgd.shuffle(rng)
        sgd.apply(drawing, eta)

    scheduler.run(step)

    pos = {u: (drawing.x(i), drawing.y(i)) for u, i in indices.items()}
    for u, i in indices.items():
        print(drawing.x(i), drawing.y(i))

    return pos
