"""
SparseSgdのパラメータ最適化実験
"""
# Standard Library
import argparse
import datetime
import json
import math
import os
import random
import sys
import uuid

# Third Party Library
import networkx as nx
import pandas as pd

# First Party Library
from drawing.fruchterman_reingold import fruchterman_reingold
from drawing.sgd import sgd
from quality_metrics import (
    angular_resolution,
    aspect_ratio,
    crossing_angle,
    crossing_number,
    gabriel_graph_property,
    ideal_edge_length,
    node_resolution,
    run_time,
    shape_based_metrics,
    stress,
)
from quality_metrics.run_time import RunTime
from utils.calc_quality_metrics import calc_qs
from utils.dataset import dataset_names
from utils.graph import generate_egraph_graph, graph_preprocessing

SS = "SS"
FR = "FR"
FM3 = "FM3"
KK = "KK"

QUALITY_METRICS = {
    "angular_resolution": angular_resolution,
    "aspect_ratio": aspect_ratio,
    "crossing_angle": crossing_angle,
    "crossing_number": crossing_number,
    "gabriel_graph_property": gabriel_graph_property,
    "ideal_edge_length": ideal_edge_length,
    "node_resolution": node_resolution,
    "run_time": run_time,
    "shape_based_metrics": shape_based_metrics,
    "stress": stress,
}

ALL_QUALITY_METRICS_NAMES = sorted([name for name in QUALITY_METRICS])


def save(
    base_df,
    export_path,
    pid,
    n_seed,
    params,
    pos,
    quality_metrics,
):
    new_df = pd.DataFrame(
        [
            {
                "pid": pid,
                "n_seed": n_seed,
                "params": params,
                "pos": pos,
                "quality_metrics": quality_metrics,
            }
        ]
    )

    df = pd.concat([base_df, new_df])
    df.to_pickle(export_path)

    return df


def parse_args():
    layout_name_abbreviations = [
        SS,
        FR,
        FM3,
        KK,
    ]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-f", required=True, help="data path")
    parser.add_argument(
        "-l",
        choices=layout_name_abbreviations,
        required=True,
        help="layout name",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    EDGE_WEIGHT = 30

    args = parse_args()

    dataset_path = f"lib/egraph-rs/js/dataset/{args.d}.json"

    export_directory = f"data/n_rpfs/{args.l}/{args.d}"
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_path = f"{export_directory}/{now}.pkl"
    os.makedirs(export_directory, exist_ok=True)

    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    all_pairs_shortest_path_length = dict(
        nx.all_pairs_dijkstra_path_length(nx_graph)
    )

    df = pd.DataFrame()

    data_df = pd.read_pickle(args.f)

    if args.l == SS:
        graph, indices = generate_egraph_graph(nx_graph)

        for i, v in data_df.iterrows():
            params = v.params
            quality_metrics = v.quality_metrics
            n_seed = v.n_seed
            b_pos = v.pos
            n_params = v.n_params

            rt = RunTime()

            rt.start()
            pos = sgd(graph, indices, params, n_seed)
            rt.end()

            print("before", quality_metrics["run_time"])

            quality_metrics = {
                **quality_metrics,
                "run_time": rt.quality(),
            }
            print("after", quality_metrics["run_time"])
            df = save(
                base_df=df,
                export_path=export_path,
                pid=n_params,
                n_seed=n_seed,
                params=params,
                pos=pos,
                quality_metrics=quality_metrics,
            )

    elif args.l == FR:
        for i, v in data_df.iterrows():
            pid = v.pid
            params = v.params
            n_seed = v.n_seed
            b_pos = v.pos
            quality_metrics = v.quality_metrics

            print(pid, n_seed)

            rt = RunTime()

            rt.start()
            pos = fruchterman_reingold(nx_graph=nx_graph, params=params)
            rt.end()

            print("before", quality_metrics["run_time"])

            quality_metrics = {
                **quality_metrics,
                "run_time": rt.quality(),
            }
            print("after", quality_metrics["run_time"])

            for key in pos:
                if pos[key] != b_pos[key]:
                    print(key, pos[key], b_pos[key], "pos changed")
                    sys.exit()

            df = save(
                base_df=df,
                export_path=export_path,
                pid=pid,
                n_seed=n_seed,
                params=params,
                pos=pos,
                quality_metrics=quality_metrics,
            )
