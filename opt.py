import json
import argparse

import optuna
import networkx as nx

from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph, edge_crossing_finder
from quality_metrics import angular_resolution, aspect_ratio, crossing_angle, crossing_number, gabriel_graph_property, ideal_edge_length, node_resolution, shape_based_metrics, stress


def objective_wrapper(nx_graph, graph, indices, qnames, all_shortest_paths, edge_weight=1):
    def objective(trial: optuna.Trial):
        params = {
            'edge_length': edge_weight,
            'number_of_pivots': trial.suggest_int('number_of_pivots', 1, len(nx_graph.nodes)),
            'number_of_iterations': trial.suggest_int('number_of_iterations', 1, 1000),
            'eps': trial.suggest_float('eps', 0.01, 1)
        }
        trial.set_user_attr('params', params)

        pos = draw_graph(graph, indices, params)
        trial.set_user_attr('pos', pos)

        # quality_metrics = calc_quality_metrics(
        #     nx_graph, pos, all_shortest_paths, edge_weight)
        quality_metrics = calc_qs(
            nx_graph, pos, all_shortest_paths, qnames, edge_weight)
        trial.set_user_attr('quality_metrics', quality_metrics)

        result = tuple([quality_metrics[name]
                       for name in qnames])
        return result
    return objective


def parse_args():
    # lib/egraph-rs/js/dataset/{dataset_name}.json
    # data/optimization/{dataset_name}/{target_qs}.json
    parser = argparse.ArgumentParser()
    # USpowerGrid
    parser.add_argument('dataset_name')

    # node_resolution,stress or all
    parser.add_argument('target_qs')

    args = parser.parse_args()

    return args


def calc_qs(nx_graph, pos, all_shortest_paths, qnames, edge_weight=1):
    result = {}
    edge_crossing = None
    if 'crossing_angle' in qnames or 'crossing_number' in qnames:
        edge_crossing = edge_crossing_finder(nx_graph, pos)

    for qname in qnames:
        if qname == 'angular_resolution':
            result[qname] = angular_resolution.quality(nx_graph, pos)
        elif qname == 'aspect_ratio':
            result[qname] = aspect_ratio.quality(pos)
        elif qname == 'crossing_angle':
            result[qname] = crossing_angle.quality(
                nx_graph, pos, edge_crossing)
        elif qname == 'crossing_number':
            result[qname] = crossing_number.quality(
                nx_graph, pos, edge_crossing)
        elif qname == 'gabriel_graph_property':
            result[qname] = gabriel_graph_property.quality(nx_graph, pos)
        elif qname == 'ideal_edge_length':
            result[qname] = ideal_edge_length.quality(nx_graph, pos)
        elif qname == 'node_resolution':
            result[qname] = node_resolution.quality(pos)
        elif qname == 'shape_based_metrics':
            result[qname] = shape_based_metrics.quality(
                nx_graph, pos, edge_weight)
        elif qname == 'stress':
            result[qname] = stress.quality(nx_graph, pos, all_shortest_paths)

    return result


def main():
    EDGE_WEIGHT = 30
    N_TRIALS = 100

    all_qnames = [
        'angular_resolution',
        'aspect_ratio',
        'crossing_angle',
        'crossing_number',
        'gabriel_graph_property',
        'ideal_edge_length',
        'node_resolution',
        'shape_based_metrics',
        'stress']
    qmap = {
        'angular_resolution': angular_resolution,
        'aspect_ratio': aspect_ratio,
        'crossing_angle': crossing_angle,
        'crossing_number': crossing_number,
        'gabriel_graph_property': gabriel_graph_property,
        'ideal_edge_length': ideal_edge_length,
        'node_resolution': node_resolution,
        'shape_based_metrics': shape_based_metrics,
        'stress': stress
    }

    args = parse_args()
    dataset_name = args.dataset_name
    target_qs = args.target_qs

    dataset_path = f'lib/egraph-rs/js/dataset/{dataset_name}.json'
    export_path = f'data/optimization/{dataset_name}/{target_qs}.json'

    # targetとなるparams配列作成
    target_qnames = [
        qname for qname in all_qnames] if target_qs == 'all' else target_qs.split(',')

    qnames = []
    for tqname in target_qnames:
        if tqname in all_qnames:
            qnames.append(tqname)
        else:
            raise ValueError(f'{tqname} in {target_qnames} is not accepted')
    qnames = sorted(qnames)

    # グラフロード
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    graph, indices = generate_graph_from_nx_graph(nx_graph)
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    # 最適化
    study = optuna.create_study(
        directions=[qmap[qname].direction
                    for qname in qnames]
    )

    study.optimize(objective_wrapper(nx_graph, graph, indices, qnames, all_shortest_paths,
                   edge_weight=EDGE_WEIGHT), n_trials=N_TRIALS, show_progress_bar=True)

    # 出力作成
    export_data = {
        'description': f'{qnames}を用いた最適化のパレート解',
        'data': {}
    }

    for best_trial in study.best_trials:
        trial_number = best_trial.number

        params = best_trial.user_attrs['params']
        pos = best_trial.user_attrs['pos']
        quality = best_trial.user_attrs['quality_metrics']
        export_data['data'][trial_number] = {
            'params': params,
            'quality': quality,
            'pos': pos
        }

    # 出力
    with open(export_path, mode='w') as f:
        json.dump(export_data, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
