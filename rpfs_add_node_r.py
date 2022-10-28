'''
rp: random params. rpで作成した描画結果を量産する。
'''

import json
import argparse
import time

import networkx as nx

from utils import graph_preprocessing, generate_graph_from_nx_graph
from quality_metrics import node_resolution, stress

parser = argparse.ArgumentParser()
# parser.add_argument('prefix')
parser.add_argument('dataset_name')
args = parser.parse_args()

dataset_name = args.dataset_name
# prefix = args.prefix

print(dataset_name)

data = {}
data['description'] = 'rp: random params. rpで作成した描画結果'
data['params_description'] = "{'edge_length': random.randint(1, 100),'number_of_pivots': random.randint(1, len(nx_graph.nodes)),'number_of_iterations': random.randint(1, 1000),'eps': random.uniform(0.01, 1)}"

with open(f'data/{dataset_name}_rpfs.json') as f:
    jsondata = json.load(f)

write_file_path = f'data/rpfs_pos/{dataset_name}.json'
with open(write_file_path, mode='w') as f:
    for e in jsondata['e']:
        params = e['params']
        for seed in e['seed']:
            print('seed', seed)
            start = time.time()
            t = e['seed'][seed]
            pos = t['pos']
            # t['stress'] = stress(nx_graph, pos, all_shortest_paths)
            t['node_resolution'] = node_resolution(pos)
            print(time.time() - start)

    json.dump(jsondata, f, ensure_ascii=False)
