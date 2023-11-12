# Third Party Library
import numpy as np
import pandas as pd
from egraph import Rng, SparseSgd, crossing_edges

# Local Library
from .config.paths import root_path
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
)

ex_path = root_path.joinpath("experiments/regression_analysis/")


N_SPLIT = 20
pivots_v, iterations_v, eps_v = np.meshgrid(
    np.linspace(1, 100, N_SPLIT, dtype=int),
    np.linspace(1, 200, N_SPLIT, dtype=int),
    np.logspace(np.log10(0.01), np.log10(1), N_SPLIT),
    indexing="ij",
)


def measure_quality_metrics(
    eg_graph, eg_drawing, eg_crossings, eg_distance_matrix
):
    return {
        "angular_resolution": -angular_resolution.measure(
            eg_graph=eg_graph, eg_drawing=eg_drawing
        ),
        "aspect_ratio": aspect_ratio.measure(eg_drawing=eg_drawing),
        "crossing_angle": -crossing_angle.measure(
            eg_graph=eg_graph,
            eg_drawing=eg_drawing,
            eg_crossings=eg_crossings,
        ),
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
    }


def sgd(
    eg_graph,
    eg_indices,
    eg_drawing,
    params,
    seed,
    edge_weight,
):
    rng = Rng.seed_from(seed)
    sparse_sgd = SparseSgd(
        eg_graph,
        lambda _: edge_weight,
        params["pivots"],
        rng,
    )
    scheduler = sparse_sgd.scheduler(
        params["iterations"],
        params["eps"],
    )

    def step(eta):
        sparse_sgd.shuffle(rng)
        sparse_sgd.apply(eg_drawing, eta)

    scheduler.run(step)

    pos = {
        u: (eg_drawing.x(i), eg_drawing.y(i)) for u, i in eg_indices.items()
    }

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
):
    params = {
        "pivots": pivots,
        "iterations": iterations,
        "eps": eps,
    }
    pos = sgd(
        eg_graph=eg_graph,
        eg_indices=eg_indices,
        eg_drawing=eg_drawing,
        params=params,
        seed=seed,
        edge_weight=edge_weight,
    )

    eg_crossings = crossing_edges(eg_graph, eg_drawing)
    quality_metrics = measure_quality_metrics(
        eg_graph=eg_graph,
        eg_drawing=eg_drawing,
        eg_crossings=eg_crossings,
        eg_distance_matrix=eg_distance_matrix,
    )

    return params, quality_metrics, pos


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
