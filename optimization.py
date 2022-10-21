import json
import argparse

import optuna
import networkx as nx

from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph
from utils.calc_quality_metrics import calc_quality_metrics

parser = argparse.ArgumentParser()
parser.add_argument('dataset_name')
args = parser.parse_args()

dataset_name = args.dataset_name

print(dataset_name)

DATASET_PATH = f'lib/egraph-rs/js/dataset/{dataset_name}.json'

EDGE_WEIGHT = 30
N_TRIALS = 100

quality_metrics_direction = {}
quality_metrics_direction['stress'] = "minimize"
quality_metrics_direction['ideal_edge_length'] = "minimize"
quality_metrics_direction['shape_based_metrics'] = 'maximize'
quality_metrics_direction['crossing_number'] = "minimize"
quality_metrics_direction['crossing_angle_maximization'] = 'maximize'
quality_metrics_direction['aspect_ratio'] = 'maximize'
quality_metrics_direction['angular_resolution'] = 'maximize'
quality_metrics_direction['node_resolution'] = 'maximize'
quality_metrics_direction['gabriel_graph_property'] = "minimize"

quality_metrics_names = [
    'angular_resolution',
    'aspect_ratio',
    'crossing_angle_maximization',
    'crossing_number',
    'gabriel_graph_property',
    'ideal_edge_length',
    'node_resolution',
    'shape_based_metrics',
    'stress'
]


def objective_wrapper(nx_graph, graph, indices, quality_metrics_names, all_shortest_paths, edge_weight=1):
    def objective(trial: optuna.Trial):
        params = {
            'edge_length': trial.suggest_int('edge_length', 1, 100),
            'number_of_pivots': trial.suggest_int('number_of_pivots', 1, len(nx_graph.nodes)),
            'number_of_iterations': trial.suggest_int('number_of_iterations', 1, 1000),
            'eps': trial.suggest_float('eps', 0.01, 1)
        }
        trial.set_user_attr('params', params)

        pos = draw_graph(graph, indices, params)
        trial.set_user_attr('pos', pos)

        quality_metrics = calc_quality_metrics(
            nx_graph, pos, all_shortest_paths, edge_weight)
        trial.set_user_attr('quality_metrics', quality_metrics)

        result = tuple([quality_metrics[name]
                       for name in quality_metrics_names])
        return result
    return objective


with open(DATASET_PATH) as f:
    graph_data = json.load(f)
nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
graph, indices = generate_graph_from_nx_graph(nx_graph)
all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

study = optuna.create_study(
    directions=[quality_metrics_direction[name]
                for name in quality_metrics_names]
)

study.optimize(objective_wrapper(nx_graph, graph, indices, quality_metrics_names,
               all_shortest_paths, edge_weight=EDGE_WEIGHT), n_trials=N_TRIALS, show_progress_bar=True)

best_trials_data = {
    'description': '9つの評価を用いた最適化結果のbest_trialsデータ',
    'data': {}
}
for best_trial in study.best_trials:
    trial_number = best_trial.number

    params = best_trial.user_attrs['params']
    pos = best_trial.user_attrs['pos']
    quality = best_trial.user_attrs['quality_metrics']
    best_trials_data['data'][trial_number] = {
        'params': params,
        'quality': quality,
        'pos': pos
    }


with open(f'data/optimization/{dataset_name}.json', mode='w') as f:
    json.dump(best_trials_data, f, ensure_ascii=False)
