import json
import quality_metrics
import networkx as nx
import time

from quality_metrics import stress
from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph
from utils.calc_quality_metrics import calc_quality_metrics
from quality_metrics import node_resolution

DATASET_NAME = 'USpowerGrid'
DATASET_PATH = f'lib/egraph-rs/js/dataset/{DATASET_NAME}.json'

EDGE_WEIGHT = 30

# with open(DATASET_PATH) as f:
#     graph_data = json.load(f)
# nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
# graph, indices = generate_graph_from_nx_graph(nx_graph)
# all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

with open(f'data/rpfs_pos/{DATASET_NAME}.json') as f:
    jsondata = json.load(f)

for e in jsondata['e']:
    for seed in e['seed']:
        start = time.time()
        print('seed', seed)
        pos = e['seed'][str(seed)]['pos']
        e['seed'][str(seed)]['node_resolution'] = node_resolution.quality(pos)
        print(time.time() - start)

with open(f'data/rpfs_pos/{DATASET_NAME}/stress,node_resolution.json', mode='w') as f:
    json.dump(jsondata, f, ensure_ascii=False)
