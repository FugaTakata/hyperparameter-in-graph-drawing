# Standard Library
import argparse
from statistics import median

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


def objective(nx_graph, p_max, seeds):
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)

    def _objective(trial: optuna.Trial):
        pivots = trial.suggest_int("pivots", 1, p_max)
        pivots_rate = pivots2rate(pivots, n_nodes)
        iterations = trial.suggest_int("iterations", 1, 200)
        eps = trial.suggest_float("eps", 0.01, 1)
        params = {
            "pivots": pivots,
            "pivots_rate": pivots_rate,
            "iterations": iterations,
            "eps": eps,
        }

        all_seed_quality_metrics = dict(
            [(qm_name, []) for qm_name in qm_names]
        )

        for seed in seeds:
            eg_drawing = Drawing.initial_placement(eg_graph)
            pos, quality_metrics = draw_and_measure(
                pivots=pivots,
                iterations=iterations,
                eps=eps,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                eg_drawing=eg_drawing,
                eg_distance_matrix=eg_distance_matrix,
                edge_weight=EDGE_WEIGHT,
                seed=seed,
                n_nodes=n_nodes,
                n_edges=n_edges,
            )
            for qm_name in qm_names:
                all_seed_quality_metrics[qm_name].append(
                    quality_metrics[qm_name]
                )

        median_quality_metrics = dict(
            [
                (qm_name, median(all_seed_quality_metrics[qm_name]))
                for qm_name in qm_names
            ]
        )

        trial.set_user_attr("params", params)
        trial.set_user_attr("median_quality_metrics", median_quality_metrics)

        result = [median_quality_metrics[qm_name] for qm_name in qm_names]
        return result

    return _objective


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-n", type=int, required=True, help="n_trials")
    parser.add_argument("--db-suffix", required=True, help="db name suffix")
    parser.add_argument(
        "--study-suffix", required=True, help="study name suffix"
    )
    parser.add_argument(
        "--seeds",
        type=int,
        required=True,
        nargs="*",
        help="seeds to get median",
    )

    args = parser.parse_args()

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )
    p_max = max(1, int(len(nx_graph.nodes) * 0.25))

    study_name = f"multi-obj-{args.study_suffix}"
    db_uri = f"sqlite:///{ex_path.joinpath(f'data/optimization/{args.d}-{args.db_suffix}.db')}"
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
    study.set_user_attr("max_pivots", p_max)
    study.set_user_attr("seeds", args.seeds)
    study.set_metric_names(qm_names)

    study.optimize(
        func=objective(nx_graph=nx_graph, p_max=p_max, seeds=args.seeds),
        n_trials=args.n,
        n_jobs=-1,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
# 1.9mb
