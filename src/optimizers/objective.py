# Standard Library
import statistics

# Third Party Library
import optuna

# First Party Library
from config import params_domains, quality_metrics
from generators import drawing_and_qualities, graph


def ss(
    nx_graph,
    shortest_path_length,
    target_qm_names,
    edge_weight,
    n_means,
    generate_seed,
):
    eg_graph, eg_indices = graph.egraph_graph(nx_graph=nx_graph)

    def objective(trial: optuna.Trial):
        params = {
            "edge_length": edge_weight,
            "number_of_pivots": trial.suggest_int(
                "number_of_pivots",
                params_domains.ss["number_of_pivots"]["l"],
                params_domains.ss["number_of_pivots"]["u"],
            ),
            "number_of_iterations": trial.suggest_int(
                "number_of_iterations",
                params_domains.ss["number_of_iterations"]["l"],
                params_domains.ss["number_of_iterations"]["u"],
            ),
            "eps": trial.suggest_float(
                "eps",
                params_domains.ss["eps"]["l"],
                params_domains.ss["eps"]["u"],
            ),
        }

        trial.set_user_attr("params", params)

        qualities_means = {}
        for qm_name in quality_metrics.ALL_QM_NAMES:
            qualities_means[qm_name] = []

        for _ in range(n_means):
            seed = generate_seed()
            pos, qualities = drawing_and_qualities.ss(
                nx_graph=nx_graph,
                eg_graph=eg_graph,
                eg_indices=eg_indices,
                params=params,
                shortest_path_length=shortest_path_length,
                seed=seed,
                edge_weight=edge_weight,
            )

            for qm_name in quality_metrics.ALL_QM_NAMES:
                qualities_means[qm_name].append(qualities[qm_name])

        for qm_name in quality_metrics.ALL_QM_NAMES:
            qualities_means[qm_name] = statistics.mean(
                qualities_means[qm_name]
            )

        trial.set_user_attr("qualities", qualities_means)

        result = tuple(
            [qualities_means[qm_name] for qm_name in target_qm_names]
        )

        return result

    return objective
