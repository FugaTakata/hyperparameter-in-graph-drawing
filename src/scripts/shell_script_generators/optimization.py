# Standard Library
import argparse

# First Party Library
from config import dataset, layout, paths, quality_metrics


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--uuid", required=True, help="uuid")
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
        required=True,
        help="how to handle multiple seed",
    )
    parser.add_argument(
        "--n-jobs", type=int, required=True, help="number of jobs"
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    UUID = args.uuid
    D = args.d
    L = args.l
    N_TRIALS = args.n_trials
    N_SEED = args.n_seed
    HANDLE_RESULT = args.handle_result
    FIXED_SEED = args.fixed_seed
    N_JOBS = args.n_jobs

    stem = "optimization"
    filename = f"{stem}.sh"
    shell_script_path = paths.get_shell_script_path(filename=filename)

    result_handler_type = ""
    if HANDLE_RESULT == "median":
        result_handler_type = f"-{N_SEED}median"
    elif HANDLE_RESULT == "mean":
        result_handler_type += f"-{N_SEED}mean"

    db_stem = f"{N_TRIALS * N_JOBS}trials{result_handler_type}-{'fixed_seed' if FIXED_SEED else 'non_fixed_seed'}"

    target_qm_names = quality_metrics.ALL_QM_NAMES

    lines = ["#!/bin/sh", ""]

    for job_n in range(N_JOBS):
        # to avoid optuna failing
        line = [f"sleep {job_n}"]
        for target_qm_name in target_qm_names:
            line.append(
                f"poetry run python -u ./src/scripts/{stem}.py --uuid {UUID} --stem {db_stem} -d {D} -l {L} --n-trials {N_TRIALS} --n-seed {N_SEED} {'--fixed-seed' if FIXED_SEED else ''} --handle-result {HANDLE_RESULT} -t {target_qm_name} 2>&1 | tee -a {stem}-{job_n}.out"
            )
        lines.append(f"({' && '.join(line)}) &")

    lines.append("wait")
    lines.append(
        f'poetry run python ./src/scripts/notify.py -m "{stem} {L} {D} finished"'
    )

    with shell_script_path.open(mode="w") as f:
        f.write("\n".join(lines))
