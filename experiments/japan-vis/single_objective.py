# Standard Library
import argparse

# Third Party Library
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import (
    draw_and_measure_scaled,
    ex_path,
    generate_seed_median_df,
    generate_sscalers,
    pivots2rate,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30


def objective(nx_graph, scalers, pref):
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)
    p_max = max(1, int(n_nodes * 0.25))

    def _objective(trial: optuna.Trial):
        eg_drawing = Drawing.initial_placement(eg_graph)
        pivots = trial.suggest_int("pivots", 1, p_max)
        pivots_rate = pivots2rate(pivots, n_nodes)
        iterations = trial.suggest_int("iterations", 1, 200)
        eps = trial.suggest_float("eps", 0.01, 1)

        pos, quality_metrics, scaled_quality_metrics = draw_and_measure_scaled(
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

        params = {
            "pivots": pivots,
            "pivots_rate": pivots_rate,
            "iterations": iterations,
            "eps": eps,
        }

        trial.set_user_attr("params", params)
        trial.set_user_attr("row_quality_metrics", quality_metrics)
        trial.set_user_attr("scaled_quality_metrics", scaled_quality_metrics)
        weighted_scaled_quality_metrics = {}
        for qm_name in qm_names:
            weighted_scaled_quality_metrics[qm_name] = (
                pref[qm_name] * scaled_quality_metrics[qm_name]
            )
        trial.set_user_attr(
            "weighted_scaled_quality_metrics", weighted_scaled_quality_metrics
        )

        result = sum(
            [weighted_scaled_quality_metrics[qm_name] for qm_name in qm_names]
        )
        return result

    return _objective


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-n", type=int, required=True, help="n_trials")
    parser.add_argument("-a", required=True, help="additional name info")
    for qm_name in qm_names:
        parser.add_argument(
            f"--{qm_name}",
            required=True,
            type=float,
            help=f"pref weight for {qm_name}",
        )

    args = parser.parse_args()
    args_dict = args.__dict__

    pref = {}
    pref_sum = sum([args_dict[qm_name] for qm_name in qm_names])
    for qm_name in qm_names:
        pref[qm_name] = args_dict[qm_name] / pref_sum

    db_uri = f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )

    n_split = 10
    data_seeds = list(range(10))
    df_paths = [
        ex_path.joinpath(
            f"data/grid/{args.d}/n={n_split}/seed={data_seed}.pkl"
        )
        for data_seed in data_seeds
    ]
    df = pd.concat([pd.read_pickle(df_path) for df_path in df_paths])
    mdf = generate_seed_median_df(df)
    sscalers = generate_sscalers(mdf)

    study_name = f"{args.d}_n-trials={args.n}_sscaled-sum_pref={','.join(map(str, [args_dict[qm_name] for qm_name in qm_names]))}"
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
    study.set_user_attr("pref", pref)
    study.set_metric_names(["weighted_scaled_sum"])

    study.optimize(
        func=objective(nx_graph=nx_graph, scalers=sscalers, pref=pref),
        n_trials=args.n,
        n_jobs=-1,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
