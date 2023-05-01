# First Party Library
from layouts import sgd
from utils import quality_metrics


def ss(
    nx_graph,
    eg_graph,
    eg_indices,
    params,
    shortest_path_length,
    seed,
    edge_weight,
):
    pos = sgd.sgd(
        eg_graph=eg_graph, eg_indices=eg_indices, params=params, seed=seed
    )

    qualities = quality_metrics.measure_qualities(
        nx_graph=nx_graph,
        pos=pos,
        shortest_path_length=shortest_path_length,
        edge_weight=edge_weight,
    )

    return pos, qualities
