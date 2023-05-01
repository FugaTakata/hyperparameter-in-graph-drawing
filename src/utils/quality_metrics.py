# Third Party Library
from egraph import crossing_edges, warshall_floyd

# First Party Library
from config import const
from quality_metrics import (
    angular_resolution,
    aspect_ratio,
    crossing_angle,
    crossing_number,
    gabriel_graph_property,
    ideal_edge_lengths,
    neighborhood_preservation,
    node_resolution,
    stress,
)


def measure_qualities(
    target_qm_names,
    eg_graph,
    eg_drawing,
    eg_crossings=None,
    eg_distance_matrix=None,
):
    if eg_distance_matrix is None and (
        "ideal_edge_lengths" in target_qm_names or "stress" in target_qm_names
    ):
        eg_distance_matrix = warshall_floyd(
            eg_graph, lambda _: const.EDGE_WEIGHT
        )
    if eg_crossings is None and (
        "crossing_angle" in target_qm_names
        or "crossing_number" in target_qm_names
    ):
        eg_crossings = crossing_edges(eg_graph, eg_drawing)

    qualities = {}
    for qm_name in target_qm_names:
        if qm_name == "angular_resolution":
            qualities[qm_name] = angular_resolution.quality(
                eg_graph=eg_graph, eg_drawing=eg_drawing
            )
        elif qm_name == "aspect_ratio":
            qualities[qm_name] = aspect_ratio.quality(eg_drawing=eg_drawing)
        elif qm_name == "crossing_angle":
            qualities[qm_name] = crossing_angle.quality(
                eg_graph=eg_graph,
                eg_drawing=eg_drawing,
                eg_crossings=eg_crossings,
            )
        elif qm_name == "crossing_number":
            qualities[qm_name] = crossing_number.quality(
                eg_graph=eg_graph,
                eg_drawing=eg_drawing,
                eg_crossings=eg_crossings,
            )
        elif qm_name == "gabriel_graph_property":
            qualities[qm_name] = gabriel_graph_property.quality(
                eg_graph=eg_graph, eg_drawing=eg_drawing
            )
        elif qm_name == "ideal_edge_lengths":
            qualities[qm_name] = ideal_edge_lengths.quality(
                eg_graph=eg_graph,
                eg_drawing=eg_drawing,
                eg_distance_matrix=eg_distance_matrix,
            )
        elif qm_name == "node_resolution":
            qualities[qm_name] = node_resolution.quality(
                eg_graph=eg_graph, eg_drawing=eg_drawing
            )
        elif qm_name == "neighborhood_preservation":
            qualities[qm_name] = neighborhood_preservation.quality(
                eg_graph=eg_graph, eg_drawing=eg_drawing
            )
        elif qm_name == "stress":
            qualities[qm_name] = stress.quality(
                eg_graph=eg_graph,
                eg_drawing=eg_drawing,
                eg_distance_matrix=eg_distance_matrix,
            )

    return qualities
