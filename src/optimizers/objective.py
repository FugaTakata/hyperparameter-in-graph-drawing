# Third Party Library
import optuna
from egraph import Coordinates, warshall_floyd

# First Party Library
from config import parameters, quality_metrics
from generators import graph as graph_generator
from layouts import sgd
from utils.quality_metrics import measure_qualities


def ss(
    nx_graph,
    target_qm_names,
    edge_weight,
    n_seed,
    result_handler,
    generate_seed,
):
    eg_graph, eg_indices = graph_generator.egraph_graph(nx_graph=nx_graph)
    eg_distance_matrix = warshall_floyd(eg_graph, lambda _: edge_weight)

    def objective(trial: optuna.Trial):
        params = {
            "edge_length": edge_weight,
            "number_of_pivots": trial.suggest_int(
                "number_of_pivots",
                parameters.domain_ss["number_of_pivots"]["l"],
                parameters.domain_ss["number_of_pivots"]["u"],
            ),
            "number_of_iterations": trial.suggest_int(
                "number_of_iterations",
                parameters.domain_ss["number_of_iterations"]["l"],
                parameters.domain_ss["number_of_iterations"]["u"],
            ),
            "eps": trial.suggest_float(
                "eps",
                parameters.domain_ss["eps"]["l"],
                parameters.domain_ss["eps"]["u"],
            ),
        }

        trial.set_user_attr("params", params)

        qualities_list = {}
        for qm_name in quality_metrics.qm_names:
            qualities_list[qm_name] = []

        for _ in range(n_seed):
            seed = generate_seed()
            eg_drawing = Coordinates.initial_placement(eg_graph)

            _ = sgd.sgd(
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                eg_drawing=eg_drawing,
                params=params,
                seed=seed,
            )

            qualities = measure_qualities(
                target_qm_names=quality_metrics.qm_names,
                eg_graph=eg_graph,
                eg_drawing=eg_drawing,
                eg_distance_matrix=eg_distance_matrix,
            )

            for qm_name in quality_metrics.qm_names:
                qualities_list[qm_name].append(qualities[qm_name])

        qualities_result = result_handler(qualities_list)

        trial.set_user_attr("qualities", qualities_result)

        result = tuple(
            [qualities_result[qm_name] for qm_name in target_qm_names]
        )

        return result

    return objective
