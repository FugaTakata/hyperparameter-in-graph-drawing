'''
SparseSgdのパラメータ最適化実験
'''

import json
import argparse
import os
from multiprocessing import Process
import math
import time

import networkx as nx
import optuna
from tulip import tlp

from utils import graph_preprocessing
from utils.calc_quality_metrics import calc_qs
from utils.graph import generate_egraph_graph, generate_tulip_graph
from quality_metrics.run_time import RunTime
from quality_metrics import angular_resolution, aspect_ratio, crossing_angle, crossing_number, gabriel_graph_property, ideal_edge_length, node_resolution, run_time, shape_based_metrics, stress


from drawing.sgd import sgd
from drawing.fruchterman_reingold import fruchterman_reingold
from drawing.fm3 import fm3
from drawing.kamada_kawai import kamada_kawai

SS = 'Sparse-SGD'
FR = 'Fruchterman-Reingold'
FM3 = 'FM3'
KK = 'Kamada-Kawai'


def optimize(dataset_path, qnames, n_trials, database_uri, study_name, layout_name, edge_weight=1):
    # グラフのロード
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), edge_weight)
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

    if layout_name == FR:
        initial_pos = nx.random_layout(nx_graph, seed=0)
        study.optimize(fr_objective(initial_pos=initial_pos, nx_graph=nx_graph, all_shortest_paths=all_shortest_paths, qnames=qnames, edge_weight=edge_weight),
                       n_trials=n_trials, show_progress_bar=True)
    elif layout_name == KK:
        graph, indices = generate_egraph_graph(nx_graph)
        study.optimize(kk_objective(nx_graph=nx_graph, eg_graph=graph, indices=indices, all_shortest_paths=all_shortest_paths, qnames=qnames, edge_weight=edge_weight),
                       n_trials=n_trials, show_progress_bar=True)
    elif layout_name == SS:
        graph, indices = generate_egraph_graph(nx_graph)
        study.optimize(ss_objective(nx_graph, graph, indices, qnames, all_shortest_paths,
                                    edge_weight=edge_weight), n_trials=n_trials, show_progress_bar=True)
    elif layout_name == FM3:
        tlp_graph = generate_tulip_graph(nx_graph)
        study.optimize(fm3_objective(nx_graph=nx_graph, tlp_graph=tlp_graph, all_shortest_paths=all_shortest_paths,
                       qnames=qnames, edge_weight=edge_weight), n_trials=n_trials, show_progress_bar=True)


def fm3_objective(nx_graph, tlp_graph, all_shortest_paths, qnames, edge_weight):
    def objective(trial: optuna.Trial):
        tlp_layout_name = 'FM^3 (OGDF)'
        base_params = {
            "unit edge length": edge_weight,
            "new initial placement": True,
            "fixed iterations": 100,
            "threshold": 0.01,
            "page format": "square",
            "quality vs speed": "beautiful and fast",
            "edge length measurement": "midpoint",
            "allowed positions": "all",
            "tip over": "no growing row",
            "presort": "decreasing height",
            "galaxy choice": "non uniform lower mass",
            "max iter change": "linearly decreasing",
            "initial placement": "advanced",
            "force model": "new",
            "repulsive force method": "nmm",
            "initial placement forces": "uniform grid",
            "reduced tree construction": "subtree by subtree",
            "smallest cell finding": "iteratively",
        }
        params = {
            **tlp.getDefaultPluginParameters(tlp_layout_name, tlp_graph),
            **base_params,
            "fixed iterations": trial.suggest_int('fixed iterations', 1, 1000),
            "threshold": trial.suggest_float('threshold', 0.001, 1.0),
        }
        run_time = RunTime()

        run_time.start()
        pos = fm3(tlp_graph, params)
        run_time.end()
        trial.set_user_attr('pos', pos)

        quality_metrics = calc_qs(
            nx_graph,
            pos,
            all_shortest_paths=all_shortest_paths,
            qnames=qnames,
            edge_weight=edge_weight)
        quality_metrics = {
            **quality_metrics,
            'run_time': run_time.quality()
        }
        trial.set_user_attr('quality_metrics', quality_metrics)

        del params['result']
        del params['edge length property']
        del params['node size']
        trial.set_user_attr('params', params)

        result = tuple([quality_metrics[name] for name in qnames])
        return result
    return objective


def fr_objective(initial_pos, nx_graph, all_shortest_paths, qnames, edge_weight):
    def objective(trial: optuna.Trial):
        k_rate = trial.suggest_float('k_rate', 0.01, 1)
        k = math.ceil(k_rate * len(nx_graph.nodes))
        params = {
            'k_rate': k_rate,
            'k': k,
            'fixed': None,
            'iterations': trial.suggest_int('iterations', 1, 1000),
            'threshold': trial.suggest_float('threshold', 0.00001, 0.001),
            'weight': 'weight',
            'scale': None,
            'center': None,
            'dim': 2,
            'seed': 0,
        }
        run_time = RunTime()

        trial.set_user_attr('params', params)
        del params['k_rate']

        run_time.start()
        pos = fruchterman_reingold(
            nx_graph, initial_pos=initial_pos, params=params)
        run_time.end()

        trial.set_user_attr('pos', pos)

        quality_metrics = calc_qs(
            nx_graph,
            pos,
            all_shortest_paths=all_shortest_paths,
            qnames=qnames,
            edge_weight=edge_weight)
        quality_metrics = {
            **quality_metrics,
            'run_time': run_time.quality()
        }
        trial.set_user_attr('quality_metrics', quality_metrics)

        result = tuple([quality_metrics[name] for name in qnames])
        return result
    return objective


