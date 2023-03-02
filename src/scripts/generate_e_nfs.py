# Standard Library
import argparse
import random

# Third Party Library
from egraph import Coordinates, warshall_floyd
from tqdm import trange

# First Party Library
from config import const, dataset, layout, parameters, paths, quality_metrics
from generators import graph as graph_generator
from layouts import sgd
from utils import graph, save
from utils.quality_metrics import measure_qualities


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--uuid", required=True, help="uuid")
    parser.add_argument("--stem", required=True, help="export file stem")
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

    UUID = args.uuid
    STEM = args.stem
    D = args.d
    L = args.l
    N_SEED = args.n_seed

    filename = f"{STEM}.pkl"

    dataset_path = paths.get_dataset_path(dataset_name=D)

    e_nfs_path = paths.get_e_nfs_path(
        dataset_name=D, layout_name=L, filename=filename, uuid=UUID
    )

    nx_graph = graph.load_nx_graph(
        dataset_name=D, edge_weight=const.EDGE_WEIGHT
    )

    if L == layout.SS:
        eg_graph, eg_indices = graph_generator.egraph_graph(nx_graph=nx_graph)
        eg_distance_matrix = warshall_floyd(
            eg_graph, lambda _: const.EDGE_WEIGHT
        )

        params = {
            "edge_length": const.EDGE_WEIGHT,
            "number_of_pivots": parameters.empirical_ss["number_of_pivots"],
            "number_of_iterations": parameters.empirical_ss[
                "number_of_iterations"
            ],
            "eps": parameters.empirical_ss["eps"],
        }

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

            save.e_nfs(
                seed=seed,
                params=params,
                qualities=qualities,
                pos=pos,
                e_nfs_path=e_nfs_path,
            )
