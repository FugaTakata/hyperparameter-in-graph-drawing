import networkx as nx
from egraph import Graph, Coordinates, Rng, SparseSgd


# グラフの生成・読み込み
def generate_graph_from_nx_graph(nx_graph):
    graph = Graph()

    indices = {}
    for u in nx_graph.nodes:
        indices[u] = graph.add_node(u)
    for u, v in nx_graph.edges:
        graph.add_edge(indices[u], indices[v], (u, v))

    return graph, indices


def graph_preprocessing(nx_graph, edge_weight=0):
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


# グラフの描画
def draw_graph(graph, indices, params, seed=0):
    drawing = Coordinates.initial_placement(graph)
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

    return pos
