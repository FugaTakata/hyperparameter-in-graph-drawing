# Standard Library
import math

# Third Party Library
import numpy as np
import pandas as pd
from egraph import Rng, SparseSgd, crossing_edges
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Local Library
from .config.paths import root_path
from .config.quality_metrics import qm_names
from .quality_metrics import (
    angular_resolution,
    aspect_ratio,
    crossing_angle,
    crossing_number,
    gabriel_graph_property,
    ideal_edge_length,
    neighborhood_preservation,
    node_resolution,
    stress,
    time_complexity,
)

ex_path = root_path.joinpath("experiments/japan-vis/")


def measure_quality_metrics(
    pivots,
    iterations,
    eg_graph,
    eg_drawing,
    eg_crossings,
    eg_distance_matrix,
    n_nodes,
    n_edges,
):
    quality_metrics = {
        "angular_resolution": -angular_resolution.measure(
            eg_graph=eg_graph, eg_drawing=eg_drawing
        ),
        "aspect_ratio": aspect_ratio.measure(eg_drawing=eg_drawing),
        "crossing_number": -crossing_number.measure(
            eg_graph=eg_graph,
            eg_drawing=eg_drawing,
            eg_crossings=eg_crossings,
        ),
        "gabriel_graph_property": -gabriel_graph_property.measure(
            eg_graph=eg_graph, eg_drawing=eg_drawing
        ),
        "ideal_edge_length": -ideal_edge_length.measure(
            eg_graph=eg_graph,
            eg_drawing=eg_drawing,
            eg_distance_matrix=eg_distance_matrix,
        ),
        "neighborhood_preservation": neighborhood_preservation.measure(
            eg_graph=eg_graph, eg_drawing=eg_drawing
        ),
        "node_resolution": -node_resolution.measure(eg_drawing=eg_drawing),
        "stress": -stress.measure(
            eg_drawing=eg_drawing,
            eg_distance_matrix=eg_distance_matrix,
        ),
        "time_complexity": -time_complexity.measure(
            pivots=pivots,
            iterations=iterations,
            n_nodes=n_nodes,
            n_edges=n_edges,
        ),
    }

    quality_metrics["crossing_angle"] = -crossing_angle.measure(
        eg_graph=eg_graph,
        eg_drawing=eg_drawing,
        eg_crossings=eg_crossings,
        crossing_number=quality_metrics["crossing_number"],
    )

    return quality_metrics


def sgd(
    pivots,
    iterations,
    eps,
    eg_graph,
    eg_indices,
    eg_drawing,
    seed,
    edge_weight,
):
    rng = Rng.seed_from(seed)
    sparse_sgd = SparseSgd(
        eg_graph,
        lambda _: edge_weight,
        pivots,
        rng,
    )
    scheduler = sparse_sgd.scheduler(
        iterations,
        eps,
    )

    def step(eta):
        sparse_sgd.shuffle(rng)
        sparse_sgd.apply(eg_drawing, eta)

    scheduler.run(step)

    pos = {
        u: (eg_drawing.x(i), eg_drawing.y(i)) for u, i in eg_indices.items()
    }

    return pos


def draw(
    pivots,
    iterations,
    eps,
    eg_graph,
    eg_indices,
    eg_drawing,
    edge_weight,
    seed,
):
    pos = sgd(
        pivots=pivots,
        iterations=iterations,
        eps=eps,
        eg_graph=eg_graph,
        eg_indices=eg_indices,
        eg_drawing=eg_drawing,
        seed=seed,
        edge_weight=edge_weight,
    )

    return pos


def draw_and_measure(
    pivots,
    iterations,
    eps,
    eg_graph,
    eg_indices,
    eg_drawing,
    eg_distance_matrix,
    edge_weight,
    seed,
    n_nodes,
    n_edges,
):
    pos = draw(
        pivots=pivots,
        iterations=iterations,
        eps=eps,
        eg_graph=eg_graph,
        eg_indices=eg_indices,
        eg_drawing=eg_drawing,
        edge_weight=edge_weight,
        seed=seed,
    )

    eg_crossings = crossing_edges(eg_graph, eg_drawing)
    quality_metrics = measure_quality_metrics(
        pivots=pivots,
        iterations=iterations,
        eg_graph=eg_graph,
        eg_drawing=eg_drawing,
        eg_crossings=eg_crossings,
        eg_distance_matrix=eg_distance_matrix,
        n_nodes=n_nodes,
        n_edges=n_edges,
    )

    return pos, quality_metrics


