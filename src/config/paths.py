# Standard Library
import os
from pathlib import Path

# Third Party Library
from dotenv import load_dotenv

load_dotenv()

project_root_dir = os.environ["HYPERPARAMETER_OPTIMIZATION_ROOT_PATH"]
dataset_dir = "submodules/egraph-rs/js/dataset/"
data_dir = "data/"


def get_dataset_path(dataset_name):
    dataset_path = (
        Path(project_root_dir)
        .joinpath(dataset_dir)
        .joinpath(f"{dataset_name}.json")
    )

    return dataset_path


def get_r_nfs_dir(layout_name, dataset_name):
    r_nfs_dir = (
        Path(project_root_dir)
        .joinpath(data_dir)
        .joinpath("r_nfs/")
        .joinpath(layout_name)
        .joinpath(dataset_name)
    )

    return r_nfs_dir


def get_r_nfs_path(layout_name, dataset_name, filename):
    r_nfs_dir = get_r_nfs_dir(
        layout_name=layout_name, dataset_name=dataset_name
    )
    r_nfs_path = r_nfs_dir.joinpath(filename)

    return r_nfs_path


def get_o_nfs_dir(layout_name, dataset_name):
    o_nfs_dir = (
        Path(project_root_dir)
        .joinpath(data_dir)
        .joinpath("o_nfs/")
        .joinpath(layout_name)
        .joinpath(dataset_name)
    )

    return o_nfs_dir


def get_o_nfs_path(layout_name, dataset_name, filename):
    o_nfs_dir = get_o_nfs_dir(
        layout_name=layout_name, dataset_name=dataset_name
    )
    o_nfs_path = o_nfs_dir.joinpath(filename)

    return o_nfs_path
