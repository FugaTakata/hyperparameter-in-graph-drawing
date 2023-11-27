# Third Party Library
import matplotlib.pyplot as plt
import networkx as nx
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import (
    calc_hp_compare_score,
    draw,
    draw_and_measure,
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
n_compare = 2
threshold = 0.05


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
    print("dataset", "n_pareto", "max_win")

    for d_name in d_names:
        a = "max_pivots=0.25n"

        db_uri = (
            f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"
        )
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        study = optuna.load_study(study_name=study_name, storage=db_uri)

        best_trials = []
        for trial in study.best_trials:
            trial_dict = {
                **trial.user_attrs["row_quality_metrics"],
                **trial.user_attrs["params"],
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
        best_df["win"] = 0
        best_df["even"] = 0
        best_df["lose"] = 0
        rows = list(best_df.iterrows())
        for row_index, (i_a, trial_a) in enumerate(rows):
            for i_b, trial_b in rows[row_index + 1 :]:
                qa = dict(
                    [(qm_name, trial_a[qm_name]) for qm_name in qm_names]
                )
                qb = dict(
                    [(qm_name, trial_b[qm_name]) for qm_name in qm_names]
                )
                score = calc_hp_compare_score(
                    qa=qa,
                    qb=qb,
                    scalers=scalers,
                    n_compare=n_compare,
                )

                if score > 1 + threshold:
                    best_df.at[i_a, "win"] += 1
                    best_df.at[i_b, "lose"] += 1
                elif score < 1 - threshold:
                    best_df.at[i_a, "lose"] += 1
                    best_df.at[i_b, "win"] += 1
                else:
                    best_df.at[i_a, "even"] += 1
                    best_df.at[i_b, "even"] += 1

        most_win = best_df[best_df["win"] == best_df["win"].max()]
        print(
            d_name,
            len(best_df),
            best_df["win"].max(),
        )
        for i, row in most_win.iterrows():
            d = row.to_dict()
            print(d)
            pivots = int(d["pivots"])
            iterations = int(d["iterations"])
            eps = d["eps"]
            print(i, pivots, iterations, eps)

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

            plt.savefig(f"./node-link-p_p-{d_name}_{i}.png")


if __name__ == "__main__":
    main()
