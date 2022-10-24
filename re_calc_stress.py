import json
import quality_metrics
import networkx as nx

from quality_metrics import stress
from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph
from utils.calc_quality_metrics import calc_quality_metrics

DATASET_NAME = 'USpowerGrid'
DATASET_PATH = f'lib/egraph-rs/js/dataset/{DATASET_NAME}.json'

EDGE_WEIGHT = 30

with open(DATASET_PATH) as f:
    graph_data = json.load(f)
nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
graph, indices = generate_graph_from_nx_graph(nx_graph)
all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

with open(f'data/{DATASET_NAME}_rpfs.json') as f:
    jsondata = json.load(f)

data = None
for seed in range(0, 10):
    print('seed', seed)
    pos = jsondata['e']['seed'][seed]['pos']
    quality_metrics = stress(
        nx_graph, pos, all_shortest_paths=all_shortest_paths)

    jsondata['e']['seed'][seed]['stress'] = quality_metrics

with open(f'data/{DATASET_NAME}_rpfs_new.json', mode='w') as f:
    json.dump(jsondata, f, ensure_ascii=False)
