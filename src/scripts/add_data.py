# Standard Library
import argparse
from itertools import product

# Third Party Library
import optuna
import pandas as pd
from egraph import Coordinates, warshall_floyd
from optuna.distributions import FloatDistribution, IntDistribution
from tqdm import tqdm

# First Party Library
from config import const, dataset, layout, parameters, paths, quality_metrics
from generators import graph as graph_generator
from layouts import sgd
from utils import graph, uuid


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--uuid", required=True, help="uuid")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    UUID = args.uuid

    P_NAMES = ["number_of_pivots", "number_of_iterations", "eps"]

    for L in layout.LAYOUT_NAMES:
        for D in dataset.DATASET_NAMES:
            data_dir = paths.get_data_dir(
                layout_name=L, dataset_name=D, uuid=UUID
            )
            if not data_dir.exists():
                continue

            df = pd.DataFrame()

            for i in range(4):
                grid_data_path = data_dir.joinpath("grid").joinpath(
                    f"20split-{i}.pkl"
                )
                df = pd.concat([df, pd.read_pickle(grid_data_path)])
            for qm_name in quality_metrics.ALL_QM_NAMES:
                db_path = data_dir.joinpath("grid").joinpath("data.sql")
                study = optuna.create_study(
                    storage=f"sqlite:///{db_path.resolve()}",
                    study_name=qm_name,
                    direction=quality_metrics.QUALITY_METRICS_MAP[
                        qm_name
                    ].direction,
                    load_if_exists=True,
                )
                trials = []
                for row in tqdm(df.itertuples()):
                    params = row.params
                    if "edge_length" in params:
                        del params["edge_length"]
                    qualities = row.qualities

                    trial = optuna.trial.create_trial(
                        params=params,
                        distributions={
                            "number_of_pivots": IntDistribution(0, 100),
                            "number_of_iterations": IntDistribution(1, 200),
                            "eps": FloatDistribution(0.01, 1),
                        },
                        value=qualities[qm_name],
                    )
                    trials.append(trial)
                study.add_trials(trials=trials)
