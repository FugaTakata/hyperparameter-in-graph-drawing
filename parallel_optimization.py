'''
SparseSgdのパラメータ最適化実験
'''

import json
import argparse
import os
from multiprocessing import Process
import time

import networkx as nx
import optuna

from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph, edge_crossing_finder
from quality_metrics import angular_resolution, aspect_ratio, crossing_angle, crossing_number, gabriel_graph_property, ideal_edge_length, node_resolution, run_time, shape_based_metrics, stress


def objective_wrapper(nx_graph, graph, indices, qnames, all_shortest_paths, edge_weight=1):
    def objective(trial: optuna.Trial):
        params = {
            'edge_length': edge_weight,
            'number_of_pivots': trial.suggest_int('number_of_pivots', 1, len(nx_graph.nodes)),
            'number_of_iterations': trial.suggest_int('number_of_iterations', 1, 200),
            'eps': trial.suggest_float('eps', 0.01, 1)
        }
        trial.set_user_attr('params', params)

        rt = run_time.RunTime()
        rt.start()
        pos = draw_graph(graph, indices, params)
        rt.end()

        trial.set_user_attr('pos', pos)

        # quality_metrics = calc_quality_metrics(
        #     nx_graph, pos, all_shortest_paths, edge_weight)
        quality_metrics = calc_qs(
            nx_graph, pos, all_shortest_paths, qnames, edge_weight)
        quality_metrics = {
            **quality_metrics,
            'run_time': rt.quality()
        }
        trial.set_user_attr('quality_metrics', quality_metrics)

        result = tuple([quality_metrics[name]
                       for name in qnames])
        return result
    return objective


def calc_qs(nx_graph, pos, all_shortest_paths, qnames, edge_weight=1):
    result = {}
    edge_crossing = None
    if 'crossing_angle' in qnames or 'crossing_number' in qnames:
        edge_crossing = edge_crossing_finder(nx_graph, pos)

    for qname in qnames:
        if qname == 'angular_resolution':
            result[qname] = angular_resolution.quality(nx_graph, pos)
        elif qname == 'aspect_ratio':
            result[qname] = aspect_ratio.quality(nx_graph, pos)
        elif qname == 'crossing_angle':
            result[qname] = crossing_angle.quality(
                nx_graph, pos, edge_crossing)
        elif qname == 'crossing_number':
            result[qname] = crossing_number.quality(
                nx_graph, pos, edge_crossing)
        elif qname == 'gabriel_graph_property':
            result[qname] = gabriel_graph_property.quality(nx_graph, pos)
        elif qname == 'ideal_edge_length':
            result[qname] = ideal_edge_length.quality(
                nx_graph, pos, all_shortest_paths)
        elif qname == 'node_resolution':
            result[qname] = node_resolution.quality(pos)
        elif qname == 'shape_based_metrics':
            result[qname] = shape_based_metrics.quality(
                nx_graph, pos, edge_weight)
        elif qname == 'stress':
            result[qname] = stress.quality(nx_graph, pos, all_shortest_paths)

    return result


def parse_args():
    # lib/egraph-rs/js/dataset/{dataset_name}.json
    # data/optimization/{dataset_name}/{target_qs}.json
    parser = argparse.ArgumentParser()
    # USpowerGrid
    parser.add_argument('dataset_name')

    # node_resolution,stress or all
    parser.add_argument('target_qs')

    # n_trials
    parser.add_argument('n_trials')

    # concurrency
    parser.add_argument('concurrency')

    args = parser.parse_args()

    return args


def optimize(dataset_path, qnames, n_trials, database_uri, study_name, edge_weight=1):
    # グラフのロード
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), edge_weight)
    graph, indices = generate_graph_from_nx_graph(nx_graph)
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    qmap = {
        'angular_resolution': angular_resolution,
        'aspect_ratio': aspect_ratio,
        'crossing_angle': crossing_angle,
        'crossing_number': crossing_number,
        'gabriel_graph_property': gabriel_graph_property,
        'ideal_edge_length': ideal_edge_length,
        'node_resolution': node_resolution,
        'run_time': run_time,
        'shape_based_metrics': shape_based_metrics,
        'stress': stress
    }

    # 最適化
    study = optuna.create_study(
        directions=[qmap[qname].direction
                    for qname in qnames],
        storage=database_uri,
        study_name=study_name,
        load_if_exists=True
    )

    study.optimize(objective_wrapper(nx_graph, graph, indices, qnames, all_shortest_paths,
                   edge_weight=edge_weight), n_trials=n_trials, show_progress_bar=True)


if __name__ == '__main__':
    EDGE_WEIGHT = 30

    all_qnames = [
        'angular_resolution',
        'aspect_ratio',
        'crossing_angle',
        'crossing_number',
        'gabriel_graph_property',
        'ideal_edge_length',
        'node_resolution',
        'run_time',
        'shape_based_metrics',
        'stress',
    ]

    args = parse_args()
    dataset_name = args.dataset_name
    target_qs = args.target_qs
    n_trials = int(args.n_trials)
    concurrency = int(args.concurrency)

    dataset_path = f'lib/egraph-rs/js/dataset/{dataset_name}.json'
    database_uri = f'sqlite:///db/optimization/{dataset_name}/{target_qs}.db'
    study_name = f'{target_qs}'

    # targetとなるquality metrics名の配列作成
    target_qnames = [
        qname for qname in all_qnames] if target_qs == 'all' else target_qs.split(',')

    qnames = []
    for tqname in target_qnames:
        if tqname in all_qnames:
            qnames.append(tqname)
        else:
            raise ValueError(f'{tqname} in {target_qnames} is not accepted')
    qnames = sorted(qnames)

    concurrency = 4
    max_cpu = os.cpu_count()
    assert concurrency <= max_cpu
    n_trials_per_cpu = int(n_trials / concurrency)

    workers = [Process(target=optimize, kwargs={
        'dataset_path': dataset_path,
        'qnames': qnames,
        'n_trials': n_trials_per_cpu,
        'database_uri': database_uri,
        'study_name': study_name,
        'edge_weight': EDGE_WEIGHT
    }) for _ in range(concurrency)]

    for worker in workers:
        worker.start()
        time.sleep(2)
