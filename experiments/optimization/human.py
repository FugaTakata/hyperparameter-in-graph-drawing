# Standard Library
import argparse
import os
import textwrap
import time
from typing import NoReturn

# Third Party Library
import matplotlib.pyplot as plt
import networkx as nx
import optuna
from egraph import Drawing, all_sources_bfs
from ex_utils.config.dataset import dataset_names
from ex_utils.config.paths import get_dataset_path
from ex_utils.config.quality_metrics import qm_names
from ex_utils.share import draw, draw_and_measure, ex_path
from ex_utils.utils.graph import (
    egraph_graph,
    load_nx_graph,
    nx_graph_preprocessing,
)
from optuna.artifacts import FileSystemArtifactStore, upload_artifact
from optuna.trial import TrialState
from optuna_dashboard import (
    ChoiceWidget,
    register_objective_form_widgets,
    save_note,
)
from optuna_dashboard.artifact import get_artifact_path

EDGE_WEIGHT = 30
D = "USpowerGrid"


def suggest_and_generate_image(
    study: optuna.Study,
    artifact_store: FileSystemArtifactStore,
    eg_graph,
    eg_indices,
    nx_graph,
) -> None:
    # 1. Ask new parameters
    trial = study.ask()
    eg_drawing = Drawing.initial_placement(eg_graph)
    params = {
        "pivots": trial.suggest_int("pivots", 1, 100),
        "iterations": trial.suggest_int("iterations", 1, 200),
        "eps": trial.suggest_float("eps", 0.01, 1),
    }
    pos = draw(
        params=params,
        eg_graph=eg_graph,
        eg_indices=eg_indices,
        eg_drawing=eg_drawing,
        edge_weight=EDGE_WEIGHT,
        seed=0,
    )

    fig, ax = plt.subplots(dpi=300, facecolor="white")
    ax.set_aspect("equal")

    nx.draw(
        nx_graph,
        pos=pos,
        node_size=5,
        node_color="#AB47BC",
        edge_color="#CFD8DC",
        ax=ax,
        alpha=0.8,
    )

    # print(quality_metrics)

    # plt.show()

    # 2. Generate image
    image_path = f"tmp/sample-{trial.number}.png"
    plt.savefig(image_path, dpi=300)

    # 3. Upload Artifact
    artifact_id = upload_artifact(trial, image_path, artifact_store)
    artifact_path = get_artifact_path(trial, artifact_id)

    # 4. Save Note
    note = textwrap.dedent(
        f"""\
    ## Trial {trial.number}

    ![generated-image]({artifact_path})
    """
    )
    save_note(trial, note)


def start_optimization(artifact_store: FileSystemArtifactStore) -> NoReturn:
    # 1. Create Study
    study = optuna.create_study(
        study_name="Human-in-the-loop Optimization 7",
        storage="sqlite:///db.sqlite3",
        sampler=optuna.samplers.TPESampler(
            constant_liar=True, n_startup_trials=5
        ),
        load_if_exists=True,
    )

    # 2. Set an objective name
    study.set_metric_names(["Looks like sunset color?"])

    cs = [1, 2, 3, 4, 5, 6, 7]
    # 3. Register ChoiceWidget
    register_objective_form_widgets(
        study,
        widgets=[
            ChoiceWidget(
                choices=cs,
                values=[-c for c in cs],
                description="Please input your score!",
            ),
        ],
    )

    dataset_path = get_dataset_path(D)
    nx_graph = nx_graph_preprocessing(
        load_nx_graph(dataset_path=dataset_path), EDGE_WEIGHT
    )
    eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)

    # 4. Start Human-in-the-loop Optimization
    n_batch = 4
    while True:
        running_trials = study.get_trials(
            deepcopy=False, states=(TrialState.RUNNING,)
        )
        if len(running_trials) >= n_batch:
            time.sleep(1)  # Avoid busy-loop
            continue
        suggest_and_generate_image(
            study,
            artifact_store,
            eg_graph,
            eg_indices,
            nx_graph,
        )


def main() -> NoReturn:
    tmp_path = os.path.join(os.path.dirname(__file__), "tmp")

    # 1. Create Artifact Store
    artifact_path = os.path.join(os.path.dirname(__file__), "artifact")
    artifact_store = FileSystemArtifactStore(artifact_path)

    if not os.path.exists(artifact_path):
        os.mkdir(artifact_path)

    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    # 2. Run optimize loop
    start_optimization(artifact_store)


if __name__ == "__main__":
    main()
