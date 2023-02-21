# Standard Library
import argparse
import datetime

# First Party Library
from config import dataset, layout, paths, quality_metrics


def get_args():
    parser = argparse.ArgumentParser()

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
        "--n-means", type=int, required=True, help="n seed per trial"
    )
    parser.add_argument(
        "--fixed-seed", action="store_true", help="use fixed seed"
    )
    parser.add_argument(
        "--n-jobs", type=int, required=True, help="number of jobs"
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    STEM = args.stem
    D = args.d
    L = args.l
    N_TRIALS = args.n_trials
    N_MEANS = args.n_means
    FIXED_SEED = args.fixed_seed
    N_JOBS = args.n_jobs

    stem = "optimization"
    filename = f"{stem}.sh"
    shell_script_path = paths.get_shell_script_path(filename=filename)

    tz_jst = datetime.timezone(datetime.timedelta(hours=+9))
    dt_now_jst = datetime.datetime.now(tz=tz_jst)
    dt_now_jst_iso = datetime.datetime.isoformat(dt_now_jst)
    db_stem = f"{N_TRIALS * N_JOBS}trials-{N_MEANS}means-{'fixed-seed' if FIXED_SEED else 'non-fixed-seed'}_{dt_now_jst_iso}"

    target_qm_names = quality_metrics.ALL_QM_NAMES

    lines = ["#!/bin/sh", ""]

    for job_n in range(N_JOBS):
        # to avoid optuna failing
        line = [f"sleep {job_n}"]
        for target_qm_name in target_qm_names:
            line.append(
                f"poetry run python -u ./src/scripts/{stem}.py --stem {STEM} -d {D} -l {L} --n-trials {N_TRIALS} --n-means {N_MEANS} {'--fixed-seed' if FIXED_SEED else None} -t {target_qm_name} 2>&1 | tee -a {stem}-{job_n}.out"
            )
        lines.append(f"({' && '.join(line)}) &")

    lines.append("wait")
    lines.append(
        f'poetry run python ./src/scripts/notify.py -m "{stem} finished"'
    )

    with shell_script_path.open(mode="w") as f:
        f.write("\n".join(lines))
