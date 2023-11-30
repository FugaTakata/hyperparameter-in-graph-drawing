# Standard Library
import argparse
import math

# Third Party Library
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_name_abbreviations, qm_names
from ex_utils.quality_metrics import time_complexity
from ex_utils.share import (
    draw_and_measure,
    ex_path,
    generate_base_df_data,
    generate_mmscalers,
    generate_sscalers,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

n_bins = 50
EDGE_WEIGHT = 30

p_names = ["params_pivots", "params_iterations", "params_eps"]
# p_names = ["params_pivots", "params_iterations"]
# qm_names = [
#     "angular_resolution",
#     "aspect_ratio",
#     "crossing_angle",
#     "crossing_number",
#     "gabriel_graph_property",
#     "ideal_edge_length",
#     "neighborhood_preservation",
#     "node_resolution",
#     "runtime",
#     "time_complexity",
# ]
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
    seed = 1
    n_split = 10
    data_seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    df_paths = [
        ex_path.joinpath(
            f"data/grid/{d_name}/n={n_split}/seed={data_seed}.pkl"
        )
        for data_seed in data_seeds
    ]

    df = (
        pd.concat([pd.read_pickle(df_path) for df_path in df_paths])
        .reset_index()
        .sort_index(axis=1)
    )
    median_df = (
        df.groupby(["params_pivots", "params_iterations", "params_eps"])
        .agg(
            dict(
                [(f"values_{qm_name}", "median") for qm_name in qm_names]
                + [("edge_weight", "first")]
            )
        )
        .reset_index()
        .sort_index(axis=1)
    )

    # display(median_df.describe())

    # dataset_path = get_dataset_path(d_name)
    # nx_graph = nx_graph_preprocessing(
    #     load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    # )
    # n_nodes = len(nx_graph.nodes)
    # n_edges = len(nx_graph.edges)

    # l = time_complexity.measure(n_nodes, 200, n_nodes, n_edges)
    # m = time_complexity.measure(n_nodes / 2, 100, n_nodes, n_edges)
    # s = time_complexity.measure(1, 1, n_nodes, n_edges)
    # max_time = -time_complexity.measure(n_nodes, 200, n_nodes, n_edges) / 10
    # max_time = -time_complexity.measure(1, 1, n_nodes, n_edges) ** 2
    # max_time = (
    #     -(
    #         time_complexity.measure(n_nodes, 200, n_nodes, n_edges)
    #         + time_complexity.measure(1, 1, n_nodes, n_edges)
    #     )
    #     / 2
    # )
    # max_time = -(l) / np.sqrt(s)
    # max_time = -(10**8)
    # df_data = []
    # for pivots in range(1, n_nodes + 1):
    #     for iterations in range(1, 200 + 1):
    #         df_data.append(
    #             {
    #                 "pivots": pivots,
    #                 "iterations": iterations,
    #                 "time_complexity": time_complexity.measure(
    #                     pivots, iterations, n_nodes, n_edges
    #                 ),
    #             }
    #         )
    # ddf = pd.DataFrame(df_data)
    # med = ddf["time_complexity"].quantile(0.75)

    # max_time = med
    # max_time = -l / 10
    # adf = median_df.query(f"values_time_complexity >= {max_time}")
    # bdf = median_df.query(f"values_time_complexity < {max_time}")
    q = {}

    for p_name in p_names:
        fig, axes = plt.subplots(
            nrows=2, ncols=5, dpi=300, facecolor="white", squeeze=False
        )
        for qm_name, ax in zip(qm_names, axes.flatten()):
            # ax.boxplot(
            #     median_df[f"values_{qm_name}"], positions=median_df[p_name]
            # )
            median_df.boxplot(
                column=f"values_{qm_name}", by=p_name, ax=ax, showfliers=False
            )
            ax.tick_params(axis="x", labelsize=5, rotation=-45)
            ax.tick_params(axis="y", labelsize=5)
            ax.set_title(f"{qm_name}", fontsize=5)
            # ax.boxplot(median_df[p_name], median_df[f"values_{qm_name}"])

            # ax.scatter(
            #     list(map(str, adf[p_name])), adf[f"values_{qm_name}"], s=1
            # )
            # ax.scatter(
            #     list(map(str, bdf[p_name])),
            #     bdf[f"values_{qm_name}"],
            #     s=1,
            #     color="red",
            # )
            # ax.scatter(df[p_name], df[f"values_{qm_name}"], s=1)
        fig.suptitle(f"{d_name} {p_name}", fontsize=10)
        plt.show()
