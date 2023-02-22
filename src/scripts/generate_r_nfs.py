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
    parser.add_argument("--n-params", type=int, required=True, help="n params")
    parser.add_argument("--n-seed", type=int, required=True, help="n seed")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    STEM = args.stem
    D = args.d
    L = args.l
    N_PARAMS = args.n_params
    N_SEED = args.n_seed

    filename = f"{STEM}.pkl"

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
            params_id = uuid.get_uuid()
            parameters = {
                "edge_length": const.EDGE_WEIGHT,
                "number_of_pivots": random.randint(
                    parameters.domain_ss["number_of_pivots"]["l"],
                    parameters.domain_ss["number_of_pivots"]["u"],
                ),
                "number_of_iterations": random.randint(
                    parameters.domain_ss["number_of_iterations"]["l"],
                    parameters.domain_ss["number_of_iterations"]["u"],
                ),
                "eps": random.uniform(
                    parameters.domain_ss["eps"]["l"],
                    parameters.domain_ss["eps"]["u"],
                ),
            }

            for _ in trange(N_SEED):
                seed = random.randint(0, const.RAND_MAX)
                pos, qualities = drawing_and_qualities.ss(
                    nx_graph=nx_graph,
                    eg_graph=eg_graph,
                    eg_indices=eg_indices,
                    params=parameters,
                    shortest_path_length=shortest_path_length,
                    seed=seed,
                    edge_weight=const.EDGE_WEIGHT,
                )

                save.r_nfs(
                    params_id=params_id,
                    seed=seed,
                    params=parameters,
                    qualities=qualities,
                    pos=pos,
                    r_nfs_path=r_nfs_path,
                )
