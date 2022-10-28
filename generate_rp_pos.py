'''
rp: random params. rpで作成した描画結果を量産する。
'''

import os
import json
import random
import argparse

import networkx as nx

import quality_metrics
from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph
from utils.calc_quality_metrics import calc_quality_metrics

parser = argparse.ArgumentParser()
parser.add_argument('prefix')
parser.add_argument('dataset_name')
args = parser.parse_args()

dataset_name = args.dataset_name
prefix = args.prefix

print(dataset_name)

DATASET_PATH = f'lib/egraph-rs/js/dataset/{dataset_name}.json'

EDGE_WEIGHT = 30


with open(DATASET_PATH) as f:
    graph_data = json.load(f)
nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
graph, indices = generate_graph_from_nx_graph(nx_graph)
all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

data = {}
data['description'] = 'rp: random params. rpで作成した描画結果'
data['params_description'] = "{'edge_length': random.randint(1, 100),'number_of_pivots': random.randint(1, len(nx_graph.nodes)),'number_of_iterations': random.randint(1, 1000),'eps': random.uniform(0.01, 1)}"

write_file_path = f'data/rp_pos/{prefix}_{dataset_name}.json'
with open(write_file_path, mode='a') as f:
    while True:
        # avoid exceeding 100MB
        print(os.path.getsize(write_file_path))
        if 0.9 * 10 ** 8 < os.path.getsize(write_file_path):
            break

        seed = 0
        params = {
            'edge_length': random.randint(1, 100),
            'number_of_pivots': random.randint(1, len(nx_graph.nodes)),
            'number_of_iterations': random.randint(1, 1000),
            'eps': random.uniform(0.01, 1)
        }

        pos = draw_graph(graph, indices, params, seed)
        quality_metrics = calc_quality_metrics(
            nx_graph, pos, all_shortest_paths, edge_weight=EDGE_WEIGHT)

        data['seed'] = seed
        data['params'] = params
        data['quality_metrics'] = quality_metrics
        data['pos'] = pos

        jsondata = json.dumps(data, ensure_ascii=False)
        f.write(jsondata + '\n')
