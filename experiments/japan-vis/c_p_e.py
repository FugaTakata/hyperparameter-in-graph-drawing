# Standard Library
import argparse
import math
import os
from pprint import pprint
from random import random

# Third Party Library
import matplotlib.pyplot as plt
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_name_abbreviations, qm_names
from ex_utils.quality_metrics import time_complexity
from ex_utils.share import (
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
    print("dataset", "gt_empirical", "n_pareto", "gt_empirical/all")

    for d_name in d_names:
        n_trials = 300
        a = "max_pivots=0.25n"
        EDGE_WEIGHT = 30

        n_compare = 100

        db_uri = (
            f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"
        )
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        study = optuna.load_study(study_name=study_name, storage=db_uri)

        best_trials = []
        sorted_quality_metrics = dict((qm_name, []) for qm_name in qm_names)

        for trial in study.best_trials:
            trial_dict = {
                **trial.user_attrs["row_quality_metrics"],
                # **trial.user_attrs["quality_metrics_with_time-compexity-penalty"],
                **trial.params,
            }
            best_trials.append(trial_dict)

            for qm_name in qm_names:
                sorted_quality_metrics[qm_name].append(trial_dict[qm_name])

        for qm_name in qm_names:
            sorted_quality_metrics[qm_name] = sorted(
                sorted_quality_metrics[qm_name]
            )

        for trial in best_trials:
            for qm_name in qm_names:
                trial[f"{qm_name}_asc_order"] = sorted_quality_metrics[
                    qm_name
                ].index(trial[qm_name])
            trial["order_sum"] = 0
            # trial["pref_order_sum"] = 0
            for qm_name in qm_names:
                trial["order_sum"] += trial[f"{qm_name}_asc_order"]
                # trial["pref_order_sum"] += (
                #     trial[f"{qm_name}_asc_order"] * pref[qm_name]
                # )
        best_trials = sorted(
            best_trials, key=lambda x: x["order_sum"], reverse=True
        )

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

        vs = []
        # for best in best_trials:
        for i, best in best_df.query("not sp").iterrows():
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
                qma = dict([(qm_name, best[qm_name]) for qm_name in qm_names])
                qmb = e_quality_metrics
                for qm_name in qm_names:
                    sqma[qm_name] = (
                        scalers[qm_name].transform([[qma[qm_name]]])[0][0]
                        * weight[qm_name]
                    )
                    sqmb[qm_name] = (
                        scalers[qm_name].transform([[qmb[qm_name]]])[0][0]
                        * weight[qm_name]
                    )
                weighted_qma_sum = sum(sqma[qm_name] for qm_name in qm_names)
                weighted_qmb_sum = sum(sqmb[qm_name] for qm_name in qm_names)
                result_df_data.append(
                    {
                        **dict(
                            [
                                (f"a_{qm_name}", sqma[qm_name])
                                for qm_name in qm_names
                            ]
                        ),
                        **dict(
                            [
                                (f"b_{qm_name}", sqmb[qm_name])
                                for qm_name in qm_names
                            ]
                        ),
                        **dict(
                            [
                                (f"weight_{qm_name}", weight[qm_name])
                                for qm_name in qm_names
                            ]
                        ),
                        "weighted_qma_sum": weighted_qma_sum,
                        "weighted_qmb_sum": weighted_qmb_sum,
                        "best": best,
                    }
                )

            result_df = (
                pd.DataFrame(result_df_data).sort_index(axis=1).reset_index()
            )

            con = result_df["weighted_qmb_sum"] < result_df["weighted_qma_sum"]
            adf = result_df[con]
            bdf = result_df[~con]

            if len(adf) > len(bdf):
                c += 1
            vs.append(len(adf) / len(result_df))

        print(d_name, c, len(best_trials), c / len(best_trials))


if __name__ == "__main__":
    main()
