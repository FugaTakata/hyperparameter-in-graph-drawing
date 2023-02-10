# Standard Library
import argparse
import os

# Third Party Library
import pandas as pd

# First Party Library
from utils.dataset import dataset_names

SS = "SS"

ALL_QUALITY_METRICS_NAMES = [
    "angular_resolution",
    "aspect_ratio",
    "crossing_angle",
    "crossing_number",
    "gabriel_graph_property",
    "ideal_edge_length",
    "node_resolution",
    # "run_time",
    "shape_based_metrics",
    "stress",
]


layout_name_abbreviations = [SS]


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", choices=dataset_names, required=True, help="dataset name"
)
parser.add_argument(
    "-l",
    choices=layout_name_abbreviations,
    required=True,
    help="layout name",
)

args = parser.parse_args()


export_directory = f"data/experienced/{args.l}/{args.d}"
df = pd.DataFrame()
filenames = os.listdir(export_directory)
for name in filenames:
    if ".pkl" in name and "ignore" not in name:
        df = pd.concat([df, pd.read_pickle(f"{export_directory}/{name}")])
df.info()

df.to_pickle(f"{export_directory}/ignore_50fs.pkl")
