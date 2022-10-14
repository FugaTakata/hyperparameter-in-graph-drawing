import json
import random
import argparse

import networkx as nx

import quality_metrics
from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph
from utils.calc_quality_metrics import calc_quality_metrics

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

# 前回の実験でstressの値がよかったparams
params = {
    "edge_length": 26,
    "number_of_pivots": 281,
    "number_of_iterations": 867,
    "eps": 0.4001671578513263
}

data = {}
data['description'] = 'rpfs: random params, free seed. 2022/09/27の実験でstressの結果がよかったparamsを用いてUSpowerGridを描画する。このときseedの固定を外すことでparamsが運良くseedにはまったのか？それともどんなseedでもうまく行くのかを調べる。追加で、どんなパラメータであってもseedに依存しないことを確認したい。'
data['e'] = []

for _ in range(0, 20):
    rd = {}
    rd['seed'] = {}
    params = {
        'edge_length': random.randint(1, 100),
        'number_of_pivots': random.randint(1, len(nx_graph.nodes)),
        'number_of_iterations': random.randint(1, 1000),
        'eps': random.uniform(0.01, 1)
    }
    rd['params'] = params
    for seed in range(0, 10):
        print('_', _, 'seed', seed)
        pos = draw_graph(graph, indices, params, seed)
        quality_metrics = calc_quality_metrics(
            nx_graph, pos, edge_weight=EDGE_WEIGHT)

        rd['seed'][seed] = {
            'stress': quality_metrics['stress'],
            'pos': pos,
        }
    data['e'].append(rd)


with open(f'data/{dataset_name}_rpfs.json', mode='w') as f:
    json.dump(data, f, ensure_ascii=False)
