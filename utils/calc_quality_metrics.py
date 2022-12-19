# First Party Library
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
from utils.edge_crossing_finder import edge_crossing_finder


def calc_qs(
    nx_graph,
    pos,
    all_pairs_shortest_path_length,
    target_quality_metrics_names,
    edge_weight,
):
    result = {}
    edge_crossing = None
    if (
        "crossing_angle" in target_quality_metrics_names
        or "crossing_number" in target_quality_metrics_names
    ):
        edge_crossing = edge_crossing_finder(nx_graph, pos)

    for qname in target_quality_metrics_names:
        if qname == "angular_resolution":
            result[qname] = angular_resolution.quality(nx_graph, pos)
        elif qname == "aspect_ratio":
            result[qname] = aspect_ratio.quality(nx_graph, pos)
        elif qname == "crossing_angle":
            result[qname] = crossing_angle.quality(
                nx_graph, pos, edge_crossing
            )
        elif qname == "crossing_number":
            result[qname] = crossing_number.quality(
                nx_graph, pos, edge_crossing
            )
        elif qname == "gabriel_graph_property":
            result[qname] = gabriel_graph_property.quality(nx_graph, pos)
        elif qname == "ideal_edge_length":
            result[qname] = ideal_edge_length.quality(
                nx_graph, pos, all_pairs_shortest_path_length
            )
        elif qname == "node_resolution":
            result[qname] = node_resolution.quality(pos)
        elif qname == "shape_based_metrics":
            result[qname] = shape_based_metrics.quality(
                nx_graph, pos, edge_weight
            )
        elif qname == "stress":
            result[qname] = stress.quality(
                nx_graph, pos, all_pairs_shortest_path_length
            )

    return result
