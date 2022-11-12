'''
SparseSgdのopfs作成
'''

import os
import json
import argparse
import time
import datetime
import random

import networkx as nx

from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph, edge_crossing_finder
from quality_metrics import angular_resolution, aspect_ratio, crossing_angle, crossing_number, gabriel_graph_property, ideal_edge_length, node_resolution, shape_based_metrics, stress


def calc_qs(nx_graph, pos, all_shortest_paths, qnames, edge_weight=1):
    start = time.time()
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

    print(time.time() - start)
    return result


def parse_args():
    # lib/egraph-rs/js/dataset/{dataset_name}.json
    # data/optimization/{dataset_name}/{target_qs}.json
    parser = argparse.ArgumentParser()
    # USpowerGrid
    parser.add_argument('dataset_name')

    # node_resolution,stress or all
    parser.add_argument('target_qs')

    # seed数
    parser.add_argument('n_seed')

    # 対象ファイル名
    # q=all_n_trials=100_d=2022-11-10_14-17-37
    parser.add_argument('target_opt_filename')

    # パレート最適化のパラメータのうちqが最大のものを用いる
    # カンマ区切りでqsを入力 or all
    # angular_resolution,aspect_ratio
    parser.add_argument('target_pareto_qs')

    args = parser.parse_args()

    return args


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
        'shape_based_metrics',
        'stress'
    ]

    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    args = parse_args()
    dataset_name = args.dataset_name
    target_qs = args.target_qs
    n_seed = int(args.n_seed)
    target_opt_filename = args.target_opt_filename
    target_pareto_qs = args.target_pareto_qs

    dataset_path = f'lib/egraph-rs/js/dataset/{dataset_name}.json'
    export_path = f'data/opfs/{dataset_name}/q={target_qs}_seed={n_seed}_d={now}.json'
    target_opt_path = f'data/optimization/{dataset_name}/{target_opt_filename}.json'

    # 出力ファイルの有無確認
    with open(export_path, mode='a'):
        pass

    # targetとなるquality metrics名の配列作成
    target_qnames = [
        qname for qname in all_qnames] if target_qs == 'all' else target_qs.split(',')

    # targetとなるquality metrics名の配列作成
    target_pareto_qnames = [
        qname for qname in all_qnames] if target_pareto_qs == 'all' else target_pareto_qs.split(',')

    # targetとなる最適化済みparamsデータ取得
    with open(target_opt_path) as f:
        opt_data = json.load(f)

    inf = float('inf')
    max_pareto_params = {
        'angular_resolution': {'quality': -inf},
        'aspect_ratio': {'quality': -inf},
        'crossing_angle': {'quality': inf},
        'crossing_number': {'quality': inf},
        'gabriel_graph_property': {'quality': -inf},
        'ideal_edge_length': {'quality': inf},
        'node_resolution': {'quality': -inf},
        'shape_based_metrics': {'quality': -inf},
        'stress': {'quality': inf}
    }

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

    opt_params = []
    for best_num in opt_data['best_trial_numbers']:
        trial = opt_data['trials'][best_num]
        qs = trial['quality']
        pos = trial['pos']
        params = trial['params']
        seed = 0

        for tpq in target_pareto_qnames:
            q = qs[tpq]
            if qmap[tpq] == 'maximize':
                if max_pareto_params[tpq] < q:
                    max_pareto_params[tpq] = {
                        'params': params, 'quality': qs, 'seed': seed, 'pos': pos
                    }
            elif qmap[tpq] == 'minimize':
                if q < max_pareto_params[tpq]:
                    max_pareto_params[tpq] = {
                        'params': params, 'quality': qs, 'seed': seed, 'pos': pos
                    }

    qnames = []
    for tqname in target_qnames:
        if tqname in all_qnames:
            qnames.append(tqname)
        else:
            raise ValueError(f'{tqname} in {target_qnames} is not accepted')
    qnames = sorted(qnames)

    # グラフのロード
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    graph, indices = generate_graph_from_nx_graph(nx_graph)
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    # 出力作成
    max_size = 0.9 * 10 ** 8
    # ファイルサイズが100MBを超えないようにする
    while os.path.getsize(export_path) < max_size:
        params = {
            'edge_length': EDGE_WEIGHT,
            'number_of_pivots': random.randint(1, len(nx_graph.nodes)),
            'number_of_iterations': random.randint(1, 200),
            'eps': random.uniform(0.01, 1)
        }
        export_data = {
            'params': params,
            'data': []
        }

        for _ in range(n_seed):
            seed = random.randint(0, 10000)

            pos = draw_graph(graph, indices, params, seed)
            quality = calc_qs(nx_graph, pos, all_shortest_paths,
                              qnames, edge_weight=EDGE_WEIGHT)
            export_data['data'].append({
                'seed': seed,
                'quality': quality,
                'pos': pos
            })

        with open(export_path, mode='a') as f:
            f.write(json.dumps(export_data, ensure_ascii=False) + "\n")
