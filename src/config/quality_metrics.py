# First Party Library
from quality_metrics import (
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

QUALITY_METRICS_MAP = {
    "angular_resolution": angular_resolution,
    "aspect_ratio": aspect_ratio,
    "crossing_angle": crossing_angle,
    "crossing_number": crossing_number,
    "gabriel_graph_property": gabriel_graph_property,
    "ideal_edge_length": ideal_edge_length,
    "node_resolution": node_resolution,
    # "run_time": run_time,
    "shape_based_metrics": neighborhood_preservation,
    "stress": stress,
}

ALL_QM_NAMES = sorted([name for name in QUALITY_METRICS_MAP])
