'''
上限下限の探索用
'''

import json
import argparse
import os
import math

from tulip import tlp


import pandas as pd
import networkx as nx

from utils.graph import load_nx_graph, generate_egraph_graph, generate_tulip_graph
from utils.calc_quality_metrics import calc_qs
from quality_metrics.run_time import RunTime
from drawing.sgd import sgd
from drawing.fruchterman_reingold import fruchterman_reingold
from drawing.fm3 import fm3
from drawing.kamada_kawai import kamada_kawai

SS = 'Sparse-SGD'
FR = 'Fruchterman-Reingold'
FM3 = 'FM3'
KK = 'Kamada-Kawai'


def save_df(dataset_name,
            layout_name,
            params,
            target_params_name,
            quality_metrics,
            pos,
            result_df,
            result_df_columns,
            export_path):
    df = pd.DataFrame(data=[[
        dataset_name,
        layout_name,
        params,
        target_params_name,
        quality_metrics,
        pos
    ]], columns=result_df_columns)

    result_df = pd.concat([result_df, df])
    result_df.to_pickle(export_path)

    return result_df


def search_params(layout_name, dataset_name, nx_graph: nx.Graph, all_pairs_path_length, quality_metrics_names, export_path, edge_weight=1):
    result_df_columns = ['graph',
                         'layout',
                         'params',
                         'target_params',
                         'quality_metrics',
                         'pos']
    result_df = pd.DataFrame(
        columns=result_df_columns)

    candidates_path = f'data/params/search/candidates/{layout_name}.json'
    with open(candidates_path) as f:
        candidates = json.load(f)

    run_time = RunTime()

    if layout_name == SS:
        base_params = {
            'edge_length': 30,
            'number_of_pivots_rate': 0.5,
            'number_of_iterations': 100,
            'eps': 0.1
        }
        target_params_names = [
            'number_of_pivots_rate',
            'number_of_iterations',
            'eps'
        ]

        eg_graph, indices = generate_egraph_graph(nx_graph)

        for target_params_name in target_params_names:
            for candidate in candidates[target_params_name]:
                print(f'{target_params_name}={candidate}')
                number_of_pivots_rate = candidate if target_params_name == 'number_of_pivots_rate' else base_params[
                    'number_of_pivots_rate']
                number_of_pivots = math.ceil(
                    number_of_pivots_rate * len(nx_graph.nodes))
                params = {
                    **base_params,
                    'number_of_pivots': number_of_pivots,
                    'number_of_pivots_rate': number_of_pivots_rate,
                    target_params_name: candidate
                }

                run_time.start()
                pos = sgd(eg_graph, indices, params, 0)
                run_time.end()

                quality_metrics = calc_qs(
                    nx_graph,
                    pos,
                    all_shortest_paths=all_pairs_path_length,
                    qnames=quality_metrics_names,
                    edge_weight=edge_weight)
                quality_metrics = {
                    **quality_metrics,
                    'run_time': run_time.quality()
                }

                result_df = save_df(dataset_name=dataset_name,
                                    layout_name=layout_name,
                                    params=params,
                                    target_params_name=target_params_name,
                                    quality_metrics=quality_metrics,
                                    pos=pos,
                                    result_df=result_df,
                                    result_df_columns=result_df_columns,
                                    export_path=export_path)
    elif layout_name == FR:
        base_params = {
            'k_rate': 0.5,
            'fixed': None,
            'iterations': 50,
            'threshold': 0.0001,
            'weight': 'weight',
            'scale': None,
            'center': None,
            'dim': 2,
            'seed': 0,
        }
        target_params_names = [
            'iterations',
            'threshold',
            'k_rate'
        ]

        initial_pos = nx.random_layout(nx_graph, seed=0)
        for target_params_name in target_params_names:
            for candidate in candidates[target_params_name]:
                print(f'{target_params_name}={candidate}')
                k_rate = candidate if target_params_name == 'k_rate' else base_params['k_rate']
                k = k_rate * len(nx_graph.nodes)
                params = {
                    **base_params,
                    'k': k,
                    'k_rate': k_rate,
                    target_params_name: candidate
                }

                run_time.start()
                pos = fruchterman_reingold(
                    nx_graph, initial_pos=initial_pos, params=params)
                run_time.end()

                quality_metrics = calc_qs(
                    nx_graph,
                    pos,
                    all_shortest_paths=all_pairs_path_length,
                    qnames=quality_metrics_names,
                    edge_weight=edge_weight)
                quality_metrics = {
                    **quality_metrics,
                    'run_time': run_time.quality()
                }

                result_df = save_df(dataset_name=dataset_name,
                                    layout_name=layout_name,
                                    params=params,
                                    target_params_name=target_params_name,
                                    quality_metrics=quality_metrics,
                                    pos=pos,
                                    result_df=result_df,
                                    result_df_columns=result_df_columns,
                                    export_path=export_path)
    elif layout_name == FM3:
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
        target_params_names = [
            'fixed iterations',
            'threshold',
            'page format',
        ]

        tlp_graph = generate_tulip_graph(nx_graph)
        for target_params_name in target_params_names:
            for candidate in candidates[target_params_name]:
                print(f'{target_params_name}={candidate}')
                params = {
                    **tlp.getDefaultPluginParameters(tlp_layout_name, tlp_graph),
                    **base_params,
                    target_params_name: candidate
                }

                run_time.start()
                pos = fm3(tlp_graph, params)
                run_time.end()

                quality_metrics = calc_qs(
                    nx_graph,
                    pos,
                    all_shortest_paths=all_pairs_path_length,
                    qnames=quality_metrics_names,
                    edge_weight=edge_weight)
                quality_metrics = {
                    **quality_metrics,
                    'run_time': run_time.quality()
                }

                del params['result']
                del params['edge length property']
                del params['node size']

                result_df = save_df(dataset_name=dataset_name,
                                    layout_name=layout_name,
                                    params=params,
                                    target_params_name=target_params_name,
                                    quality_metrics=quality_metrics,
                                    pos=pos,
                                    result_df=result_df,
                                    result_df_columns=result_df_columns,
                                    export_path=export_path)
    elif layout_name == KK:
        target_params_names = [
            'eps'
        ]
        base_params = {
            'edge_length': edge_weight,
            'eps': 0.001
        }

        eg_graph, indices = generate_egraph_graph(nx_graph)
        for target_params_name in target_params_names:
            for candidate in candidates[target_params_name]:
                print(f'{target_params_name}={candidate}')
                params = {
                    **base_params,
                    target_params_name: candidate
                }

                run_time.start()
                pos = kamada_kawai(eg_graph, indices, params)
                run_time.end()

                quality_metrics = calc_qs(
                    nx_graph,
                    pos,
                    all_shortest_paths=all_pairs_path_length,
                    qnames=quality_metrics_names,
                    edge_weight=edge_weight)
                quality_metrics = {
                    **quality_metrics,
                    'run_time': run_time.quality()
                }

                result_df = save_df(dataset_name=dataset_name,
                                    layout_name=layout_name,
                                    params=params,
                                    target_params_name=target_params_name,
                                    quality_metrics=quality_metrics,
                                    pos=pos,
                                    result_df=result_df,
                                    result_df_columns=result_df_columns,
                                    export_path=export_path)


if __name__ == '__main__':
    EDGE_WEIGHT = 30

    quality_metrics_names = sorted([
        'angular_resolution',
        'aspect_ratio',
        'crossing_angle',
        'crossing_number',
        'gabriel_graph_property',
        'ideal_edge_length',
        'node_resolution',
        'shape_based_metrics',
        'stress'
    ])

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

    # args = parse_args()
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', choices=dataset_names)
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

    dataset_path = f'lib/egraph-rs/js/dataset/{args.dataset_name}.json'
    export_path = f'data/params/search/results/{layout_name}/{args.dataset_name}.pkl'

    # prepare directories
    os.makedirs(
        f'data/params/search/results/{layout_name}', exist_ok=True)

    # load graph
    nx_graph = load_nx_graph(dataset_path=dataset_path,
                             edge_weight=EDGE_WEIGHT)

    # all_pairs_path_length
    all_pairs_path_length = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    search_params(layout_name,
                  args.dataset_name,
                  nx_graph,
                  all_pairs_path_length=all_pairs_path_length,
                  quality_metrics_names=quality_metrics_names,
                  export_path=export_path,
                  edge_weight=EDGE_WEIGHT)
