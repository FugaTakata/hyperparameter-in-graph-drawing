# Standard Library
import argparse

# Third Party Library
import optuna
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.quality_metrics import time_complexity
from ex_utils.share import draw_and_measure, ex_path, rate2pivots
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30
TIME_COMPLEXITY_CAP = 10**8


def objective(nx_graph):
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)

    def _objective(trial: optuna.Trial):
        eg_drawing = Drawing.initial_placement(eg_graph)
        pivots_rate = trial.suggest_float("pivots_rate", 0, 1)
        pivots = rate2pivots(rate=pivots_rate, n_nodes=n_nodes)
        iterations = trial.suggest_int("iterations", 1, 200)
        eps = trial.suggest_float("eps", 0.01, 1)
        time_complexity_value = time_complexity.measure(
            pivots=pivots,
            iterations=iterations,
            n_nodes=n_nodes,
            n_edges=n_edges,
        )
        if TIME_COMPLEXITY_CAP < time_complexity_value:
            raise optuna.TrialPruned()

        pos, quality_metrics = draw_and_measure(
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

        params = {
            "pivots": pivots,
            "iterations": iterations,
            "eps": eps,
        }
        trial.set_user_attr("params", params)
        trial.set_user_attr("quality_metrics", quality_metrics)

        result = [quality_metrics[qm_name] for qm_name in qm_names]
        return result

    return _objective


def main():
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

    study_name = f"{args.d}_n-trials={args.n}_prune-time-10-8_multi-objective"
    storage = optuna.storages.RDBStorage(
        url=db_uri,
        engine_kwargs={"connect_args": {"timeout": 1000}},
    )
    study = optuna.create_study(
        directions=["maximize" for _ in qm_names],
        storage=storage,
        study_name=study_name,
        load_if_exists=True,
    )
    study.set_metric_names(qm_names)

    study.optimize(
        func=objective(nx_graph=nx_graph),
        callbacks=[
            optuna.study.MaxTrialsCallback(
                n_trials=args.n,
                states=(
                    optuna.trial.TrialState.COMPLETE,
                    optuna.trial.TrialState.RUNNING,
                ),
            )
        ],
        n_jobs=-1,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
