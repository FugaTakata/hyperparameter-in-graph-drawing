# Standard Library
import argparse
import math
import os
from pprint import pprint
from random import random

# Third Party Library
import matplotlib.pyplot as plt
import networkx as nx
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_name_abbreviations, qm_names
from ex_utils.quality_metrics import time_complexity
from ex_utils.share import (
    draw,
    draw_and_measure,
    draw_and_measure_scaled,
    ex_path,
    generate_seed_median_df,
    generate_sscalers,
    rate2pivots,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

pd.set_option("display.max_columns", None)

EDGE_WEIGHT = 30


def main():
    d_names = [
        "1138_bus",
        "USpowerGrid",
        "dwt_1005",
        "poli",
        "qh882",
        "3elt",
        "dwt_2680",
    ]

    for d_name in d_names:
        n_trials = 200
        a = "max_pivots=0.25n"

        n_compare = 10

        db_uri = (
            f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"
        )
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        study = optuna.load_study(study_name=study_name, storage=db_uri)

        best_trials = []

        for trial in study.best_trials:
            trial_dict = {
                **trial.user_attrs["row_quality_metrics"],
                **trial.user_attrs["params"]
                # trial.user_attrs["quality_metrics_with_time-compexity-penalty"],
            }
            best_trials.append(trial_dict)

        n_split = 10
        data_seeds = list(range(10))
        df_paths = [
            ex_path.joinpath(
                f"data/grid/{d_name}/n={n_split}/seed={data_seed}.pkl"
            )
            for data_seed in data_seeds
        ]
        df = pd.concat([pd.read_pickle(df_path) for df_path in df_paths])
        mdf = generate_seed_median_df(df)
        scalers = generate_sscalers(mdf)

        dataset_path = get_dataset_path(d_name)
        nx_graph = nx_graph_preprocessing(
            load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
        )
        n_nodes = len(nx_graph.nodes)
        n_edges = len(nx_graph.edges)

        eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
        eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)
        p_max = math.ceil(n_nodes * 0.25)

        pivots = 50
        iterations = 100
        eps = 0.1
        # print(pivots, iterations, eps)

        eg_drawing = Drawing.initial_placement(eg_graph)
        pos, e_quality_metrics = draw_and_measure(
            pivots=pivots,
            iterations=iterations,
            eps=eps,
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            eg_drawing=eg_drawing,
            eg_distance_matrix=eg_distance_matrix,
            edge_weight=EDGE_WEIGHT,
            seed=0,
            n_nodes=n_nodes,
            n_edges=n_edges,
        )

        best_df = pd.DataFrame(best_trials)
        best_df["sp"] = False

        c = 0
        threshold = 0.05
        vs = []

        best_df["win_count"] = 0
        best_df["even"] = 0
        best_df["lose_count"] = 0

        rows = list(best_df.query("not sp").iterrows())

        # for best in best_trials:
        for i_w, best_win in rows:
            for i_l, best_lose in rows[i_w:]:
                if i_w == i_l:
                    continue
                result_df_data = []
                for _ in range(n_compare):
                    sqma = {}
                    sqmb = {}
                    weight = {}
                    for qm_name in qm_names:
                        weight[qm_name] = random()
                    weight_sum = sum(weight[qm_name] for qm_name in qm_names)
                    for qm_name in qm_names:
                        weight[qm_name] = weight[qm_name] / weight_sum

                    # qma = best
                    qma = dict(
                        [(qm_name, best_win[qm_name]) for qm_name in qm_names]
                    )
                    qmb = dict(
                        [(qm_name, best_lose[qm_name]) for qm_name in qm_names]
                    )
                    for qm_name in qm_names:
                        sqma[qm_name] = (
                            scalers[qm_name].transform([[qma[qm_name]]])[0][0]
                            * weight[qm_name]
                        )
                        sqmb[qm_name] = (
                            scalers[qm_name].transform([[qmb[qm_name]]])[0][0]
                            * weight[qm_name]
                        )
                    weighted_qma_sum = sum(
                        sqma[qm_name] for qm_name in qm_names
                    )
                    weighted_qmb_sum = sum(
                        sqmb[qm_name] for qm_name in qm_names
                    )
                    result_df_data.append(
                        {
                            # **dict(
                            #     [
                            #         (f"a_{qm_name}", sqma[qm_name])
                            #         for qm_name in qm_names
                            #     ]
                            # ),
                            # **dict(
                            #     [
                            #         (f"b_{qm_name}", sqmb[qm_name])
                            #         for qm_name in qm_names
                            #     ]
                            # ),
                            # **dict(
                            #     [
                            #         (f"weight_{qm_name}", weight[qm_name])
                            #         for qm_name in qm_names
                            #     ]
                            # ),
                            "weighted_qma_sum": weighted_qma_sum,
                            "weighted_qmb_sum": weighted_qmb_sum,
                            # "best_win": best_win,
                            # "best_loser": best_loser,
                        }
                    )

                result_df = (
                    pd.DataFrame(result_df_data)
                    .sort_index(axis=1)
                    .reset_index()
                )

                con_left = (
                    result_df["weighted_qma_sum"]
                    / result_df["weighted_qmb_sum"]
                    < 0.5 - threshold
                )

                con_center = (
                    0.5 - threshold
                    <= result_df["weighted_qma_sum"]
                    / result_df["weighted_qmb_sum"]
                ) & (
                    result_df["weighted_qma_sum"]
                    / result_df["weighted_qmb_sum"]
                    <= 0.5 + threshold
                )

                con_right = (
                    result_df["weighted_qma_sum"]
                    / result_df["weighted_qmb_sum"]
                    > 0.5 - threshold
                )

                ldf = result_df[con_left]
                cdf = result_df[con_center]
                rdf = result_df[con_right]

                if len(adf) / len(result_df) > threshold:
                    best_df.at[i_w, "win_count"] += 1
                    best_df.at[i_l, "lose_count"] += 1

        super_winner = best_df[
            best_df["win_count"] == best_df["win_count"].max()
        ]
        less_lose = best_df[best_df["lose_count"] == 0]

        for i, row in super_winner.iterrows():
            print(d_name, row)
        # display(super_winner)
        # display(less_lose)

        # print("dataset", "gt_count", "n_pareto", "gt_count/all")
        # print(d_name, c, len(best_trials), c / len(best_trials))


if __name__ == "__main__":
    main()
