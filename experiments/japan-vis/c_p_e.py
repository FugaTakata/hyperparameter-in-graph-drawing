# Third Party Library
import json
import pandas as pd
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import (
    calc_hp_compare_score,
    ex_path,
    generate_seed_median_df,
    generate_sscalers,
)

EDGE_WEIGHT = 30

n_trials = 200
n_compare = 100
threshold = 0.05


def main():
    d_names = [
        "1138_bus",
        "USpowerGrid",
        "dwt_1005",
        "poli",
        "qh882",
        "3elt",
        "dwt_2680",
    ]
    print(
        "dataset",
        "win",
        "even",
        "lose",
        "win/all",
        "even/all",
        "lose/all",
    )
    for d_name in d_names:
        compare_results = [
            "dataset",
            "win",
            "even",
            "lose",
            "win/all",
            "even/all",
            "lose/all",
        ]
        a = "max_pivots=0.25n"

        seeds = list(range(10))
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        pareto_df_paths = [
            ex_path.joinpath(
                f"data/pareto/{d_name}/{study_name}/seed={seed}.pkl"
            )
            for seed in seeds
        ]
        pareto_df = pd.concat(
            [pd.read_pickle(path) for path in pareto_df_paths]
        )
        pareto_df = generate_seed_median_df(pareto_df)

        n_split = 10
        data_seeds = list(range(10))
        df_paths = [
            ex_path.joinpath(
                f"data/grid/{d_name}/n={n_split}/seed={data_seed}.pkl"
            )
            for data_seed in data_seeds
        ]
        df = pd.concat([pd.read_pickle(df_path) for df_path in df_paths])
        mdf = generate_seed_median_df(df)
        scalers = generate_sscalers(mdf)

        # empirical
        empirical_df_paths = [
            ex_path.joinpath(
                f"data/baseline/empirical/{d_name}/seed={seed}.pkl"
            )
            for seed in seeds
        ]
        empirical_df = pd.concat(
            [pd.read_pickle(path) for path in empirical_df_paths]
        )

        data = []
        rows = list(pareto_df.iterrows())
        for _, trial_a in rows:
            qa = dict(
                [
                    (qm_name, trial_a[f"values_{qm_name}"])
                    for qm_name in qm_names
                ]
            )
            qb = dict(
                [
                    (qm_name, empirical_df.iloc[0][f"values_{qm_name}"])
                    for qm_name in qm_names
                ]
            )
            score = calc_hp_compare_score(
                qa=qa,
                qb=qb,
                scalers=scalers,
                n_compare=n_compare,
            )

            data.append({"score": score})

        res_df = pd.DataFrame(data)
        win_con = res_df["score"] > 1 + threshold
        lose_con = res_df["score"] < 1 - threshold

        win_df = res_df[win_con]
        lose_df = res_df[lose_con]
        even_df = res_df[(~win_con) & (~lose_con)]

        n_win = len(win_df)
        n_lose = len(lose_df)
        n_even = len(even_df)
        n_best = len(pareto_df)

        print(
            d_name,
            n_win,
            n_even,
            n_lose,
            n_win / n_best,
            n_even / n_best,
            n_lose / n_best,
        )
        compare_results.append(
            [
                d_name,
                n_win,
                n_even,
                n_lose,
                n_win / n_best,
                n_even / n_best,
                n_lose / n_best,
            ]
        )

        compare_result_path = ex_path.joinpath(
            f"results/c_p_e/{d_name}/{study_name}/results.json"
        )
        compare_result_path.parent.mkdir(parents=True, exist_ok=True)
        with open(compare_result_path, mode="w") as f:
            json.dump(compare_results, f)


if __name__ == "__main__":
    main()
