# Standard Library
import argparse

# Third Party Library
import optuna
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import draw_and_measure_sscaled, ex_path, generate_sscalers
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30


def objective(nx_graph, sscalers):
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)

    def _objective(trial: optuna.Trial):
        eg_drawing = Drawing.initial_placement(eg_graph)

        (
            _params,
            quality_metrics,
            sscaled_quality_metrics,
            pos,
        ) = draw_and_measure_sscaled(
            pivots=trial.suggest_int("pivots", 1, 100),
            iterations=trial.suggest_int("iterations", 1, 200),
            eps=trial.suggest_float("eps", 0.01, 1),
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            eg_drawing=eg_drawing,
            eg_distance_matrix=eg_distance_matrix,
            edge_weight=EDGE_WEIGHT,
            seed=0,
            sscalers=sscalers,
        )

        for qm_name in qm_names:
            trial.set_user_attr(f"values_{qm_name}", quality_metrics[qm_name])
            trial.set_user_attr(
                f"values_sscaled_{qm_name}",
                sscaled_quality_metrics[qm_name][0][0],
            )

        result = sum(
            [sscaled_quality_metrics[qm_name] for qm_name in qm_names]
        )
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
        f"sqlite:///{ex_path.joinpath('results/optimization/optimization.db')}"
    )

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )

    seed = 0
    n_split = 10
    sscalers = generate_sscalers(
        ex_path.joinpath(f"data/grid/{args.d}/seed={seed}_n={n_split}.pkl")
    )

    study_name = f"{args.d}_ss_n-trials={args.n}_n-split={n_split}"
    study = optuna.create_study(
        direction="maximize",
        storage=db_uri,
        study_name=study_name,
        load_if_exists=True,
    )
    study.set_metric_names(["sscaled_sum"])

    study.optimize(
        func=objective(nx_graph=nx_graph, sscalers=sscalers),
        n_trials=args.n,
        n_jobs=-1,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
