# Standard Library
import argparse
import random

# First Party Library
from config import const, dataset, layout, quality_metrics
from optimizers import single


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--database-uri", required=True, help="study storage uri"
    )
    parser.add_argument(
        "-d", choices=dataset.DATASET_NAMES, required=True, help="dataset name"
    )
    parser.add_argument(
        "-l", choices=layout.LAYOUT_NAMES, required=True, help="layout name"
    )
    parser.add_argument(
        "--n-trials", type=int, required=True, help="n trials on optimization"
    )
    parser.add_argument(
        "--n-means", type=int, required=True, help="n seed per trial"
    )
    parser.add_argument(
        "--fixed-seed", action="store_true", help="use fixed seed"
    )
    parser.add_argument(
        "-t",
        choices=quality_metrics.ALL_QM_NAMES,
        nargs="*",
        required=True,
        help="target quality metrics names",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    DATABASE_URI = args.database_uri
    D = args.d
    L = args.l
    N_TRIALS = args.n_trials
    N_MEANS = args.n_means
    FIXED_SEED = args.fixed_seed
    TARGET_QM_NAMES = args.t

    if (not FIXED_SEED) and 1 < N_MEANS:
        raise ValueError("n means must be 1 when seed fixed")

    study_name = ",".join(TARGET_QM_NAMES)

    def generate_seed():
        seed = random.randint(0, const.RAND_MAX) if FIXED_SEED else 0

        return seed

    single.ss(
        dataset_name=D,
        database_uri=DATABASE_URI,
        study_name=study_name,
        n_trials=N_TRIALS,
        n_means=N_MEANS,
        generate_seed=generate_seed,
        target_qm_names=TARGET_QM_NAMES,
        edge_weight=const.EDGE_WEIGHT,
    )
