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
import time
from multiprocessing import Process

# Third Party Library
import networkx as nx
import pandas as pd

# First Party Library
from drawing.sgd import sgd
from quality_metrics.run_time import RunTime
from utils import graph_preprocessing
from utils.calc_quality_metrics import calc_qs
from utils.graph import generate_egraph_graph

SS = "Sparse-SGD"
FR = "Fruchterman-Reingold"
FM3 = "FM3"
KK = "Kamada-Kawai"


def rpfs(dataset_path, export_path, n_params, n_seed, edge_weight=1):
    # グラフのロード
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), edge_weight)
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    all_qnames = [
        "angular_resolution",
        "aspect_ratio",
        "crossing_angle",
        "crossing_number",
        "gabriel_graph_property",
        "ideal_edge_length",
        "node_resolution",
        "run_time",
        "shape_based_metrics",
        "stress",
    ]

    graph, indices = generate_egraph_graph(nx_graph)

    df = pd.DataFrame()

    for i in range(n_params):
        number_of_pivots_rate = random.uniform(0.01, 1)
        number_of_pivots = math.ceil(
            number_of_pivots_rate * len(nx_graph.nodes)
        )
        params = {
            "edge_length": edge_weight,
            "number_of_pivots_rate": number_of_pivots_rate,
            "number_of_pivots": number_of_pivots,
            "number_of_iterations": random.randrange(1, 200 + 1),
            "eps": random.uniform(0.01, 1),
        }

        for s in range(n_seed):
            run_time = RunTime()

            run_time.start()
            pos = sgd(graph, indices, params, s)
            run_time.end()

            quality_metrics = calc_qs(
                nx_graph,
                pos,
                all_shortest_paths=all_shortest_paths,
                qnames=all_qnames,
                edge_weight=edge_weight,
            )
            quality_metrics = {
                **quality_metrics,
                "run_time": run_time.quality(),
            }

            new_df = pd.DataFrame(
                [
                    {
                        "n_params": i,
                        "n_seed": s,
                        "params": params,
                        "pos": pos,
                        "quality_metrics": quality_metrics,
                    }
                ]
            )

            df = pd.concat([df, new_df])
            df.to_pickle(export_path)


if __name__ == "__main__":
    EDGE_WEIGHT = 30

    all_qnames = [
        "angular_resolution",
        "aspect_ratio",
        "crossing_angle",
        "crossing_number",
        "gabriel_graph_property",
        "ideal_edge_length",
        "node_resolution",
        "run_time",
        "shape_based_metrics",
        "stress",
    ]

    dataset_names = sorted(
        [
            "3elt",
            "1138_bus",
            "bull",
            "chvatal",
            "cubical",
            "davis_southern_women",
            "desargues",
            "diamond",
            "dodecahedral",
            "dwt_1005",
            "dwt_2680",
            "florentine_families",
            "frucht",
            "heawood",
            "hoffman_singleton",
            "house_x",
            "house",
            "icosahedral",
            "karate_club",
            "krackhardt_kite",
            "les_miserables",
            "moebius_kantor",
            "octahedral",
            "package",
            "pappus",
            "petersen",
            "poli",
            "qh882",
            "sedgewick_maze",
            "tutte",
            "USpowerGrid",
        ]
    )

    layout_name_abbreviations = ["SS", "FR", "FM3", "KK"]

    parser = argparse.ArgumentParser()

    parser.add_argument("dataset_name", choices=dataset_names)

    parser.add_argument("target_qs")

    parser.add_argument("n_params_per_cpu", type=int)

    parser.add_argument("n_seed", type=int)

    parser.add_argument("concurrency", type=int)

    parser.add_argument(
        "layout_name_abbreviation", choices=layout_name_abbreviations
    )

    args = parser.parse_args()

    if args.layout_name_abbreviation == "SS":
        layout_name = SS
    elif args.layout_name_abbreviation == "FR":
        layout_name = FR
    elif args.layout_name_abbreviation == "FM3":
        layout_name = FM3
    elif args.layout_name_abbreviation == "KK":
        layout_name = KK

    dataset_name = args.dataset_name
    target_qs = args.target_qs
    concurrency = args.concurrency

    dataset_path = f"lib/egraph-rs/js/dataset/{dataset_name}.json"
    export_directory = f"data/n_rpfs/{layout_name}/{dataset_name}"

    os.makedirs(export_directory, exist_ok=True)

    # targetとなるquality metrics名の配列作成
    target_qnames = (
        [qname for qname in all_qnames]
        if target_qs == "all"
        else target_qs.split(",")
    )

    qnames = []
    for tqname in target_qnames:
        if tqname in all_qnames:
            qnames.append(tqname)
        else:
            raise ValueError(f"{tqname} in {target_qnames} is not accepted")
    qnames = sorted(qnames)

    max_cpu = os.cpu_count()
    assert concurrency <= max_cpu

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    workers = [
        Process(
            target=rpfs,
            kwargs={
                "dataset_path": dataset_path,
                "export_path": f"{export_directory}/{now}-{i}.pkl",
                "n_params": args.n_params_per_cpu,
                "n_seed": args.n_seed,
                "edge_weight": EDGE_WEIGHT,
            },
        )
        for i in range(concurrency)
    ]

    for worker in workers:
        worker.start()
        time.sleep(2)

