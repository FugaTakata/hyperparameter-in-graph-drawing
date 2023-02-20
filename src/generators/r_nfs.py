# Standard Library
import random

# Third Party Library
import pandas as pd
from tqdm import trange

# First Party Library
from config import const, params_domains
from generators import drawing_and_qualities
from utils.uuid import get_uuid


def save(params_id, seed, params, qualities, pos, r_nfs_path):
    data_id = get_uuid()
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


def ss(
    nx_graph,
    eg_graph,
    eg_indices,
    shortest_path_length,
    r_nfs_path,
    n_seed,
    edge_weight,
):
    params_id = get_uuid()
    params = {
        "edge_length": edge_weight,
        "number_of_pivots": random.randint(
            params_domains.ss["number_of_pivots"]["l"],
            params_domains.ss["number_of_pivots"]["u"],
        ),
        "number_of_iterations": random.randint(
            params_domains.ss["number_of_iterations"]["l"],
            params_domains.ss["number_of_iterations"]["u"],
        ),
        "eps": random.uniform(
            params_domains.ss["eps"]["l"],
            params_domains.ss["eps"]["u"],
        ),
    }

    for _ in trange(n_seed):
        seed = random.randint(0, const.RAND_MAX)
        pos, qualities = drawing_and_qualities.ss(
            nx_graph=nx_graph,
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            params=params,
            shortest_path_length=shortest_path_length,
            edge_weight=edge_weight,
        )

        save(
            params_id=params_id,
            seed=seed,
            params=params,
            qualities=qualities,
            pos=pos,
            r_nfs_path=r_nfs_path,
        )
