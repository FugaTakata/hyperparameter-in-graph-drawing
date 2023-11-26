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

threshold = 0.05
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
    print(
        "dataset",
        "best",
        "even",
        "empirical",
        "best/(all - even)",
    )
    for d_name in d_names:
        n_trials = 100
        aas = [
            "pref=1.0,2.0,1.0,1.0,2.0,2.0,2.0,1.0,2.0,3.0",
            "pref=1.0,2.0,1.0,1.0,2.0,2.0,2.0,1.0,2.0,3.0",
            "pref=1.0,1.0,2.0,2.0,1.0,1.0,3.0,1.0,2.0,1.0",
            "pref=10.0,5.0,10.0,10.0,5.0,5.0,20.0,5.0,15.0,15.0",
            "pref=10.0,10.0,15.0,10.0,5.0,10.0,20.0,5.0,15.0,15.0",
            "pref=5.0,5.0,5.0,20.0,5.0,20.0,40.0,5.0,30.0,3.0",
        ]
        a = aas[5]

        n_compare = 200
        db_uri = (
            f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"
        )
        study_name = f"{d_name}_n-trials={n_trials}_sscaled-sum_{a}"
        study = optuna.load_study(study_name=study_name, storage=db_uri)

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

        best_trial = study.best_trial

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

            qma = best_trial.user_attrs["row_quality_metrics"]
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
                    # "best": best_trial,
                }
            )

        result_df = (
            pd.DataFrame(result_df_data).sort_index(axis=1).reset_index()
        )

        con_left = (
            result_df["weighted_qma_sum"] / result_df["weighted_qmb_sum"] < 0.5
        )

        con_center = (
            result_df["weighted_qma_sum"] / result_df["weighted_qmb_sum"]
            == 0.5
        )

        con_right = (
            result_df["weighted_qma_sum"] / result_df["weighted_qmb_sum"] > 0.5
        )

        ldf = result_df[con_left]
        cdf = result_df[con_center]
        rdf = result_df[con_right]

        # print(best_trial.params)
        print(
            d_name,
            len(rdf),
            len(cdf),
            len(ldf),
            len(rdf) / (len(result_df)),
        )

        pivots = best_trial.user_attrs["params"]["pivots"]
        iterations = best_trial.user_attrs["params"]["iterations"]
        eps = best_trial.user_attrs["params"]["eps"]
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

        fig, ax = plt.subplots(dpi=300, facecolor="white")
        ax.set_aspect("equal")

        # ax.set_title(
        #     f"""{d_name} pivots={pivots},iter={iterations},eps={round(eps, 4)}"""
        # )
        # fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
        fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

        nx.draw(
            nx_graph,
            pos=pos,
            node_size=0.5,
            width=0.5,
            # node_color="#AB47BC",
            # edge_color="#CFD8DC",
            ax=ax,
        )

        plt.savefig(f"./node-link-{d_name}.png")


if __name__ == "__main__":
    main()