def draw_and_measure_scaled(
    pivots,
    iterations,
    eps,
    eg_graph,
    eg_indices,
    eg_drawing,
    eg_distance_matrix,
    edge_weight,
    seed,
    n_nodes,
    n_edges,
    scalers,
):
    pos, quality_metrics = draw_and_measure(
        pivots=pivots,
        iterations=iterations,
        eps=eps,
        eg_graph=eg_graph,
        eg_indices=eg_indices,
        eg_drawing=eg_drawing,
        eg_distance_matrix=eg_distance_matrix,
        edge_weight=edge_weight,
        seed=seed,
        n_nodes=n_nodes,
        n_edges=n_edges,
    )

    scaled_quality_metrics = {}
    for qm_name in qm_names:
        scaled_quality_metrics[qm_name] = scalers[qm_name].transform(
            [[quality_metrics[qm_name]]]
        )[0][0]

    return pos, quality_metrics, scaled_quality_metrics


def generate_base_df_data(
    params,
    quality_metrics,
    seed,
    edge_weight,
):
    df_data = dict(
        [[f"params_{k}", params[k]] for k in params]
        + [[f"values_{k}", quality_metrics[k]] for k in quality_metrics]
        + [["seed", seed]]
        + [["edge_weight", edge_weight]]
    )

    return df_data


def calc_bounds(pos):
    xs = [pos[key][0] for key in pos]
    ys = [pos[key][1] for key in pos]

    x_bounds = (min(xs), max(xs))
    y_bounds = (min(ys), max(ys))

    return x_bounds, y_bounds


def generate_hp_grid(n_split, n_nodes):
    pivots_v, iterations_v, eps_v = np.meshgrid(
        np.array(
            list(
                map(
                    int,
                    map(
                        lambda x: min(x, n_nodes),
                        map(
                            math.ceil,
                            np.logspace(
                                np.log10(1), np.log10(n_nodes), n_split
                            ),
                        ),
                    ),
                )
            )
        ),
        np.linspace(1, 200, n_split, dtype=int),
        np.logspace(np.log10(0.01), np.log10(1), n_split),
        indexing="ij",
    )

    return pivots_v, iterations_v, eps_v


def generate_seed_median_df(df):
    median_df = (
        df.groupby(["params_pivots", "params_iterations", "params_eps"])
        .agg(
            dict(
                [(f"values_{qm_name}", "median") for qm_name in qm_names]
                + [("edge_weight", "first")]
            )
        )
        .reset_index()
        .sort_index(axis=1)
    )

    return median_df


def generate_sscalers(dataset_paths):
    df = pd.concat(
        [pd.read_pickle(dataset_path) for dataset_path in dataset_paths]
    )

    median_df = generate_seed_median_df(df)

    sscalers = {}
    for qm_name in qm_names:
        sscalers[qm_name] = StandardScaler()
        sscalers[qm_name] = sscalers[qm_name].fit(
            median_df[f"values_{qm_name}"].values.reshape(-1, 1)
        )

    return sscalers


def generate_mmscalers(dataset_paths):
    df = pd.concat(
        [pd.read_pickle(dataset_path) for dataset_path in dataset_paths]
    )

    median_df = generate_seed_median_df(df)

    mmscalers = {}
    for qm_name in qm_names:
        mmscalers[qm_name] = MinMaxScaler()
        mmscalers[qm_name] = mmscalers[qm_name].fit(
            median_df[f"values_{qm_name}"].values.reshape(-1, 1)
        )

    return mmscalers


def rate2pivots(rate, n_nodes):
    return max(1, int(n_nodes * rate))
