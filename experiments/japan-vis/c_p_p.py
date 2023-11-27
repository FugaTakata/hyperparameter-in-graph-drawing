# Standard Library
import json
import argparse

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

EDGE_WEIGHT = 30

n_trials = 200
n_compare = 100
threshold = 0.05


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
    compare_results = [["dataset", "n_pareto", "max_win"]]
    print("dataset", "n_pareto", "max_win")

    for d_name in d_names:
        a = "max_pivots=0.25n"

        seeds = list(range(10))
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        pareto_df_paths = [
            ex_path.joinpath(
                f"data/pareto/{d_name}/{study_name}/seed={seed}.pkl"
            )
            for seed in seeds
        ]
        pareto_df = pd.concat(
            [pd.read_pickle(path) for path in pareto_df_paths]
        )
        pareto_df = generate_seed_median_df(pareto_df)

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

        pareto_df["win"] = 0
        pareto_df["even"] = 0
        pareto_df["lose"] = 0
        rows = list(pareto_df.iterrows())
        for row_index, (i_a, trial_a) in enumerate(rows):
            for i_b, trial_b in rows[row_index + 1 :]:
                qa = dict(
                    [
                        (qm_name, trial_a[f"values_{qm_name}"])
                        for qm_name in qm_names
                    ]
                )
                qb = dict(
                    [
                        (qm_name, trial_b[f"values_{qm_name}"])
                        for qm_name in qm_names
                    ]
                )
                score = calc_hp_compare_score(
                    qa=qa,
                    qb=qb,
                    scalers=scalers,
                    n_compare=n_compare,
                )

                if score > 1 + threshold:
                    pareto_df.at[i_a, "win"] += 1
                    pareto_df.at[i_b, "lose"] += 1
                elif score < 1 - threshold:
                    pareto_df.at[i_a, "lose"] += 1
                    pareto_df.at[i_b, "win"] += 1
                else:
                    pareto_df.at[i_a, "even"] += 1
                    pareto_df.at[i_b, "even"] += 1

        most_win = pareto_df[pareto_df["win"] == pareto_df["win"].max()]
        print(
            d_name,
            len(pareto_df),
            pareto_df["win"].max(),
        )
        compare_results.append(
            [
                d_name,
                len(pareto_df),
                pareto_df["win"].max(),
            ]
        )
        for i, row in most_win.iterrows():
            d = row.to_dict()
            pivots = int(d["params_pivots"])
            iterations = int(d["params_iterations"])
            eps = d["params_eps"]
            print(i, pivots, iterations, eps)
            compare_results.append([i, pivots, iterations, eps])

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

            most_win_pareto_picture_path = ex_path.joinpath(
                f"results/picture/baseline/empirical/{d_name}/{study_name}/seed={picture_seed}.png"
            )
            most_win_pareto_picture_path.parent.mkdir(
                parents=True, exist_ok=True
            )
            plt.savefig(most_win_pareto_picture_path)

    compare_result_path = ex_path.joinpath(
        f"results/c_p_p/{d_name}/{study_name}/results.json"
    )
    compare_result_path.parent.mkdir(parents=True, exist_ok=True)
    with open(compare_result_path, mode="w") as f:
        json.dump(compare_results, f)


if __name__ == "__main__":
    main()
