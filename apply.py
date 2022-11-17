'''
SparseSgdの最適化済みパラメータのfs作成
'''

import datetime
import random
import json
import argparse

import networkx as nx

from utils import graph_preprocessing, generate_graph_from_nx_graph, draw_graph, edge_crossing_finder
from quality_metrics import angular_resolution, aspect_ratio, crossing_angle, crossing_number, gabriel_graph_property, ideal_edge_length, node_resolution, run_time, shape_based_metrics, stress


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

    # seed数
    parser.add_argument('n_seed')

    # どの評価指標のopfsか？
    # stress
    parser.add_argument('target_quality')

    # 入力paramsのデータセット名
    parser.add_argument('apply_dataset')

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
        'run_time',
        'shape_based_metrics',
        'stress',
    ]

    args = parse_args()
    dataset_name = args.dataset_name
    target_qs = args.target_qs
    n_seed = int(args.n_seed)
    target_quality = args.target_quality
    apply_dataset = args.apply_dataset

    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    dataset_path = f'lib/egraph-rs/js/dataset/{dataset_name}.json'
    export_path = f'data/apply/{dataset_name}/q={target_qs}_seed={n_seed}_target_quality={target_quality}.json'

    # get_best_trial_params.ipynbで作成
    with open(f'data/optimized_params/{apply_dataset}/params.json') as f:
        opt_params = json.load(f)

    # export確認
    with open(export_path, mode='a') as f:
        pass

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

    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    graph, indices = generate_graph_from_nx_graph(nx_graph)
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    export_data = {
        'date': now,
        'data': {}
    }

    for target_q in opt_params:
        if target_q != target_quality:
            continue

        params = opt_params[target_q]
        export_data['data'][target_q] = {
            'params': params,
            'data': []
        }
        for _ in range(n_seed):
            seed = random.randint(0, 10000)
            print(_, seed)

            rt = run_time.RunTime()
            rt.start()
            pos = draw_graph(graph, indices, params, seed)
            rt.end()

            quality_metrics = calc_qs(
                nx_graph, pos, all_shortest_paths, qnames, EDGE_WEIGHT)
            quality_metrics = {
                **quality_metrics,
                'run_time': rt.quality()
            }

            export_data['data'][target_q]['data'].append({
                'seed': seed,
                'quality': quality_metrics,
                'pos': pos
            })

            with open(export_path, mode='w') as f:
                f.write(json.dumps(export_data, ensure_ascii=False) + "\n")
