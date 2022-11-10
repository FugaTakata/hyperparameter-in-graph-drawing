import json
import random
import argparse

import networkx as nx

import quality_metrics
from quality_metrics import node_resolution
from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph
from quality_metrics import stress

parser = argparse.ArgumentParser()
parser.add_argument('dataset_name')
args = parser.parse_args()

dataset_name = args.dataset_name

print(dataset_name)

DATASET_PATH = f'lib/egraph-rs/js/dataset/{dataset_name}.json'

EDGE_WEIGHT = 30


with open(DATASET_PATH) as f:
    graph_data = json.load(f)
nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
graph, indices = generate_graph_from_nx_graph(nx_graph)
all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

# 前回の実験でstressの値がよかったparams
params = {
    "edge_length": 56,
    "number_of_pivots": 917,
    "number_of_iterations": 155,
    "eps": 0.8459816384096752
}

data = {}
data['description'] = 'opfs: optimized params, free seed. 2022/09/27の実験でstressの結果がよかったparamsを用いてUSpowerGridを描画する。このときseedの固定を外すことでparamsが運良くseedにはまったのか？それともどんなseedでもうまく行くのかを調べる。追加で、どんなパラメータであってもseedに依存しないことを確認したい。'
data['e'] = []


rd = {}
rd['seed'] = {}
rd['params'] = params
for seed in range(0, 10):
    print('seed', seed)
    pos = draw_graph(graph, indices, params, seed)

    rd['seed'][seed] = {
        'node_resolution': node_resolution.quality(pos),
        'pos': pos,
    }
data['e'].append(rd)


with open(f'data/opfs_pos/{dataset_name}/node_resolution.json', mode='w') as f:
    json.dump(data, f, ensure_ascii=False)
