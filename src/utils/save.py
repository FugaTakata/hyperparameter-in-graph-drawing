# Third Party Library
import pandas as pd

# First Party Library
from utils import uuid


def e_nfs(target_qm_names, seed, params, qualities, pos, e_nfs_path):
    data_id = uuid.get_uuid()
    base_df = pd.DataFrame()
    if e_nfs_path.exists():
        base_df = pd.read_pickle(e_nfs_path)

    new_df = pd.DataFrame(
        [
            {
                "id": data_id,
                "target_qm_names": target_qm_names,
                "seed": seed,
                "params": params,
                "qualities": qualities,
                "pos": pos,
            }
        ]
    )

    df = pd.concat([base_df, new_df])
    df.to_pickle(e_nfs_path)


def r_nfs(params_id, seed, params, qualities, pos, r_nfs_path):
    data_id = uuid.get_uuid()
    base_df = pd.DataFrame()
    if r_nfs_path.exists():
        base_df = pd.read_pickle(r_nfs_path)

    new_df = pd.DataFrame(
        [
            {
                "id": data_id,
                "params_id": params_id,
                "seed": seed,
                "params": params,
                "qualities": qualities,
                "pos": pos,
            }
        ]
    )

    df = pd.concat([base_df, new_df])
    df.to_pickle(r_nfs_path)


def o_nfs(
    params_id, target_qm_names, seed, params, qualities, pos, o_nfs_path
):
    data_id = uuid.get_uuid()
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
