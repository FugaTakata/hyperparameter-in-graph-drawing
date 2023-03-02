# Standard Library
import argparse
from itertools import product

# Third Party Library
import pandas as pd
from egraph import Coordinates, warshall_floyd
from tqdm import tqdm

# First Party Library
from config import const, dataset, layout, parameters, paths, quality_metrics
from generators import graph as graph_generator
from layouts import sgd
from utils import graph, uuid
from utils.quality_metrics import measure_qualities


def save(params_id, seed, params, qualities, path):
    data_id = uuid.get_uuid()
    base_df = pd.DataFrame()
    if path.exists():
        base_df = pd.read_pickle(path)

    new_df = pd.DataFrame(
        [
            {
                "id": data_id,
                "params_id": params_id,
                "seed": seed,
                "params": params,
                "qualities": qualities,
            }
        ]
    )

    df = pd.concat([base_df, new_df])
    df.to_pickle(path)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--n-slice", type=int, required=True, help="n slice")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    N_SLICE = args.n_slice

    UUID = "cd7c1537-2ebe-4434-9ead-f7b1a866815a"

    P_NAMES = ["number_of_pivots", "number_of_iterations", "eps"]
    N_SPLIT = 20

    params_steps = {
        "number_of_pivots": 5,
        "number_of_iterations": 10,
        "eps": 0.05,
    }

    params_candidates = {}
    for p_name in P_NAMES:
        lower = parameters.domain_ss[p_name]["l"]
        upper = parameters.domain_ss[p_name]["u"]

        params_candidates[p_name] = [
            v * params_steps[p_name] for v in list(range(1, 20 + 1))
        ]

    params_list = [
        {
            "edge_length": const.EDGE_WEIGHT,
            "number_of_pivots": number_of_pivots,
            "number_of_iterations": number_of_iterations,
            "eps": eps,
        }
        for number_of_pivots, number_of_iterations, eps in list(
            product(*[params_candidates[p_name] for p_name in P_NAMES])
        )
    ]

    for L in layout.LAYOUT_NAMES:
        for D in dataset.DATASET_NAMES:
            data_dir = paths.get_data_dir(
                layout_name=L, dataset_name=D, uuid=UUID
            )
            if not data_dir.exists():
                continue

            dataset_path = paths.get_dataset_path(dataset_name=D)

            nx_graph = graph.load_nx_graph(
                dataset_name=D, edge_weight=const.EDGE_WEIGHT
            )
            eg_graph, eg_indices = graph_generator.egraph_graph(
                nx_graph=nx_graph
            )
            eg_distance_matrix = warshall_floyd(
                eg_graph, lambda _: const.EDGE_WEIGHT
            )

            grid_data_path = data_dir.joinpath("grid").joinpath(
                f"{N_SPLIT}split-{N_SLICE}.pkl"
            )
            n = len(params_list) // 4
            for params in tqdm(params_list[n * N_SLICE : n * (N_SLICE + 1)]):
                print(params)
                params_id = uuid.get_uuid()
                seed = 0
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

                save(
                    params_id=params_id,
                    seed=seed,
                    params=params,
                    qualities=qualities,
                    path=grid_data_path,
                )
