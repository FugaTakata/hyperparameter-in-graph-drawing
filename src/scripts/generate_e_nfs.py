# Standard Library
import argparse
import random

# Third Party Library
from tqdm import trange

# First Party Library
from config import const, dataset, layout, parameters, paths
from generators import drawing_and_qualities
from generators import graph as graph_generator
from utils import graph, save, uuid


def get_args():
    parser = argparse.ArgumentParser()

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

    STEM = args.stem
    D = args.d
    L = args.l
    N_SEED = args.n_seed

    filename = f"{STEM}.pkl"

    dataset_path = paths.get_dataset_path(dataset_name=D)

    e_nfs_path = paths.get_e_nfs_path(
        dataset_name=D, layout_name=L, filename=filename
    )

    nx_graph = graph.load_nx_graph(
        dataset_name=D, edge_weight=const.EDGE_WEIGHT
    )
    shortest_path_length = graph.get_shortest_path_length(nx_graph=nx_graph)

    if L == layout.SS:
        eg_graph, eg_indices = graph_generator.egraph_graph(nx_graph=nx_graph)

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
            pos, qualities = drawing_and_qualities.ss(
                nx_graph=nx_graph,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                params=params,
                shortest_path_length=shortest_path_length,
                seed=seed,
                edge_weight=const.EDGE_WEIGHT,
            )

            save.e_nfs(
                seed=seed,
                params=params,
                qualities=qualities,
                pos=pos,
                e_nfs_path=e_nfs_path,
            )
