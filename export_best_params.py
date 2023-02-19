# Standard Library
import argparse
import os

# Third Party Library
import optuna
import pandas as pd

# First Party Library
from utils.dataset import dataset_names

SS = "SS"
FR = "FR"

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


layout_name_abbreviations = [
    SS,
    FR,
]


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

df = pd.DataFrame()

for q in ALL_QUALITY_METRICS_NAMES:
    study = optuna.load_study(
        study_name=q,
        storage=f"sqlite:///db_opt_m/{args.l}/{args.d}/{q}.db",
    )
    params = study.best_trial.user_attrs["params"]
    new_df = pd.DataFrame([{"target": q, "params": params}])

    df = pd.concat([df, new_df])


direc = f"data/params_m/optimized/{args.l}/{args.d}/"
os.makedirs(direc, exist_ok=True)
pd.to_pickle(df, f"{direc}/opt.pkl")
df = pd.read_pickle(f"{direc}/opt.pkl")
for i, p in df.iterrows():
    dc = p.to_dict()
    print(dc["target"], dc["params"])
