# Standard Library
import argparse

# First Party Library
from config import dataset, layout, paths


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--uuid", required=True, help="uuid")
    parser.add_argument(
        "-d", choices=dataset.DATASET_NAMES, required=True, help="dataset name"
    )
    parser.add_argument(
        "-l", choices=layout.LAYOUT_NAMES, required=True, help="layout name"
    )
    parser.add_argument("--n-params", type=int, required=True, help="n params")
    parser.add_argument("--n-seed", type=int, required=True, help="n seed")
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
    N_PARAMS = args.n_params
    N_SEED = args.n_seed
    N_JOBS = args.n_jobs

    stem = "generate_r_nfs"
    filename = f"{stem}.sh"
    shell_script_path = paths.get_shell_script_path(filename=filename)

    lines = ["#!/bin/sh", ""]
    for job_n in range(N_JOBS):
        export_file_stem = f"{N_PARAMS * N_JOBS}rp-{N_SEED}nfs-{job_n}"
        lines.append(
            f"(sleep {job_n} && poetry run python -u ./src/scripts/{stem}.py --uuid {UUID} --stem {export_file_stem} -d {D} -l {L} --n-params {N_PARAMS} --n-seed {N_SEED} 2>&1 | tee -a {stem}-{job_n}.out) &"
        )

    lines.append("wait")
    lines.append(
        f'poetry run python ./src/scripts/notify.py -m "{stem} {L} {D} finished"'
    )

    with shell_script_path.open(mode="w") as f:
        f.write("\n".join(lines))
