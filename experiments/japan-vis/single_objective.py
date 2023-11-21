# Standard Library
import argparse
import os

# Third Party Library
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.quality_metrics import time_complexity
from ex_utils.share import (
    draw_and_measure_scaled,
    ex_path,
    generate_sscalers,
    rate2pivots,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30


def objective(nx_graph, scalers):
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)

    df_data = []
    for pivots in range(1, n_nodes + 1):
        for iterations in range(1, 200 + 1):
            df_data.append(
                {
                    "pivots": pivots,
                    "iterations": iterations,
                    "time_complexity": -time_complexity.measure(
                        pivots, iterations, n_nodes, n_edges
                    ),
                }
            )
    df = pd.DataFrame(df_data)
    time_complexity_cap = df["time_complexity"].quantile(0.25)

    def _objective(trial: optuna.Trial):
        eg_drawing = Drawing.initial_placement(eg_graph)
        pivots_rate = trial.suggest_float("pivots_rate", 0, 1)
        pivots = rate2pivots(rate=pivots_rate, n_nodes=n_nodes)
        iterations = trial.suggest_int("iterations", 1, 200)
        eps = trial.suggest_float("eps", 0.01, 1)
        time_complexity_value = -time_complexity.measure(
            pivots=pivots,
            iterations=iterations,
            n_nodes=n_nodes,
            n_edges=n_edges,
        )

        if time_complexity_cap > time_complexity_value:
            raise optuna.TrialPruned()

        pos, quality_metrics, scaled_qualit_metrics = draw_and_measure_scaled(
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
            scalers=scalers,
        )
        print(scaled_qualit_metrics)

        params = {
            "pivots": pivots,
            "iterations": iterations,
            "eps": eps,
        }
        trial.set_user_attr("params", params)
        trial.set_user_attr("quality_metrics", quality_metrics)
        trial.set_user_attr("scaled_quality_metrics", scaled_qualit_metrics)

        result = sum([scaled_qualit_metrics[qm_name] for qm_name in qm_names])
        return result

    return _objective


def main():
    print(os.cpu_count())
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-n", type=int, required=True, help="n_trials")

    args = parser.parse_args()

    db_uri = (
        f"sqlite:///{ex_path.joinpath('data/optimization/optimization.db')}"
    )

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )

    n_split = 10
    data_seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    df_paths = [
        ex_path.joinpath(
            f"data/grid/{args.d}/seed={data_seed}_n={n_split}.pkl"
        )
        for data_seed in data_seeds
    ]
    sscalers = generate_sscalers(df_paths)

    study_name = f"{args.d}_n-trials={args.n}_sscaled-sum"
    storage = optuna.storages.RDBStorage(
        url=db_uri,
        engine_kwargs={"connect_args": {"timeout": 1000}},
    )
    study = optuna.create_study(
        direction="maximize",
        storage=storage,
        study_name=study_name,
        load_if_exists=True,
    )

    study.optimize(
        func=objective(nx_graph=nx_graph, scalers=sscalers),
        n_trials=args.n,
        n_jobs=-1,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
