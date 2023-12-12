# Standard Library
import argparse

# Third Party Library
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

EDGE_WEIGHT = 30


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument("--seed", required=True, type=int, help="seeds")

    args = parser.parse_args()

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )
    n_nodes = len(nx_graph.nodes)
    n_edges = len(nx_graph.edges)

    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)

    export_df_data = []
    export_path = ex_path.joinpath(f"data/tmp/{args.d}/seed={args.seed}.pkl")
    export_path.parent.mkdir(parents=True, exist_ok=True)

    pivots = 50
    iterations = 100
    eps = 0.1

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
