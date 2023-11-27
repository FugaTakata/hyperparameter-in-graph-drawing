# Standard Library
import argparse
import json

# Third Party Library
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from egraph import Drawing
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import (
    calc_hp_compare_score,
    draw,
    ex_path,
    generate_seed_median_df,
    generate_sscalers,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

threshold = 0.05
EDGE_WEIGHT = 30
n_trials = 100
n_compare = 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True, help="picture seed")
    args = parser.parse_args()

    picture_seed = args.seed
    d_names = [
        "1138_bus",
        "USpowerGrid",
        "dwt_1005",
        "poli",
        "qh882",
        "3elt",
        "dwt_2680",
    ]
    compare_results = [
        ["dataset", "score", "pivots", "iterations", "eps"],
    ]

    print("dataset", "score", "pivots", "iterations", "eps")

    for d_name in d_names:
        aas = [
            "pref=1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0",
            "pref=1.0,2.0,1.0,1.0,2.0,2.0,2.0,1.0,2.0,3.0",
            "pref=1.0,1.0,2.0,2.0,1.0,1.0,3.0,1.0,2.0,1.0",
            "pref=10.0,5.0,10.0,10.0,5.0,5.0,20.0,5.0,15.0,15.0",
            "pref=2.0,1.0,1.0,3.0,2.0,2.0,3.0,1.0,2.0,2.0",
        ]
        a = aas[0]

        seeds = list(range(10))
        study_name = f"{d_name}_n-trials={n_trials}_sscaled-sum_{a}"

        best_df_paths = [
            ex_path.joinpath(
                f"data/best/{d_name}/{study_name}/seed={seed}.pkl"
            )
            for seed in seeds
        ]
        best_df = pd.concat([pd.read_pickle(path) for path in best_df_paths])
        best_df = generate_seed_median_df(best_df)
        best = best_df.iloc[0]

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
        eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)

        # empirical
        empirical_df_paths = [
            ex_path.joinpath(
                f"data/baseline/empirical/{d_name}/seed={seed}.pkl"
            )
            for seed in seeds
        ]
        empirical_df = pd.concat(
            [pd.read_pickle(path) for path in empirical_df_paths]
        )

        empirical = empirical_df.iloc[0]
        pivots = int(empirical["params_pivots"])
        iterations = int(empirical["params_iterations"])
        eps = empirical["params_eps"]

        eg_drawing = Drawing.initial_placement(eg_graph)
        pos = draw(
            pivots=pivots,
            iterations=iterations,
            eps=eps,
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            eg_drawing=eg_drawing,
            edge_weight=EDGE_WEIGHT,
            seed=0,
        )

        fig, ax = plt.subplots(dpi=300, facecolor="white")
        ax.set_aspect("equal")

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

        empirical_picture_path = ex_path.joinpath(
            f"results/picture/baseline/empirical/{d_name}/seed={picture_seed}.png"
        )
        empirical_picture_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(empirical_picture_path)

        # compare
        qa = dict(
            [(qm_name, best[f"values_{qm_name}"]) for qm_name in qm_names]
        )
        qb = dict(
            [(qm_name, empirical[f"values_{qm_name}"]) for qm_name in qm_names]
        )
        score = calc_hp_compare_score(
            qa=qa,
            qb=qb,
            scalers=scalers,
            n_compare=n_compare,
        )

        pivots = int(best["params_pivots"])
        iterations = int(best["params_iterations"])
        eps = best["params_eps"]
        compare_results.append([d_name, score, pivots, iterations, eps])
        print(d_name, score, pivots, iterations, eps)

        eg_drawing = Drawing.initial_placement(eg_graph)
        pos = draw(
            pivots=pivots,
            iterations=iterations,
            eps=eps,
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            eg_drawing=eg_drawing,
            edge_weight=EDGE_WEIGHT,
            seed=0,
        )

        fig, ax = plt.subplots(dpi=300, facecolor="white")
        ax.set_aspect("equal")

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

        best_picture_path = ex_path.joinpath(
            f"results/picture/baseline/empirical/{d_name}/{study_name}/seed={picture_seed}.png"
        )
        best_picture_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(best_picture_path)

    compare_result_path = ex_path.joinpath(
        f"results/c_b_e/{d_name}/{study_name}/results.json"
    )
    compare_result_path.parent.mkdir(parents=True, exist_ok=True)
    with open(compare_result_path, mode="w") as f:
        json.dump(compare_results, f)


if __name__ == "__main__":
    main()
