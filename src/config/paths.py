# Standard Library
import os
from pathlib import Path

# Third Party Library
from dotenv import load_dotenv

load_dotenv()

project_root_dir = os.environ["HYPERPARAMETER_OPTIMIZATION_ROOT_PATH"]


def get_dataset_path(dataset_name):
    dataset_path = (
        Path(project_root_dir)
        .joinpath("submodules/egraph-rs/js/dataset/")
        .joinpath(f"{dataset_name}.json")
    )

    return dataset_path


def get_data_dir(layout_name, dataset_name):
    data_dir = (
        Path(project_root_dir)
        .joinpath("data/")
        .joinpath(layout_name)
        .joinpath(dataset_name)
    )

    return data_dir


def get_optimization_path(layout_name, dataset_name, filename):
    data_dir = get_data_dir(layout_name=layout_name, dataset_name=dataset_name)
    optimization_dir = data_dir.joinpath("optimization/")
    optimization_path = optimization_dir.joinpath(filename)

    optimization_dir.mkdir(parents=True, exist_ok=True)

    return optimization_path


def get_r_nfs_path(layout_name, dataset_name, filename):
    data_dir = get_data_dir(layout_name=layout_name, dataset_name=dataset_name)
    r_nfs_dir = data_dir.joinpath("r_nfs/")
    r_nfs_path = r_nfs_dir.joinpath(filename)

    r_nfs_dir.mkdir(parents=True, exist_ok=True)

    return r_nfs_path


def get_o_nfs_path(layout_name, dataset_name, filename):
    data_dir = get_data_dir(layout_name=layout_name, dataset_name=dataset_name)
    o_nfs_dir = data_dir.joinpath("o_nfs/")
    o_nfs_path = o_nfs_dir.joinpath(filename)

    o_nfs_dir.mkdir(parents=True, exist_ok=True)

    return o_nfs_path
