# Standard Library
import math

# Third Party Library
import networkx as nx
import optuna

# First Party Library
from drawing.fruchterman_reingold import fruchterman_reingold
from drawing.sgd import sgd
from quality_metrics.run_time import RunTime
from utils.calc_quality_metrics import calc_qs
from utils.graph import generate_egraph_graph


def ss_objective(
    nx_graph,
    all_pairs_shortest_path_length,
    target_quality_metrics_names,
    all_quality_metrics_names,
    edge_weight,
):
    graph, indices = generate_egraph_graph(nx_graph)

    def objective(trial: optuna.Trial):
        number_of_pivots_rate = trial.suggest_float(
            "number_of_pivots_rate", 0.01, 1
        )
        number_of_pivots = math.ceil(
            number_of_pivots_rate * len(nx_graph.nodes)
        )
        params = {
            "edge_length": edge_weight,
            "number_of_pivots_rate": number_of_pivots_rate,
            "number_of_pivots": number_of_pivots,
            "number_of_iterations": trial.suggest_int(
                "number_of_iterations", 1, 200
            ),
            "eps": trial.suggest_float("eps", 0.01, 1),
        }
        trial.set_user_attr("params", params)
        del params["number_of_pivots_rate"]

        run_time = RunTime()

        run_time.start()
        pos = sgd(graph, indices, params, 0)
        run_time.end()

        trial.set_user_attr("pos", pos)

        quality_metrics = calc_qs(
            nx_graph=nx_graph,
            pos=pos,
            all_pairs_shortest_path_length=all_pairs_shortest_path_length,
            target_quality_metrics_names=all_quality_metrics_names,
            edge_weight=edge_weight,
        )
        quality_metrics = {**quality_metrics, "run_time": run_time.quality()}
        trial.set_user_attr("quality_metrics", quality_metrics)

        result = tuple(
            [quality_metrics[name] for name in target_quality_metrics_names]
        )
        return result

    return objective


def fr_objective(
    nx_graph,
    all_pairs_shortest_path_length,
    target_quality_metrics_names,
    all_quality_metrics_names,
    edge_weight,
):
    initial_pos = nx.random_layout(nx_graph, seed=0)
    for k in initial_pos:
        x, y = initial_pos[k]
        print(x, y, float(x), float(y))
        initial_pos[k] = [float(x), float(y)]

    def objective(trial: optuna.Trial):
        k_rate = trial.suggest_float("k_rate", 0.01, 1)
        k = math.ceil(k_rate * len(nx_graph.nodes))
        params = {
            "k_rate": k_rate,
            "k": k,
            "pos": initial_pos,
            "fixed": None,
            "iterations": trial.suggest_int("iterations", 1, 200),
            "threshold": trial.suggest_float("threshold", 0.00001, 0.001),
            "weight": "weight",
            "scale": 1,
            "center": None,
            "dim": 2,
            "seed": 0,
        }
        trial.set_user_attr("params", params)
        del params["k_rate"]

        run_time = RunTime()

        run_time.start()
        pos = fruchterman_reingold(nx_graph, params=params)
        run_time.end()

        trial.set_user_attr("pos", pos)

        quality_metrics = calc_qs(
            nx_graph=nx_graph,
            pos=pos,
            all_pairs_shortest_path_length=all_pairs_shortest_path_length,
            target_quality_metrics_names=all_quality_metrics_names,
            edge_weight=edge_weight,
        )
        quality_metrics = {**quality_metrics, "run_time": run_time.quality()}
        trial.set_user_attr("quality_metrics", quality_metrics)

        result = tuple(
            [quality_metrics[name] for name in target_quality_metrics_names]
        )
        return result

    return objective
