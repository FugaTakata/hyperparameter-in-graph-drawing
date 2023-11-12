# Standard Library
from pathlib import Path

# Local Library
from .env import PROJECT_ROOT_PATH_STRING

root_path = Path(PROJECT_ROOT_PATH_STRING)


def get_dataset_path(dataset_name: str) -> Path:
    return root_path.joinpath("submodules/egraph-rs/js/dataset/").joinpath(
        f"{dataset_name}.json"
    )
