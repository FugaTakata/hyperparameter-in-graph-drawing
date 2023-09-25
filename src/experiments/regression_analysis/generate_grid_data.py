DATASET_NAME = "USpowerGrid"

EDGE_WEIGHT = 30

NUM_OF_ITERATIONS = 100
NUM_OF_PIVOTS = 50
EPS = 0.1

N_SEED = 1

# Standard Library
from uuid import uuid4

# Third Party Library
import pandas as pd
from tqdm import tqdm


def generate_data_id():
    return str(uuid4())


# Standard Library
from random import randint


def generate_seed():
    return randint(0, 2**32)


def generate_data_object(data_id, pos, quality_metrics, params):
    return {"id": data_id, "pos": pos, **quality_metrics, **params}


# First Party Library
from config import paths

EXPERIMENT_DATA_DIR = (
    paths.get_project_root_path()
    .joinpath("data")
    .joinpath("experiments")
    .joinpath("regression_analysis")
)
EXPERIMENT_DATA_DIR.mkdir(exist_ok=True, parents=True)

NAME_ABBREVIATIONS = {
    "angular_resolution": "ANR",
    "aspect_ratio": "AR",
    "crossing_angle": "CA",
    "crossing_number": "CN",
    "gabriel_graph_property": "GB",
    "ideal_edge_lengths": "IE",
    "node_resolution": "NR",
    "run_time": "RT",
    "neighborhood_preservation": "NP",
    "stress": "ST",
}
# First Party Library
from utils.graph import load_nx_graph

dataset_path = paths.get_dataset_path(dataset_name=DATASET_NAME)
nx_graph = load_nx_graph(dataset_name=DATASET_NAME, edge_weight=EDGE_WEIGHT)
# Third Party Library
from egraph import warshall_floyd

# First Party Library
from generators.graph import egraph_graph

eg_graph, eg_indices = egraph_graph(nx_graph=nx_graph)
eg_distance_matrix = warshall_floyd(eg_graph, lambda _: EDGE_WEIGHT)
# Standard Library
from itertools import product

# First Party Library
from config.parameters import domain_ss

params_steps = {
    "number_of_pivots": 5,
    "number_of_iterations": 10,
    "eps": 0.05,
}

params_candidates = {}
params_names = ["number_of_pivots", "number_of_iterations", "eps"]
for params_name in params_names:
    lower = domain_ss[params_name]["l"]
    upper = domain_ss[params_name]["u"]

    params_candidates[params_name] = [
        v * params_steps[params_name] for v in list(range(1, 20 + 1))
    ]

params_list = [
    {
        "number_of_pivots": number_of_pivots,
        "number_of_iterations": number_of_iterations,
        "eps": eps,
    }
    for number_of_pivots, number_of_iterations, eps in list(
        product(
            *[params_candidates[params_name] for params_name in params_names]
        )
    )
]
# Third Party Library
from egraph import Coordinates, Rng, SparseSgd, crossing_edges

# First Party Library
from config.quality_metrics import ALL_QM_NAMES
from utils.quality_metrics import measure_qualities

data = []
for params in tqdm(params_list):
    mean_quality_metrics = {}
    for qm_name in ALL_QM_NAMES:
        mean_quality_metrics[qm_name] = []

    for _ in range(N_SEED):
        eg_drawing = Coordinates.initial_placement(eg_graph)
        seed = generate_seed()
        rng = Rng.seed_from(seed)
        sparse_sgd = SparseSgd(
            eg_graph, lambda _: EDGE_WEIGHT, params["number_of_pivots"], rng
        )
        scheduler = sparse_sgd.scheduler(
            params["number_of_iterations"], params["eps"]
        )

        def step(eta):
            sparse_sgd.shuffle(rng)
            sparse_sgd.apply(eg_drawing, eta)

        scheduler.run(step)

        eg_crossings = crossing_edges(eg_graph, eg_drawing)
        quality_metrics = measure_qualities(
            target_qm_names=ALL_QM_NAMES,
            eg_graph=eg_graph,
            eg_drawing=eg_drawing,
            eg_crossings=eg_crossings,
            eg_distance_matrix=eg_distance_matrix,
        )
        quality_metrics["aspect_ratio"] *= -1
        quality_metrics["neighborhood_preservation"] *= -1
        for qm_name in ALL_QM_NAMES:
            mean_quality_metrics[qm_name].append(quality_metrics[qm_name])

        pos = {
            u: (eg_drawing.x(i), eg_drawing.y(i))
            for u, i in eg_indices.items()
        }
        data_id = generate_data_id()
        data_object = {
            "data_id": data_id,
            "pos": pos,
            **quality_metrics,
            **params,
        }
        data.append(data_object)
data_export_path = EXPERIMENT_DATA_DIR.joinpath("grid").joinpath(
    f"{DATASET_NAME}-{generate_data_id()}.pkl"
)
data_export_path.parent.mkdir(parents=True, exist_ok=True)

data_df = pd.DataFrame(data)
data_df.to_pickle(data_export_path)
