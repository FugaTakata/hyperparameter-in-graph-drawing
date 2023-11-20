# Local Library
from ..quality_metrics import (
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

qm_name_abbreviations = {
    "angular_resolution": "ANR",
    "aspect_ratio": "AR",
    "crossing_angle": "CA",
    "crossing_number": "CN",
    "gabriel_graph_property": "GG",
    "ideal_edge_length": "IE",
    "node_resolution": "NR",
    "neighborhood_preservation": "NP",
    "runtime": "RT",
    "stress": "ST",
    "time_complexity": "TC",
}

quality_metrics_map = {
    "angular_resolution": angular_resolution,
    "aspect_ratio": aspect_ratio,
    "crossing_angle": crossing_angle,
    "crossing_number": crossing_number,
    "gabriel_graph_property": gabriel_graph_property,
    "ideal_edge_length": ideal_edge_length,
    "neighborhood_preservation": neighborhood_preservation,
    "node_resolution": node_resolution,
    "stress": stress,
    "time_complexity": time_complexity,
}

qm_names = sorted([qm_name for qm_name in qm_name_abbreviations])
