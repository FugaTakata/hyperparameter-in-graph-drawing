# Standard Library
import argparse
import math

# Third Party Library
import optuna
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import draw_and_measure, ex_path, pivots2rate
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30


def objective(nx_graph):
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)
    p_max = max(1, int(n_nodes * 0.25))

    def _objective(trial: optuna.Trial):
        eg_drawing = Drawing.initial_placement(eg_graph)
        pivots = trial.suggest_int("pivots", 1, p_max)
        pivots_rate = pivots2rate(pivots, p_max)
        iterations = trial.suggest_int("iterations", 1, 200)
        eps = trial.suggest_float("eps", 0.01, 1)

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
            "pivots_rate": pivots_rate,
            "iterations": iterations,
            "eps": eps,
        }

        trial.set_user_attr("params", params)
        trial.set_user_attr("row_quality_metrics", quality_metrics)

        result = [quality_metrics[qm_name] for qm_name in qm_names]
        return result

    return _objective


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-n", type=int, required=True, help="n_trials")
    parser.add_argument("-a", required=True, help="additional name info")

    args = parser.parse_args()

    db_uri = f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )

    study_name = f"{args.d}_n-trials={args.n}_multi-objective_{args.a}"
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
        n_trials=args.n,
        n_jobs=args.j,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
