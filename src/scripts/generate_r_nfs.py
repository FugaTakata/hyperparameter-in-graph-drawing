# Standard Library
import argparse

# Third Party Library
from tqdm import trange

# First Party Library
from config import const, dataset, layout, paths
from generators import graph as graph_generator
from generators import r_nfs
from utils import graph, uuid


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", choices=dataset.DATASET_NAMES, required=True, help="dataset name"
    )
    parser.add_argument(
        "-l", choices=layout.LAYOUT_NAMES, required=True, help="layout name"
    )
    parser.add_argument("--n-params", type=int, required=True, help="n params")
    parser.add_argument("--n-seed", type=int, required=True, help="n seed")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    D = args.d
    L = args.l
    N_PARAMS = args.n_params
    N_SEED = args.n_seed

    file_id = uuid.get_uuid()
    filename = f"{file_id}.pkl"

    dataset_path = paths.get_dataset_path(dataset_name=D)

    r_nfs_path = paths.get_r_nfs_path(
        dataset_name=D, layout_name=L, filename=filename
    )

    nx_graph = graph.load_nx_graph(
        dataset_name=D, edge_weight=const.EDGE_WEIGHT
    )
    shortest_path_length = graph.get_shortest_path_length(nx_graph=nx_graph)

    if L == layout.SS:
        eg_graph, eg_indices = graph_generator.egraph_graph(nx_graph=nx_graph)
        for _ in trange(N_PARAMS):
            r_nfs.ss(
                nx_graph=nx_graph,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                shortest_path_length=shortest_path_length,
                r_nfs_path=r_nfs_path,
                n_seed=N_SEED,
                edge_weight=const.EDGE_WEIGHT,
            )
