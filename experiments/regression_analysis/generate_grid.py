# Standard Library
import argparse

# Third Party Library
import pandas as pd
from egraph import Drawing, all_sources_bfs
from tqdm import tqdm
from utils.config.dataset import dataset_names
from utils.config.paths import get_dataset_path
from utils.graph import egraph_graph, load_nx_graph, nx_graph_preprocessing
from utils.share import (
    draw_and_measure,
    eps_v,
    ex_path,
    generate_base_df_data,
    iterations_v,
    pivots_v,
)

EDGE_WEIGHT = 30


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", choices=dataset_names, required=True, help="dataset name"
    )
    parser.add_argument(
        "--seeds", required=True, type=int, nargs="*", help="a list of seeds"
    )

    args = parser.parse_args()

    dataset_path = get_dataset_path(args.d)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )

    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)

    n_split = len(pivots_v)
    for seed in args.seeds:
        export_df_data = []
        export_path = ex_path.joinpath(
            f"results/grid/{args.d}_seed={args.s}.pkl"
        )
        export_path.parent.mkdir(parents=True, exist_ok=True)
        for pi in tqdm(range(n_split)):
            for ii in tqdm(range(n_split), leave=False):
                for ei in tqdm(range(n_split), leave=False):
                    pivots = pivots_v[pi, ii, ei]
                    iterations = iterations_v[pi, ii, ei]
                    eps = eps_v[pi, ii, ei]

                    eg_drawing = Drawing.initial_placement(eg_graph)

                    params, quality_metrics, pos = draw_and_measure(
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
                        {
                            **generate_base_df_data(
                                params=params,
                                quality_metrics=quality_metrics,
                                seed=seed,
                                edge_weight=EDGE_WEIGHT,
                            ),
                        },
                    )
        export_df = pd.DataFrame(export_df_data)
        export_df.to_pickle(export_path)


if __name__ == "__main__":
    main()
