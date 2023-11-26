# Third Party Library
import matplotlib.pyplot as plt
import networkx as nx
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.paths import get_dataset_path
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

threshold = 0.05
EDGE_WEIGHT = 30
n_trials = 100
n_compare = 100


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

    print("dataset", "score", "pivots", "iterations", "eps")

    for d_name in d_names:
        aas = [
            "pref=1.0,2.0,1.0,1.0,2.0,2.0,2.0,1.0,2.0,3.0",
            "pref=1.0,2.0,1.0,1.0,2.0,2.0,2.0,1.0,2.0,3.0",
            "pref=1.0,1.0,2.0,2.0,1.0,1.0,3.0,1.0,2.0,1.0",
            "pref=10.0,5.0,10.0,10.0,5.0,5.0,20.0,5.0,15.0,15.0",
            "pref=10.0,10.0,15.0,10.0,5.0,10.0,20.0,5.0,15.0,15.0",
            "pref=5.0,5.0,5.0,20.0,5.0,20.0,40.0,5.0,30.0,3.0",
        ]
        a = aas[5]

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

        # generate empirical
        pivots = 50
        iterations = 100
        eps = 0.1

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

        # compare
        best_trial = study.best_trial
        score = calc_hp_compare_score(
            qa=best_trial.user_attrs["row_quality_metrics"],
            qb=e_quality_metrics,
            scalers=scalers,
            n_compare=n_compare,
        )

        pivots = best_trial.user_attrs["params"]["pivots"]
        iterations = best_trial.user_attrs["params"]["iterations"]
        eps = best_trial.user_attrs["params"]["eps"]
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

        plt.savefig(f"./node-link-{d_name}.png")


if __name__ == "__main__":
    main()
