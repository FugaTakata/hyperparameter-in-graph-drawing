# Standard Library
import json

# Third Party Library
import matplotlib.pyplot as plt
import networkx as nx
from egraph import Drawing
from ex_utils.config.paths import get_dataset_path
from ex_utils.share import draw, ex_path
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)

EDGE_WEIGHT = 30


def main():
    seeds = list(range(10))

    d_names = [
        "1138_bus",
        "USpowerGrid",
        "dwt_1005",
        "poli",
        "qh882",
        "3elt",
        "dwt_2680",
    ]

    for d_name in d_names:
        dataset_path = get_dataset_path(d_name)
        nx_graph = nx_graph_preprocessing(
            load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
        )
        eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)

        # empirical
        pivots = 50
        iterations = 100
        eps = 0.1
        print(pivots, iterations, eps, d_name)
        for picture_seed in seeds:
            eg_drawing = Drawing.initial_placement(eg_graph)
            pos = draw(
                pivots=pivots,
                iterations=iterations,
                eps=eps,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                eg_drawing=eg_drawing,
                edge_weight=EDGE_WEIGHT,
                seed=picture_seed,
            )

            fig, ax = plt.subplots(dpi=300, facecolor="white")
            ax.set_aspect("equal")

            fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

            nx.draw(
                nx_graph,
                pos=pos,
                node_size=0.5,
                width=0.5,
                # node_color="#AB47BC",
                edge_color="#CFD8DC",
                ax=ax,
            )

            empirical_picture_path = ex_path.joinpath(
                f"results/picture/baseline/empirical/{d_name}/seed={picture_seed}.png"
            )
            empirical_picture_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(empirical_picture_path)
            plt.close()

        # best
        n_trials = 100
        for a in [
            "pref=1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0",
            "pref=1.0,2.0,1.0,1.0,2.0,2.0,2.0,1.0,2.0,3.0",
            "pref=1.0,1.0,2.0,2.0,1.0,1.0,3.0,1.0,2.0,1.0",
            "pref=10.0,5.0,10.0,10.0,5.0,5.0,20.0,5.0,15.0,15.0",
            "pref=2.0,1.0,1.0,3.0,2.0,2.0,3.0,1.0,2.0,2.0",
            "pref=5.0,10.0,0.0,10.0,10.0,10.0,20.0,5.0,15.0,5.0",
            "pref=5.0,10.0,0.0,10.0,10.0,10.0,20.0,5.0,15.0,10.0",
        ]:
            study_name = f"{d_name}_n-trials={n_trials}_sscaled-sum_{a}"
            compare_result_path = ex_path.joinpath(
                f"results/c_b_e/{d_name}/{study_name}/compare.json"
            )
            with open(compare_result_path, mode="r") as f:
                json_data = json.load(f)
            pivots = json_data[1][2]
            iterations = json_data[1][3]
            eps = json_data[1][4]
            print(pivots, iterations, eps, d_name)

            for picture_seed in seeds:
                eg_drawing = Drawing.initial_placement(eg_graph)
                pos = draw(
                    pivots=pivots,
                    iterations=iterations,
                    eps=eps,
                    eg_graph=eg_graph,
                    eg_indices=eg_indices,
                    eg_drawing=eg_drawing,
                    edge_weight=EDGE_WEIGHT,
                    seed=picture_seed,
                )

                fig, ax = plt.subplots(dpi=300, facecolor="white")
                ax.set_aspect("equal")

                fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

                nx.draw(
                    nx_graph,
                    pos=pos,
                    node_size=0.5,
                    width=0.5,
                    # node_color="#AB47BC",
                    edge_color="#CFD8DC",
                    ax=ax,
                )

                best_picture_path = ex_path.joinpath(
                    f"results/picture/best/{d_name}/{study_name}/seed={picture_seed}.png"
                )
                best_picture_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(best_picture_path)
                plt.close()

        # pareto
        n_trials = 200
        a = "max_pivots=0.25n"
        study_name = f"{d_name}_n-trials={n_trials}_multi-objective_{a}"
        compare_result_path = ex_path.joinpath(
            f"results/c_p_p/{d_name}/{study_name}/compare.json"
        )
        with open(compare_result_path, mode="r") as f:
            json_data = json.load(f)
        pivots = json_data[2][1]
        iterations = json_data[2][2]
        eps = json_data[2][3]
        print(pivots, iterations, eps, d_name)
        for picture_seed in seeds:
            eg_drawing = Drawing.initial_placement(eg_graph)
            pos = draw(
                pivots=pivots,
                iterations=iterations,
                eps=eps,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                eg_drawing=eg_drawing,
                edge_weight=EDGE_WEIGHT,
                seed=picture_seed,
            )

            fig, ax = plt.subplots(dpi=300, facecolor="white")
            ax.set_aspect("equal")

            fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

            nx.draw(
                nx_graph,
                pos=pos,
                node_size=0.5,
                width=0.5,
                # node_color="#AB47BC",
                edge_color="#CFD8DC",
                ax=ax,
            )

            most_win_pareto_picture_path = ex_path.joinpath(
                f"results/picture/best_pareto/{d_name}/{study_name}/seed={picture_seed}.png"
            )
            plt.savefig(most_win_pareto_picture_path)
            plt.close()


if __name__ == "__main__":
    main()
