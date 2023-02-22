# Standard Library
import argparse

# First Party Library
from config import dataset, layout, paths
from utils import iso_datetime


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--db-stem", required=True, help="database stem")
    parser.add_argument(
        "-d", choices=dataset.DATASET_NAMES, required=True, help="dataset name"
    )
    parser.add_argument(
        "-l", choices=layout.LAYOUT_NAMES, required=True, help="layout name"
    )
    parser.add_argument("--n-seed", type=int, required=True, help="n seed")
    parser.add_argument(
        "--n-jobs", type=int, required=True, help="number of jobs"
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    DB_STEM = args.db_stem
    D = args.d
    L = args.l
    N_SEED = args.n_seed
    N_JOBS = args.n_jobs

    stem = "generate_o_nfs"
    filename = f"{stem}.sh"
    shell_script_path = paths.get_shell_script_path(filename=filename)

    dt_now_jst = iso_datetime.get_now_jst()

    groups = {
        4: [
            [
                "angular_resolution",
                "aspect_ratio",
                "ideal_edge_length",
            ],
            ["crossing_angle", "crossing_number"],
            [
                "gabriel_graph_property",
                "shape_based_metrics",
            ],
            ["node_resolution", "stress"],
        ]
    }

    lines = ["#!/bin/sh", ""]

    for target_qm_names, job_n in zip(groups[N_JOBS], range(N_JOBS)):
        line = []
        for target_qm_name in target_qm_names:
            line.append(
                f"poetry run python -u ./src/scripts/{stem}.py --db-stem {DB_STEM} -d {D} -l {L} --n-seed {N_SEED} -t {target_qm_name} 2>&1 | tee -a {stem}-{job_n}.out"
            )
        lines.append(f"({' && '.join(line)}) &")

    lines.append("wait")
    lines.append(
        f'poetry run python ./src/scripts/notify.py -m "{stem} {L} {D} finished"'
    )

    with shell_script_path.open(mode="w") as f:
        f.write("\n".join(lines))
