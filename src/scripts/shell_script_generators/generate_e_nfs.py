# Standard Library
import argparse

# First Party Library
from config import dataset, layout, paths
from utils import iso_datetime


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", choices=dataset.DATASET_NAMES, required=True, help="dataset name"
    )
    parser.add_argument(
        "-l", choices=layout.LAYOUT_NAMES, required=True, help="layout name"
    )
    parser.add_argument("--n-seed", type=int, required=True, help="n seed")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    D = args.d
    L = args.l
    N_SEED = args.n_seed

    stem = "generate_o_nfs"
    filename = f"{stem}.sh"
    shell_script_path = paths.get_shell_script_path(filename=filename)

    dt_now_jst = iso_datetime.get_now_jst()

    lines = ["#!/bin/sh", ""]

    export_file_stem = f"{N_SEED}nfs_{dt_now_jst}"
    lines.append(
        f"poetry run python -u ./src/scripts/{stem}.py --stem {export_file_stem} -d {D} -l {L} --n-seed {N_SEED} 2>&1 | tee -a {stem}.out"
    )

    lines.append(
        f'poetry run python ./src/scripts/notify.py -m "{stem} {L} {D} finished"'
    )

    with shell_script_path.open(mode="w") as f:
        f.write("\n".join(lines))
