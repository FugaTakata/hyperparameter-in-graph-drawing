# Standard Library
import os
from pathlib import Path

# Third Party Library
from dotenv import load_dotenv

load_dotenv()

project_root_dir = os.environ["HYPERPARAMETER_OPTIMIZATION_ROOT_PATH"]


def get_project_root_path():
    project_root_path = Path(project_root_dir)

    return project_root_path


def get_dataset_path(dataset_name):
    project_root_path = get_project_root_path()
    dataset_path = project_root_path.joinpath(
        "submodules/egraph-rs/js/dataset/"
    ).joinpath(f"{dataset_name}.json")

    return dataset_path


def get_shell_script_path(filename):
    project_root_path = get_project_root_path()
    shell_scripts_dir = project_root_path.joinpath("shell_scripts/")
    shell_scripts_path = shell_scripts_dir.joinpath(filename)

    shell_scripts_dir.mkdir(parents=True, exist_ok=True)

    return shell_scripts_path


def get_data_dir(layout_name, dataset_name, uuid):
    project_root_path = get_project_root_path()
    data_dir = (
        project_root_path.joinpath("data/")
        .joinpath(layout_name)
        .joinpath(dataset_name)
        .joinpath(uuid)
    )

    return data_dir


def get_optimization_path(layout_name, dataset_name, filename, uuid):
    data_dir = get_data_dir(
        layout_name=layout_name, dataset_name=dataset_name, uuid=uuid
    )
    optimization_dir = data_dir.joinpath("optimization/")
    optimization_path = optimization_dir.joinpath(filename)

    optimization_dir.mkdir(parents=True, exist_ok=True)

    return optimization_path


def get_r_nfs_path(layout_name, dataset_name, filename, uuid):
    data_dir = get_data_dir(
        layout_name=layout_name, dataset_name=dataset_name, uuid=uuid
    )
    r_nfs_dir = data_dir.joinpath("r_nfs/")
    r_nfs_path = r_nfs_dir.joinpath(filename)

    r_nfs_dir.mkdir(parents=True, exist_ok=True)

    return r_nfs_path


def get_o_nfs_path(layout_name, dataset_name, filename, uuid):
    data_dir = get_data_dir(
        layout_name=layout_name, dataset_name=dataset_name, uuid=uuid
    )
    o_nfs_dir = data_dir.joinpath("o_nfs/")
    o_nfs_path = o_nfs_dir.joinpath(filename)

    o_nfs_dir.mkdir(parents=True, exist_ok=True)

    return o_nfs_path


def get_e_nfs_path(layout_name, dataset_name, filename, uuid):
    data_dir = get_data_dir(
        layout_name=layout_name, dataset_name=dataset_name, uuid=uuid
    )
    e_nfs_dir = data_dir.joinpath("e_nfs/")
    e_nfs_path = e_nfs_dir.joinpath(filename)

    e_nfs_dir.mkdir(parents=True, exist_ok=True)

    return e_nfs_path
