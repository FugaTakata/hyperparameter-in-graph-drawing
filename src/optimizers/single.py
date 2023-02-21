# Third Party Library
import optuna

# First Party Library
from config import quality_metrics
from optimizers import objective
from utils import graph


def ss(
    dataset_name,
    database_uri,
    study_name,
    n_trials,
    n_means,
    generate_seed,
    target_qm_names,
    edge_weight,
):
    nx_graph = graph.load_nx_graph(
        dataset_name=dataset_name, edge_weight=edge_weight
    )
    shortest_path_length = graph.get_shortest_path_length(nx_graph=nx_graph)

    study = optuna.create_study(
        directions=[
            quality_metrics.QUALITY_METRICS_MAP[qm_name].direction
            for qm_name in target_qm_names
        ],
        storage=database_uri,
        study_name=study_name,
        load_if_exists=True,
    )

    study.optimize(
        func=objective.ss(
            nx_graph=nx_graph,
            shortest_path_length=shortest_path_length,
            target_qm_names=target_qm_names,
            edge_weight=edge_weight,
            n_means=n_means,
            generate_seed=generate_seed,
        ),
        n_trials=n_trials,
        show_progress_bar=True,
    )
