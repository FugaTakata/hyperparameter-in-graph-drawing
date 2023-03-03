# Standard Library
import argparse
import random

# Third Party Library
import optuna
from egraph import Coordinates, warshall_floyd
from tqdm import trange

# First Party Library
from config import const, dataset, layout, paths, quality_metrics
from generators import graph as graph_generator
from layouts import sgd
from utils import graph, save, uuid
from utils.quality_metrics import measure_qualities


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--uuid", required=True, help="uuid")
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

    UUID = args.uuid
    DB_STEM = args.db_stem
    D = args.d
    L = args.l
    N_SEED = args.n_seed
    TARGET_QM_NAMES = sorted(args.t)

    filename = f"op-{N_SEED}nfs-{','.join(TARGET_QM_NAMES)}-{DB_STEM}.pkl"

    dataset_path = paths.get_dataset_path(dataset_name=D)

    o_nfs_path = paths.get_o_nfs_path(
        dataset_name=D, layout_name=L, filename=filename, uuid=UUID
    )

    nx_graph = graph.load_nx_graph(
        dataset_name=D, edge_weight=const.EDGE_WEIGHT
    )

    database_name = f"{DB_STEM}.sql"
    optimization_path = paths.get_optimization_path(
        layout_name=L, dataset_name=D, filename=database_name, uuid=UUID
    )
    database_uri = f"sqlite:///{optimization_path.resolve()}"

    if L == layout.SS:
        eg_graph, eg_indices = graph_generator.egraph_graph(nx_graph=nx_graph)
        eg_distance_matrix = warshall_floyd(
            eg_graph, lambda _: const.EDGE_WEIGHT
        )

        params_id = uuid.get_uuid()
        study = optuna.load_study(
            study_name=",".join(TARGET_QM_NAMES), storage=database_uri
        )
        params = study.best_trial.user_attrs["params"]

        for _ in trange(N_SEED):
            seed = random.randint(0, const.RAND_MAX)
            eg_drawing = Coordinates.initial_placement(eg_graph)

            pos = sgd.sgd(
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                eg_drawing=eg_drawing,
                params=params,
                seed=seed,
            )
            qualities = measure_qualities(
                target_qm_names=quality_metrics.ALL_QM_NAMES,
                eg_graph=eg_graph,
                eg_drawing=eg_drawing,
                eg_distance_matrix=eg_distance_matrix,
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