def ss_objective(nx_graph, graph, indices, qnames, all_shortest_paths, edge_weight=1):
    def objective(trial: optuna.Trial):
        number_of_pivots_rate = trial.suggest_float(
            'number_of_pivots_rate', 0.01, 1)
        number_of_pivots = math.ceil(
            number_of_pivots_rate * len(nx_graph.nodes))
        params = {
            'edge_length': edge_weight,
            'number_of_pivots_rate': number_of_pivots_rate,
            'number_of_pivots': number_of_pivots,
            'number_of_iterations': trial.suggest_int('number_of_iterations', 1, 200),
            'eps': trial.suggest_float('eps', 0.01, 1)
        }
        trial.set_user_attr('params', params)
        del params['number_of_pivots_rate']

        run_time = RunTime()

        run_time.start()
        pos = sgd(graph, indices, params, 0)
        run_time.end()

        trial.set_user_attr('pos', pos)

        quality_metrics = calc_qs(
            nx_graph,
            pos,
            all_shortest_paths=all_shortest_paths,
            qnames=qnames,
            edge_weight=edge_weight)
        quality_metrics = {
            **quality_metrics,
            'run_time': run_time.quality()
        }
        trial.set_user_attr('quality_metrics', quality_metrics)

        result = tuple([quality_metrics[name] for name in qnames])
        return result
    return objective


def kk_objective(nx_graph, eg_graph, indices, qnames, all_shortest_paths, edge_weight=1):
    def objective(trial: optuna.Trial):
        params = {
            'edge_length': edge_weight,
            'eps': trial.suggest_float('eps', 0.0001, 1.0)
        }
        run_time = RunTime()

        run_time.start()
        pos = kamada_kawai(eg_graph, indices, params)
        run_time.end()

        quality_metrics = calc_qs(
            nx_graph,
            pos,
            all_shortest_paths=all_shortest_paths,
            qnames=qnames,
            edge_weight=edge_weight)
        quality_metrics = {
            **quality_metrics,
            'run_time': run_time.quality()
        }

        trial.set_user_attr('quality_metrics', quality_metrics)
        trial.set_user_attr('params', params)
        trial.set_user_attr('pos', pos)

        result = tuple([quality_metrics[name] for name in qnames])
        return result
    return objective


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

    dataset_names = sorted([
        '3elt',
        '1138_bus',
        'bull',
        'chvatal',
        'cubical',
        'davis_southern_women',
        'desargues',
        'diamond',
        'dodecahedral',
        'dwt_1005',
        'dwt_2680',
        'florentine_families',
        'frucht',
        'heawood',
        'hoffman_singleton',
        'house_x',
        'house',
        'icosahedral',
        'karate_club',
        'krackhardt_kite',
        'les_miserables',
        'moebius_kantor',
        'octahedral',
        'package',
        'pappus',
        'petersen',
        'poli',
        'qh882',
        'sedgewick_maze',
        'tutte',
        'USpowerGrid',
    ])

    layout_name_abbreviations = [
        'SS',
        'FR',
        'FM3',
        'KK'
    ]

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', choices=dataset_names)

    parser.add_argument('target_qs')

    parser.add_argument('n_trials_per_cpu', type=int)

    parser.add_argument('concurrency', type=int)

    parser.add_argument('layout_name_abbreviation',
                        choices=layout_name_abbreviations)

    args = parser.parse_args()

    if args.layout_name_abbreviation == 'SS':
        layout_name = SS
    elif args.layout_name_abbreviation == 'FR':
        layout_name = FR
    elif args.layout_name_abbreviation == 'FM3':
        layout_name = FM3
    elif args.layout_name_abbreviation == 'KK':
        layout_name = KK

    dataset_name = args.dataset_name
    target_qs = args.target_qs
    n_trials = args.n_trials_per_cpu
    concurrency = args.concurrency

    dataset_path = f'lib/egraph-rs/js/dataset/{dataset_name}.json'
    database_uri = f'sqlite:///db/optimization/{layout_name}/{dataset_name}/{target_qs}.db'
    study_name = f'{target_qs}'

    os.makedirs(
        f'db/optimization/{layout_name}/{dataset_name}/', exist_ok=True)

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

    max_cpu = os.cpu_count()
    assert concurrency <= max_cpu

    workers = [Process(target=optimize, kwargs={
        'dataset_path': dataset_path,
        'qnames': qnames,
        'n_trials': n_trials,
        'database_uri': database_uri,
        'study_name': study_name,
        'layout_name': layout_name,
        'all_qnames': all_qnames,
        'edge_weight': EDGE_WEIGHT
    }) for _ in range(concurrency)]

    for worker in workers:
        worker.start()
        time.sleep(2)
