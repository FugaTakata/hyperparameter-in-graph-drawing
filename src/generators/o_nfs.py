# Standard Library

# Standard Library
import random

# Third Party Library
import optuna
import pandas as pd
from tqdm import trange

# First Party Library
from config import const
from generators import drawing_and_qualities
from utils.uuid import get_uuid


def save(params_id, target_qm_names, seed, params, qualities, pos, o_nfs_path):
    data_id = get_uuid()
    base_df = pd.DataFrame()
    if o_nfs_path.exists():
        base_df = pd.read_pickle(o_nfs_path)

    new_df = pd.DataFrame(
        [
            {
                "id": data_id,
                "params_id": params_id,
                "target_qm_names": target_qm_names,
                "seed": seed,
                "params": params,
                "qualities": qualities,
                "pos": pos,
            }
        ]
    )

    df = pd.concat([base_df, new_df])
    df.to_pickle(o_nfs_path)


def ss(
    nx_graph,
    eg_graph,
    eg_indices,
    target_qm_names,
    database_uri,
    shortest_path_length,
    o_nfs_path,
    n_seed,
    edge_weight,
):
    params_id = get_uuid()
    study = optuna.load_study(
        study_name=",".join(target_qm_names), storage=database_uri
    )
    params = study.best_trial.user_attrs["params"]

    for _ in trange(n_seed):
        seed = random.randint(0, const.RAND_MAX)
        pos, qualities = drawing_and_qualities.ss(
            nx_graph=nx_graph,
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            params=params,
            shortest_path_length=shortest_path_length,
            seed=seed,
            edge_weight=edge_weight,
        )

        save(
            params_id=params_id,
            target_qm_names=target_qm_names,
            seed=seed,
            params=params,
            qualities=qualities,
            pos=pos,
            o_nfs_path=o_nfs_path,
        )
