# Standard Library

# Standard Library
import argparse
import random
import uuid

# Third Party Library
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.share import draw_and_measure, ex_path, generate_df_data
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)
from tqdm import tqdm

EDGE_WEIGHT = 30
N_SEED = 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-n", type=int, required=True, help="n params")

    args = parser.parse_args()

    export_path = ex_path.joinpath(
        f"results/baselines/randomized/{args.d}_{uuid.uuid4()}.pkl"
    )
    export_path.parent.mkdir(parents=True, exist_ok=True)

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )

    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)

    export_df_data = []
    for _ in tqdm(range(args.n)):
        pivots = random.randint(1, 100)
        iterations = random.randint(1, 200)
        eps = random.uniform(0.01, 1)
        for seed in tqdm(range(N_SEED), leave=False):
            eg_drawing = Drawing.initial_placement(eg_graph)

            params, quality_metrics = draw_and_measure(
                pivots=pivots,
                iterations=iterations,
                eps=eps,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                eg_drawing=eg_drawing,
                eg_distance_matrix=eg_distance_matrix,
                edge_weight=EDGE_WEIGHT,
                seed=seed,
            )

            export_df_data.append(
                generate_df_data(
                    params=params,
                    quality_metrics=quality_metrics,
                    seed=seed,
                    edge_weight=EDGE_WEIGHT,
                ),
            )

        export_df = pd.DataFrame(export_df_data)
        if export_path.exists():
            export_df = pd.concat([pd.read_pickle(export_path), export_df])
        export_df.to_pickle(export_path)
        export_df_data = []


if __name__ == "__main__":
    main()
