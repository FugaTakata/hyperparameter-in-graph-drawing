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
import uuid

# Third Party Library
import networkx as nx
import pandas as pd

# First Party Library
from drawing.fm3 import fm3
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
from utils.graph import (
    generate_egraph_graph,
    generate_tulip_graph,
    graph_preprocessing,
)

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
    target,
    n_seed,
    params,
    pos,
    quality_metrics,
):
    new_df = pd.DataFrame(
        [
            {
                "target": target,
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
    parser.add_argument(
        "--seed-from", type=int, required=True, help="n seed from. n <= s"
    )
    parser.add_argument(
        "--seed-to", type=int, required=True, help="n seed to. s <= t"
    )
    parser.add_argument(
        "-t",
        choices=ALL_QUALITY_METRICS_NAMES,
        required=True,
        help="target quality metrics name",
    )
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

    export_directory = f"data/n_opfs/{args.l}/{args.d}"
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_path = f"{export_directory}/{args.t}.pkl"
    os.makedirs(export_directory, exist_ok=True)

    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    all_pairs_shortest_path_length = dict(
        nx.all_pairs_dijkstra_path_length(nx_graph)
    )

    data_df = pd.read_pickle(f"data/params/{args.l}/{args.d}/opt.pkl")
    target_df = data_df[data_df["target"] == args.t]
    df = pd.DataFrame()

    if args.l == SS:
        graph, indices = generate_egraph_graph(nx_graph)

        params = target_df.params[0]

        for s in range(args.seed_from, args.seed_to + 1):
            print(args.t, s)
            rt = RunTime()

            rt.start()
            pos = sgd(graph, indices, params, s)
            rt.end()

            quality_metrics = calc_qs(
                nx_graph=nx_graph,
                pos=pos,
                all_pairs_shortest_path_length=all_pairs_shortest_path_length,
                target_quality_metrics_names=ALL_QUALITY_METRICS_NAMES,
                edge_weight=EDGE_WEIGHT,
            )
            quality_metrics = {
                **quality_metrics,
                "run_time": rt.quality(),
            }

            df = save(
                base_df=df,
                export_path=export_path,
                target=args.t,
                n_seed=s,
                params=params,
                pos=pos,
                quality_metrics=quality_metrics,
            )
    if args.l == FR:
        params = target_df.params[0]
        params = {**params, "pos": None}

        for s in range(args.seed_from, args.seed_to + 1):
            params = {**params, "seed": s}

            rt = RunTime()

            rt.start()
            print(params["seed"])
            pos = fruchterman_reingold(
                nx_graph=nx_graph,
                params=params,
            )
            rt.end()

            quality_metrics = calc_qs(
                nx_graph=nx_graph,
                pos=pos,
                all_pairs_shortest_path_length=all_pairs_shortest_path_length,
                target_quality_metrics_names=ALL_QUALITY_METRICS_NAMES,
                edge_weight=EDGE_WEIGHT,
            )
            quality_metrics = {
                **quality_metrics,
                "run_time": rt.quality(),
            }

            df = save(
                base_df=df,
                export_path=export_path,
                target=args.t,
                n_seed=s,
                params=params,
                pos=pos,
                quality_metrics=quality_metrics,
            )
