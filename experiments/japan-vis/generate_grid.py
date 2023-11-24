# Standard Library
import argparse
import math

# Third Party Library
import numpy as np
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.share import (
    draw_and_measure,
    ex_path,
    generate_base_df_data,
    pivots2rate,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)
from tqdm import tqdm

EDGE_WEIGHT = 30


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("-n", required=True, type=int, help="n split for grid")
    parser.add_argument("--seed", required=True, type=int, help="seed")

    args = parser.parse_args()

    n_split = args.n

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)
    p_max = max(1, int(n_nodes * 0.25))

    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)

    pivots_v, iterations_v, eps_v = np.meshgrid(
        np.array(
            list(
                map(
                    int,
                    map(
                        lambda x: min(x, p_max),
                        map(
                            math.ceil,
                            np.logspace(np.log10(1), np.log10(p_max), n_split),
                        ),
                    ),
                )
            )
        ),
        np.linspace(1, 200, n_split, dtype=int),
        np.logspace(np.log10(0.01), np.log10(1), n_split),
        indexing="ij",
    )

    export_df_data = []
    export_path = ex_path.joinpath(
        f"data/grid/{args.d}/n={args.n}/seed={args.seed}.pkl"
    )
    export_path.parent.mkdir(parents=True, exist_ok=True)
    for pi in tqdm(range(n_split)):
        for ii in tqdm(range(n_split), leave=False):
            for ei in tqdm(range(n_split), leave=False):
                pivots = pivots_v[pi, ii, ei]
                iterations = iterations_v[pi, ii, ei]
                eps = eps_v[pi, ii, ei]

                eg_drawing = Drawing.initial_placement(eg_graph)

                pos, quality_metrics = draw_and_measure(
                    pivots=pivots,
                    iterations=iterations,
                    eps=eps,
                    eg_graph=eg_graph,
                    eg_indices=eg_indices,
                    eg_drawing=eg_drawing,
                    eg_distance_matrix=eg_distance_matrix,
                    edge_weight=EDGE_WEIGHT,
                    seed=args.seed,
                    n_nodes=n_nodes,
                    n_edges=n_edges,
                )
                params = {
                    "pivots": pivots,
                    "pivots_rate": pivots2rate(pivots, n_nodes),
                    "iterations": iterations,
                    "eps": eps,
                }

                export_df_data.append(
                    {
                        **generate_base_df_data(
                            params=params,
                            quality_metrics=quality_metrics,
                            seed=args.seed,
                            edge_weight=EDGE_WEIGHT,
                        ),
                    },
                )
    export_df = pd.DataFrame(export_df_data)
    export_df.to_pickle(export_path)


if __name__ == "__main__":
    main()
