# Standard Library
import argparse
import random

# Third Party Library
import optuna
from tqdm import trange

# First Party Library
from config import const, dataset, layout, paths, quality_metrics
from generators import drawing_and_qualities
from generators import graph as graph_generator
from utils import graph, save, uuid


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
        "-t",
        choices=quality_metrics.ALL_QM_NAMES,
        nargs="*",
        required=True,
        help="target quality metrics names",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    DB_STEM = args.db_stem
    D = args.d
    L = args.l
    N_SEED = args.n_seed
    TARGET_QM_NAMES = args.t

    filename = f"{','.join(TARGET_QM_NAMES)}_{DB_STEM}.pkl"

    dataset_path = paths.get_dataset_path(dataset_name=D)

    o_nfs_path = paths.get_o_nfs_path(
        dataset_name=D, layout_name=L, filename=filename
    )

    nx_graph = graph.load_nx_graph(
        dataset_name=D, edge_weight=const.EDGE_WEIGHT
    )
    shortest_path_length = graph.get_shortest_path_length(nx_graph=nx_graph)

    database_name = f"{DB_STEM}.sql"
    optimization_path = paths.get_optimization_path(
        layout_name=L, dataset_name=D, filename=database_name
    )
    database_uri = f"sqlite:///{optimization_path.resolve()}"

    if L == layout.SS:
        eg_graph, eg_indices = graph_generator.egraph_graph(nx_graph=nx_graph)

        params_id = uuid.get_uuid()
        study = optuna.load_study(
            study_name=",".join(TARGET_QM_NAMES), storage=database_uri
        )
        params = study.best_trial.user_attrs["params"]

        for _ in trange(N_SEED):
            seed = random.randint(0, const.RAND_MAX)
            pos, qualities = drawing_and_qualities.ss(
                nx_graph=nx_graph,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                params=params,
                shortest_path_length=shortest_path_length,
                seed=seed,
                edge_weight=const.EDGE_WEIGHT,
            )

            save.o_nfs(
                params_id=params_id,
                target_qm_names=TARGET_QM_NAMES,
                seed=seed,
                params=params,
                qualities=qualities,
                pos=pos,
                o_nfs_path=o_nfs_path,
            )
