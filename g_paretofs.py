"""
SparseSgdのパラメータ最適化実験
"""
# Standard Library
import argparse
import json
import os
import random
import uuid

# Third Party Library
import networkx as nx
import optuna
import pandas as pd

# First Party Library
from drawing.sgd import sgd
from quality_metrics import (
    angular_resolution,
    aspect_ratio,
    crossing_angle,
    crossing_number,
    gabriel_graph_property,
    ideal_edge_length,
    node_resolution,
    shape_based_metrics,
    stress,
)
from utils.calc_quality_metrics import calc_qs
from utils.dataset import dataset_names
from utils.graph import generate_egraph_graph, graph_preprocessing

SS = "SS"

QUALITY_METRICS = {
    "angular_resolution": angular_resolution,
    "aspect_ratio": aspect_ratio,
    "crossing_angle": crossing_angle,
    "crossing_number": crossing_number,
    "gabriel_graph_property": gabriel_graph_property,
    "ideal_edge_length": ideal_edge_length,
    "node_resolution": node_resolution,
    "shape_based_metrics": shape_based_metrics,
    "stress": stress,
}

ALL_QUALITY_METRICS_NAMES = sorted([name for name in QUALITY_METRICS])
RAND_MAX = 2**32


def save(
    export_path, targets, seed, params, pos, quality_metrics, trial_number
):
    base_df = pd.DataFrame()
    if os.path.exists(export_path):
        base_df = pd.read_pickle(export_path)

    new_df = pd.DataFrame(
        [
            {
                "targets": targets,
                "seed": seed,
                "params": params,
                "pos": pos,
                "quality_metrics": quality_metrics,
                "trial_number": trial_number,
            }
        ]
    )

    df = pd.concat([base_df, new_df])
    df.to_pickle(export_path)


def parse_args():
    layout_name_abbreviations = [SS]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument(
        "-t",
        choices=ALL_QUALITY_METRICS_NAMES,
        nargs="*",
        required=True,
        help="target quality metrics names",
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
    L = args.l
    D = args.d

    dataset_path = f"lib/egraph-rs/js/dataset/{D}.json"

    export_directory = f"data/paretofs/{L}/{D}"
    export_path = f"{export_directory}/{','.join(args.t)}.pkl"
    os.makedirs(export_directory, exist_ok=True)

    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    all_pairs_shortest_path_length = dict(
        nx.all_pairs_dijkstra_path_length(nx_graph)
    )
    graph, indices = generate_egraph_graph(nx_graph)

    study_name = ",".join(args.t)
    storage_path = f"sqlite:///db_opt/{L}/{D}/{study_name}.db"
    study = optuna.load_study(storage=storage_path, study_name=study_name)

    for best_trial in study.best_trials:
        params = best_trial.user_attrs["params"]
        seed = random.randint(0, RAND_MAX)
        print(best_trial.number, seed)

        pos = sgd(graph=graph, indices=indices, params=params, seed=seed)

        quality_metrics = calc_qs(
            nx_graph=nx_graph,
            pos=pos,
            all_pairs_shortest_path_length=all_pairs_shortest_path_length,
            target_quality_metrics_names=ALL_QUALITY_METRICS_NAMES,
            edge_weight=EDGE_WEIGHT,
        )

        save(
            export_path=export_path,
            targets=args.t,
            seed=seed,
            params=params,
            pos=pos,
            quality_metrics=quality_metrics,
            trial_number=best_trial.number,
        )
