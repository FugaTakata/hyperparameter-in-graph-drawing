# Third Party Library
import optuna
import pandas as pd
from egraph import Drawing, all_sources_bfs
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import (
    calc_hp_compare_score,
    draw_and_measure,
    ex_path,
    generate_seed_median_df,
    generate_sscalers,
)
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30

n_trials = 300
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
        a = "max_pivots=0.25n"

        db_uri = (
            f"sqlite:///{ex_path.joinpath('data/optimization/experiment.db')}"
        )
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        study = optuna.load_study(study_name=study_name, storage=db_uri)

        best_trials = []
        for trial in study.best_trials:
            trial_dict = {
                **trial.user_attrs["row_quality_metrics"],
                **trial.user_attrs["params"],
            }
            best_trials.append(trial_dict)

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

        dataset_path = get_dataset_path(d_name)
        nx_graph = nx_graph_preprocessing(
            load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
        )
        n_nodes = len(nx_graph.nodes)
        n_edges = len(nx_graph.edges)

        eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
        eg_distance_matrix = all_sources_bfs(eg_graph, EDGE_WEIGHT)

        pivots = 50
        iterations = 100
        eps = 0.1
        # print(pivots, iterations, eps)

        eg_drawing = Drawing.initial_placement(eg_graph)
        pos, e_quality_metrics = draw_and_measure(
            pivots=pivots,
            iterations=iterations,
            eps=eps,
            eg_graph=eg_graph,
            eg_indices=eg_indices,
            eg_drawing=eg_drawing,
            eg_distance_matrix=eg_distance_matrix,
            edge_weight=EDGE_WEIGHT,
            seed=0,
            n_nodes=n_nodes,
            n_edges=n_edges,
        )

        data = []
        best_df = pd.DataFrame(best_trials)
        rows = list(best_df.iterrows())
        for _, trial_a in rows:
            qa = dict([(qm_name, trial_a[qm_name]) for qm_name in qm_names])
            score = calc_hp_compare_score(
                qa=qa,
                qb=e_quality_metrics,
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
        n_best = len(best_df)

        print(
            d_name,
            n_win,
            n_even,
            n_lose,
            n_win / n_best,
            n_even / n_best,
            n_lose / n_best,
        )


if __name__ == "__main__":
    main()
