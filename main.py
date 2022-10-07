import json
import quality_metrics
from utils import graph_preprocessing, generate_graph_from_nx_graph
import networkx as nx
from utils.calc_quality_metrics import calc_quality_metrics

from utils.graph import draw_graph

DATASET_NAME = 'bull'
DATASET_PATH = f'lib/egraph-rs/js/dataset/{DATASET_NAME}.json'

with open(DATASET_PATH) as f:
    graph_data = json.load(f)
nx_graph = graph_preprocessing(nx.node_link_graph(graph_data))
graph, indices = generate_graph_from_nx_graph(nx_graph)

# 前回の実験でstressの値がよかったparams
params = {
    "edge_length": 26,
    "number_of_pivots": 281,
    "number_of_iterations": 867,
    "eps": 0.4001671578513263
}

data = {}
data['params'] = params
data['description'] = '2022/09/27の実験でstressの結果がよかったparamsを用いてUSpowerGridを描画する。このときseedの固定を外すことでparamsが運良くseedにはまったのか？それともどんなseedでもうまく行くのかを調べる。'
data['seed'] = {}


for seed in range(0, 20):
    pos = draw_graph(graph, indices, params)
    quality_metrics = calc_quality_metrics(nx_graph, pos)

    data['seed'][seed] = {
        'pos': pos,
        'quality_metrics': quality_metrics
    }


with open(f'data/{DATASET_NAME}_result.json', mode='w') as f:
    json.dump(data, f, ensure_ascii=False)
