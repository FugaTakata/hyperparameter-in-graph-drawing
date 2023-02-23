# Standard Library
import argparse
import json

# First Party Library
from config import dataset, layout, paths
from utils import iso_datetime, uuid


def generate_r_nfs(dataset_name, layout_name, n_params, n_seed, n_jobs, uuid):
    lines = [
        f"# {layout_name} {dataset_name} r_nfs",
        f"poetry run python src/scripts/shell_script_generators/generate_r_nfs.py --uuid {uuid} -d {dataset_name} -l {layout_name} --n-params {n_params} --n-seed {n_seed} --n-jobs {n_jobs}",
    ]

    return lines


def generate_o_nfs(db_stem, dataset_name, layout_name, n_seed, n_jobs, uuid):
    lines = [
        f"# {layout_name} {dataset_name} o_nfs",
        f"poetry run python src/scripts/shell_script_generators/generate_o_nfs.py --uuid {uuid} --db-stem {db_stem} -d {dataset_name} -l {layout_name} --n-seed {n_seed} --n-jobs {n_jobs}",
    ]

    return lines


def generate_e_nfs(dataset_name, layout_name, n_seed, uuid):
    lines = [
        f"# {layout_name} {dataset_name} e_nfs",
        f"poetry run python src/scripts/shell_script_generators/generate_e_nfs.py --uuid {uuid} -d {dataset_name} -l {layout_name} --n-seed {n_seed}",
    ]

    return lines


def optimization(dataset_name, layout_name, n_trials, n_seed, n_jobs, uuid):
    lines = [
        f"# {layout_name} {dataset_name} optimization fixed-seed",
        f"poetry run python src/scripts/shell_script_generators/optimization.py --uuid {uuid} -d {dataset_name} -l {layout_name} --n-trials {n_trials} --n-seed {'1'} --fixed-seed --handle-result {'normal'} --n-jobs {n_jobs}",
    ]

    lines += [
        f"# {layout_name} {dataset_name} optimization non-fixed-seed",
        f"poetry run python src/scripts/shell_script_generators/optimization.py --uuid {uuid} -d {dataset_name} -l {layout_name} --n-trials {n_trials} --n-seed {'1'} --handle-result {'normal'} --n-jobs {n_jobs}",
    ]

    lines += [
        f"# {layout_name} {dataset_name} optimization mean",
        f"poetry run python src/scripts/shell_script_generators/optimization.py --uuid {uuid} -d {dataset_name} -l {layout_name} --n-trials {n_trials} --n-seed {n_seed} --handle-result {'mean'} --n-jobs {n_jobs}",
    ]

    lines += [
        f"# {layout_name} {dataset_name} optimization median",
        f"poetry run python src/scripts/shell_script_generators/optimization.py --uuid {uuid} -d {dataset_name} -l {layout_name} --n-trials {n_trials} --n-seed {n_seed} --handle-result {'median'} --n-jobs {n_jobs}",
    ]

    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uuid", help="uuid")
    args = parser.parse_args()

    uuid = args.uuid if args.uuid is not None else uuid.get_uuid()
    jst = iso_datetime.get_now_jst()
    shell_script_path = paths.get_shell_script_path(
        "all.shell_script_generator.sh"
    )
    project_root_path = paths.get_project_root_path()
    lines = ["do not run this script", ""]
    for layout_name in layout.LAYOUT_NAMES:
        for dataset_name in dataset.DATASET_NAMES:
            data_dir = paths.get_data_dir(
                layout_name=layout_name, dataset_name=dataset_name, uuid=uuid
            )

            lines += generate_e_nfs(
                dataset_name=dataset_name,
                layout_name=layout_name,
                n_seed=50,
                uuid=uuid,
            )

            lines += generate_r_nfs(
                dataset_name=dataset_name,
                layout_name=layout_name,
                n_params=5,
                n_seed=50,
                n_jobs=4,
                uuid=uuid,
            )

            lines += optimization(
                dataset_name=dataset_name,
                layout_name=layout_name,
                n_trials=25,
                n_seed=5,
                n_jobs=4,
                uuid=uuid,
            )

            optimization_dir = data_dir.joinpath("optimization/")
            if not optimization_dir.exists():
                continue

            for db_path in optimization_dir.iterdir():
                db_stem = db_path.stem
                lines += generate_o_nfs(
                    db_stem=db_stem,
                    dataset_name=dataset_name,
                    layout_name=layout_name,
                    n_seed=50,
                    n_jobs=4,
                    uuid=uuid,
                )

    with project_root_path.joinpath("data").joinpath("uuid_jst_map.json").open(
        mode="r"
    ) as f:
        obj = json.load(f)
    with project_root_path.joinpath("data").joinpath("uuid_jst_map.json").open(
        mode="w"
    ) as f:
        obj = {**obj, uuid: jst}
        json.dump(obj, f)
    with shell_script_path.open(mode="w") as f:
        f.write("\n".join(lines))
