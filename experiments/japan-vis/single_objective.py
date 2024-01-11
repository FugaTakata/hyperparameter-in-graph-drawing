# Standard Library
import argparse
from statistics import median

# Third Party Library
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import (
    draw_and_measure,
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


def objective(nx_graph, scalers, p_max, pref, seeds):
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
        scaled_quality_metrics = dict(
            [
                (
                    qm_name,
                    scalers[qm_name].transform([[quality_metrics[qm_name]]])[
                        0
                    ][0],
                )
                for qm_name in qm_names
            ]
        )

        weighted_scaled_quality_metrics = {}
        for qm_name in qm_names:
            weighted_scaled_quality_metrics[qm_name] = (
                pref[qm_name] * scaled_quality_metrics[qm_name]
            )

        trial.set_user_attr("params", params)
        trial.set_user_attr("median_quality_metrics", median_quality_metrics)
        trial.set_user_attr("scaled_quality_metrics", scaled_quality_metrics)
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
    parser.add_argument("--study-id", required=True, help="study id")
    parser.add_argument("--db-suffix", required=True, help="db name suffix")
    parser.add_argument(
        "--seeds",
        type=int,
        required=True,
        nargs="*",
        help="seeds to get median",
    )
    parser.add_argument(
        "--prefs",
        type=float,
        nargs="*",
        help=f"pref weight for {[qm_names]}",
    )

    args = parser.parse_args()

    pref = {}
    pref_sum = 0
    for qm_name, p in zip(qm_names, args.prefs):
        pref[qm_name] = p
        pref_sum += p
    for qm_name in qm_names:
        pref[qm_name] /= pref_sum

    n_split = 10
    df_paths = [
        ex_path.joinpath(
            f"data/grid/{args.d}/n_split={n_split}/seed={data_seed}.pkl"
        )
        for data_seed in args.seeds
    ]
    df = pd.concat([pd.read_pickle(df_path) for df_path in df_paths])
    mdf = generate_seed_median_df(df)
    sscalers = generate_sscalers(mdf)

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )
    p_max = max(1, int(len(nx_graph.nodes) * 0.25))

    db_uri = f"sqlite:///{ex_path.joinpath(f'data/optimization/{args.d}-{args.db_suffix}.db')}"
    study_name = f"single-obj_{args.study_id}"
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
    study.set_user_attr("max_pivots", p_max)
    study.set_user_attr("pref", pref)
    study.set_user_attr("seeds", args.seeds)
    study.set_metric_names(["weighted_scaled_sum"])

    study.optimize(
        func=objective(
            nx_graph=nx_graph,
            scalers=sscalers,
            p_max=p_max,
            pref=pref,
            seeds=args.seeds,
        ),
        n_trials=args.n,
        show_progress_bar=True,
        gc_after_trial=True,
        n_jobs=-1,
    )


if __name__ == "__main__":
    main()
