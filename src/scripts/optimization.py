# Standard Library
import argparse
import random
import statistics

# Third Party Library
import optuna

# First Party Library
from config import const, dataset, layout, paths, quality_metrics
from optimizers import objective
from utils import graph


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--uuid", required=True, help="uuid")
    parser.add_argument("--stem", required=True, help="database stem")
    parser.add_argument(
        "-d", choices=dataset.DATASET_NAMES, required=True, help="dataset name"
    )
    parser.add_argument(
        "-l", choices=layout.LAYOUT_NAMES, required=True, help="layout name"
    )
    parser.add_argument(
        "--n-trials", type=int, required=True, help="n trials on optimization"
    )
    parser.add_argument(
        "--n-seed", type=int, required=True, help="n seed per trial"
    )
    parser.add_argument(
        "--fixed-seed", action="store_true", help="use fixed seed"
    )
    parser.add_argument(
        "--handle-result",
        choices=["normal", "mean", "median"],
        help="how to handle multiple seed",
    )
    parser.add_argument(
        "-t",
        choices=quality_metrics.ALL_QM_NAMES,
        nargs="*",
        required=True,
        help="target quality metrics names",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    UUID = args.uuid
    STEM = args.stem
    D = args.d
    L = args.l
    N_TRIALS = args.n_trials
    N_SEED = args.n_seed
    HANDLE_RESULT = args.handle_result
    FIXED_SEED = args.fixed_seed
    TARGET_QM_NAMES = args.t

    if FIXED_SEED and 1 != N_SEED:
        raise ValueError("n seed must be 1 when seed fixed")

    if HANDLE_RESULT == "normal" and (1 != N_SEED):
        raise ValueError("n seed must be 1 when handle result is normal")

    if HANDLE_RESULT != "normal" and (1 == N_SEED):
        raise ValueError(
            "n seed must be greater than 1 when handle result is not normal"
        )

    db_name = f"{STEM}.sql"
    optimization_path = paths.get_optimization_path(
        layout_name=L, dataset_name=D, filename=db_name, uuid=UUID
    )
    database_uri = f"sqlite:///{optimization_path.resolve()}"

    study_name = ",".join(TARGET_QM_NAMES)

    def generate_seed():
        seed = 0 if FIXED_SEED else random.randint(0, const.RAND_MAX)

        return seed

    def result_handler(result):
        qualities_result = {}
        for qm_name in quality_metrics.ALL_QM_NAMES:
            if HANDLE_RESULT == "normal":
                qualities_result[qm_name] = result[qm_name][0]
            elif HANDLE_RESULT == "mean":
                qualities_result[qm_name] = statistics.mean(result[qm_name])
            elif HANDLE_RESULT == "median":
                qualities_result[qm_name] = statistics.median(result[qm_name])

        return qualities_result

    nx_graph = graph.load_nx_graph(
        dataset_name=D, edge_weight=const.EDGE_WEIGHT
    )
    shortest_path_length = graph.get_shortest_path_length(nx_graph=nx_graph)

    study = optuna.create_study(
        directions=[
            quality_metrics.QUALITY_METRICS_MAP[qm_name].direction
            for qm_name in TARGET_QM_NAMES
        ],
        storage=database_uri,
        study_name=study_name,
        load_if_exists=True,
    )

    study.optimize(
        func=objective.ss(
            nx_graph=nx_graph,
            shortest_path_length=shortest_path_length,
            target_qm_names=TARGET_QM_NAMES,
            edge_weight=const.EDGE_WEIGHT,
            n_seed=N_SEED,
            result_handler=result_handler,
            generate_seed=generate_seed,
        ),
        n_trials=N_TRIALS,
        show_progress_bar=True,
    )
