'''
SparseSgdのparamsの範囲を決めるための実験
対象パラメータは
number_of_pivots
number_of_iterations
eps
'''

import json
import argparse
import time

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

    # target parameter
    parser.add_argument('target_params')

    args = parser.parse_args()

    return args


def main():
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

    base_params = {
        'edge_length': 30,
        'number_of_pivots': 50,
        'number_of_iterations': 100,
        'eps': 0.1
    }

    params_names = ['number_of_pivots', 'number_of_iterations', 'eps']

    args = parse_args()
    dataset_name = args.dataset_name
    target_qs = args.target_qs
    target_params = args.target_params

    if target_params not in params_names:
        raise ValueError(f'{target_params} is not allowed')

    dataset_path = f'lib/egraph-rs/js/dataset/{dataset_name}.json'
    export_path = f'data/explore_limitation/{dataset_name}/{target_qs}_{target_params}.json'

    with open(export_path, mode='a'):
        pass

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

    export_data = {}
    export_data[target_params] = {}

    with open('data/explore_limitation/USpowerGrid/old.json') as f:
        old_data = json.load(f)

    for pc in old_data[target_params]:
        d = old_data[target_params][pc]
        pos = d['pos']
        params = d['params']

        start = time.time()
        print('hello')

        qs = calc_qs(nx_graph, pos, all_shortest_paths,
                     qnames, edge_weight=EDGE_WEIGHT)
        print(time.time() - start)

        export_data[target_params][pc] = {
            'params': params, 'quality_metrics': qs, 'pos': pos}

    with open(export_path, mode='w') as f:
        json.dump(export_data, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
