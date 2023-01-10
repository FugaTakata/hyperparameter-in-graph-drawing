# Standard Library
import argparse
import json
import os

# Third Party Library
import networkx as nx
import optuna

# First Party Library
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
from utils.dataset import dataset_names
from utils.graph import graph_preprocessing
from utils.objective import fr_objective, ss_objective

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
    parser.add_argument("-n", type=int, required=True, help="n trials")
    parser.add_argument(
        "-l",
        choices=layout_name_abbreviations,
        required=True,
        help="layout name",
    )
    parser.add_argument(
        "-t",
        choices=ALL_QUALITY_METRICS_NAMES,
        nargs="*",
        required=True,
        help="target quality metrics names",
    )

    args = parser.parse_args()

    return args


def optimize(
    database_uri,
    study_name,
    layout_name,
    edge_weight,
    n_trials,
    target_quality_metrics_names,
):
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), edge_weight)
    all_pairs_shortest_path_length = dict(
        nx.all_pairs_dijkstra_path_length(nx_graph)
    )

    study = optuna.create_study(
        directions=[
            QUALITY_METRICS[name].direction
            for name in target_quality_metrics_names
        ],
        storage=database_uri,
        study_name=study_name,
        load_if_exists=True,
    )

    if layout_name == SS:
        study.optimize(
            ss_objective(
                nx_graph=nx_graph,
                all_pairs_shortest_path_length=all_pairs_shortest_path_length,
                target_quality_metrics_names=target_quality_metrics_names,
                all_quality_metrics_names=ALL_QUALITY_METRICS_NAMES,
                edge_weight=edge_weight,
            ),
            n_trials=n_trials,
            show_progress_bar=True,
        )
    elif layout_name == FR:
        study.optimize(
            fr_objective(
                nx_graph=nx_graph,
                all_pairs_shortest_path_length=all_pairs_shortest_path_length,
                target_quality_metrics_names=target_quality_metrics_names,
                all_quality_metrics_names=ALL_QUALITY_METRICS_NAMES,
                edge_weight=edge_weight,
            ),
            n_trials=n_trials,
            show_progress_bar=True,
        )


if __name__ == "__main__":
    EDGE_WEIGHT = 30

    args = parse_args()

    dataset_path = f"lib/egraph-rs/js/dataset/{args.d}.json"

    database_directory = f"db/opt/{args.l}/{args.d}"
    study_name = f"{','.join(args.t)}"
    database_uri = f"sqlite:///{database_directory}/{study_name}.db"
    os.makedirs(database_directory, exist_ok=True)

    optimize(
        database_uri=database_uri,
        study_name=study_name,
        layout_name=args.l,
        edge_weight=EDGE_WEIGHT,
        n_trials=args.n,
        target_quality_metrics_names=sorted(args.t),
    )
