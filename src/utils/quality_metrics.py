# First Party Library
from config import quality_metrics
from quality_metrics import (
    angular_resolution,
    aspect_ratio,
    crossing_angle,
    crossing_number,
    gabriel_graph_property,
    ideal_edge_length,
    node_resolution,
    shape_based_metrics,
    stress,
)
from utils import edge_crossing_finder


def measure_qualities(
    nx_graph,
    pos,
    shortest_path_length,
    edge_weight,
):
    qualities = {}
    edge_crossing = edge_crossing_finder.edge_crossing_finder(
        nx_graph=nx_graph, pos=pos
    )
    for qm_name in quality_metrics.ALL_QM_NAMES:
        if qm_name == "angular_resolution":
            qualities[qm_name] = angular_resolution.quality(
                nx_graph=nx_graph, pos=pos
            )
        elif qm_name == "aspect_ratio":
            qualities[qm_name] = aspect_ratio.quality(
                nx_graph=nx_graph, pos=pos
            )
        elif qm_name == "crossing_angle":
            qualities[qm_name] = crossing_angle.quality(
                nx_graph=nx_graph, pos=pos, edge_crossing=edge_crossing
            )
        elif qm_name == "crossing_number":
            qualities[qm_name] = crossing_number.quality(
                nx_graph=nx_graph, pos=pos, edge_crossing=edge_crossing
            )
        elif qm_name == "gabriel_graph_property":
            qualities[qm_name] = gabriel_graph_property.quality(
                nx_graph=nx_graph, pos=pos
            )
        elif qm_name == "ideal_edge_length":
            qualities[qm_name] = ideal_edge_length.quality(
                nx_graph=nx_graph,
                pos=pos,
                shortest_path_length=shortest_path_length,
            )
        elif qm_name == "node_resolution":
            qualities[qm_name] = node_resolution.quality(pos=pos)
        elif qm_name == "shape_based_metrics":
            qualities[qm_name] = shape_based_metrics.quality(
                nx_graph=nx_graph, pos=pos, edge_weight=edge_weight
            )
        elif qm_name == "stress":
            qualities[qm_name] = stress.quality(
                nx_graph=nx_graph,
                pos=pos,
                shortest_path_length=shortest_path_length,
            )

    return qualities
