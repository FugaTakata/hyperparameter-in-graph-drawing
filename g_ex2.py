# poetry run python g_ex2.py -l SS -t ideal_edge_length node_resolution run_time stress
# poetry run python g_ex2.py -l FR -t angular_resolution crossing_angle ideal_edge_length node_resolution run_time shape_based_metrics stress

# Standard Library
import argparse
import json
import math
import os
import random
import shutil
import uuid

# Third Party Library
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import optuna
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# First Party Library
from drawing.fruchterman_reingold import fruchterman_reingold
from drawing.sgd import sgd
from utils.graph import generate_egraph_graph, graph_preprocessing

mpl.use("Agg")

SS = "SS"
FR = "FR"
FM3 = "FM3"
KK = "KK"

PTO = "multi_optimized"
PTR = "randomized"
PTE = "experienced"


EDGE_WEIGHT = 30
RAND_MAX = 2**32

layout_name_abbreviations = [
    SS,
    FR,
    FM3,
    KK,
]


ALL_QUALITY_METRICS_NAMES = [
    "angular_resolution",
    "aspect_ratio",
    "crossing_angle",
    "crossing_number",
    "gabriel_graph_property",
    "ideal_edge_length",
    "node_resolution",
    "run_time",
    "shape_based_metrics",
    "stress",
]

ls = [SS, FR]
ds = ["les_miserables", "1138_bus", "USpowerGrid"]

parser = argparse.ArgumentParser()

parser.add_argument(
    "-l",
    choices=layout_name_abbreviations,
    required=True,
    help="layout name",
)
parser.add_argument(
    "-t",
    choices=ALL_QUALITY_METRICS_NAMES,
    nargs="*",
    required=True,
    help="target quality metrics names",
)

N = 4
N_Q = 5

args = parser.parse_args()
targets = args.t


question_id = str(uuid.uuid4())

export_directory = f"data/question2/{args.l}/{question_id}"
os.makedirs(export_directory, exist_ok=True)

data_export_path = f"{export_directory}/data.pkl"


study_name = ",".join(targets)

zero = True

for d in ds:
    dataset_path = f"lib/egraph-rs/js/dataset/{d}.json"
    with open(dataset_path) as f:
        graph_data = json.load(f)
    nx_graph = graph_preprocessing(nx.node_link_graph(graph_data), EDGE_WEIGHT)
    storage_path = f"sqlite:///db/opt/{args.l}/{d}/{study_name}.db"
    study = optuna.load_study(storage=storage_path, study_name=study_name)
    for qi in range(1, N_Q + 1):
        # PTO
        multi_optimized = []

        best_trials = study.best_trials

        if args.l == SS:
            graph, indices = generate_egraph_graph(nx_graph)
            for i in range(N):
                drawing_id = str(uuid.uuid4())
                seed = random.randrange(RAND_MAX)

                target_trial = random.choice(best_trials)
                params = target_trial.user_attrs["params"]

                pos = sgd(
                    graph=graph, indices=indices, params=params, seed=seed
                )
                drawing_data = {
                    "id": drawing_id,
                    "question_id": qi,
                    "seed": seed,
                    "params": params,
                    "layout": args.l,
                    "dataset": d,
                    "study_name": study_name,
                    "type": PTO,
                    "pos": pos,
                }
                multi_optimized.append(drawing_data)
        elif args.l == FR:
            for i in range(N):
                drawing_id = str(uuid.uuid4())
                seed = random.randrange(RAND_MAX)

                target_trial = random.choice(best_trials)
                params = target_trial.user_attrs["params"]
                params = {**params, "seed": seed}
                pos = fruchterman_reingold(nx_graph, params)
                drawing_data = {
                    "id": drawing_id,
                    "question_id": qi,
                    "seed": seed,
                    "params": params,
                    "layout": args.l,
                    "dataset": d,
                    "study_name": study_name,
                    "type": PTO,
                    "pos": pos,
                }
                multi_optimized.append(drawing_data)

        # PTR
        randomized = []

        if args.l == SS:
            for i in range(N):
                drawing_id = str(uuid.uuid4())
                seed = random.randrange(RAND_MAX)

                number_of_pivots_rate = random.uniform(0.01, 1)
                number_of_pivots = math.ceil(
                    number_of_pivots_rate * math.sqrt(len(nx_graph.nodes))
                )
                params = {
                    "edge_length": EDGE_WEIGHT,
                    "number_of_pivots_rate": number_of_pivots_rate,
                    "number_of_pivots": number_of_pivots,
                    "number_of_iterations": random.randrange(1, 200 + 1),
                    "eps": random.uniform(0.01, 1),
                }

                pos = sgd(
                    graph=graph, indices=indices, params=params, seed=seed
                )
                drawing_data = {
                    "id": drawing_id,
                    "question_id": qi,
                    "seed": seed,
                    "params": params,
                    "layout": args.l,
                    "dataset": d,
                    "study_name": None,
                    "type": PTR,
                    "pos": pos,
                }
                randomized.append(drawing_data)
        if args.l == FR:
            for i in range(N):
                drawing_id = str(uuid.uuid4())
                seed = random.randrange(RAND_MAX)

                k_rate = random.uniform(0.01, 1)
                # k 1/n ~ 0.1
                n = len(nx_graph.nodes)
                start_e = 1 / n
                end_e = 0.1
                if end_e < start_e:
                    print("error")
                    raise ValueError()
                dist = end_e - start_e
                k = k_rate * dist + start_e
                params = {
                    "k_rate": k_rate,
                    "k": k,
                    "pos": None,
                    "fixed": None,
                    "iterations": random.randint(10, 200),
                    "threshold": random.uniform(0.00001, 0.001),
                    "weight": "weight",
                    "scale": 1,
                    "center": None,
                    "dim": 2,
                    "seed": seed,
                }

                pos = fruchterman_reingold(nx_graph, params)
                drawing_data = {
                    "id": drawing_id,
                    "question_id": qi,
                    "seed": seed,
                    "params": params,
                    "layout": args.l,
                    "dataset": d,
                    "study_name": None,
                    "type": PTR,
                    "pos": pos,
                }
                randomized.append(drawing_data)

        # PTE
        experienced = []

        if args.l == SS:
            for i in range(N):
                drawing_id = str(uuid.uuid4())
                seed = random.randrange(RAND_MAX)

                params = {
                    "edge_length": EDGE_WEIGHT,
                    "number_of_pivots_rate": None,
                    "number_of_pivots": 50,
                    "number_of_iterations": 100,
                    "eps": 0.1,
                }

                pos = sgd(
                    graph=graph, indices=indices, params=params, seed=seed
                )
                drawing_data = {
                    "id": drawing_id,
                    "question_id": qi,
                    "seed": seed,
                    "params": params,
                    "layout": args.l,
                    "dataset": d,
                    "study_name": None,
                    "type": PTE,
                    "pos": pos,
                }
                experienced.append(drawing_data)
        if args.l == FR:
            for i in range(N):
                drawing_id = str(uuid.uuid4())
                seed = random.randrange(RAND_MAX)

                params = {
                    "k_rate": None,
                    "k": 1 / math.sqrt(len(nx_graph.nodes)),
                    "pos": None,
                    "fixed": None,
                    "iterations": 50,
                    "threshold": 0.0001,
                    "weight": "weight",
                    "scale": 1,
                    "center": None,
                    "dim": 2,
                    "seed": seed,
                }

                pos = fruchterman_reingold(nx_graph, params)
                drawing_data = {
                    "id": drawing_id,
                    "question_id": qi,
                    "seed": seed,
                    "params": params,
                    "layout": args.l,
                    "dataset": d,
                    "study_name": None,
                    "type": PTE,
                    "pos": pos,
                }
                experienced.append(drawing_data)

        data = multi_optimized + randomized + experienced
        random.shuffle(data)

        for i, v in enumerate(data):
            placement_number = i + 1
            v["placement_number"] = placement_number

        df = pd.DataFrame(data)
        if zero:
            df.to_pickle(data_export_path)
            zero = False
        elif not zero:
            pd.concat([pd.read_pickle(data_export_path), df]).to_pickle(
                data_export_path
            )

        images_export_directory = f"{export_directory}/images/{d}/{qi}"
        os.makedirs(images_export_directory, exist_ok=True)

        # 一番でかいやつに合わせる
        smax = -float("inf")
        for row in df.itertuples():
            xs = [row.pos[k][0] for k in row.pos]
            ys = [row.pos[k][1] for k in row.pos]
            xmax = max(xs)
            xmin = min(xs)
            ymax = max(ys)
            ymin = min(ys)
            if smax < xmax - xmin:
                smax = xmax - xmin
            if smax < ymax - ymin:
                smax = ymax - ymin
        smax /= 2
        # ちょい余白
        smax += smax // 10

        for row in df.itertuples():
            xs = [row.pos[k][0] for k in row.pos]
            ys = [row.pos[k][1] for k in row.pos]
            xmax = max(xs)
            xmin = min(xs)
            ymax = max(ys)
            ymin = min(ys)
            xc = (xmax + xmin) / 2
            yc = (ymax + ymin) / 2
            fig, ax = plt.subplots(dpi=300, facecolor="white")
            ax.set_aspect("equal")
            ax.set_xlim(xc - smax, xc + smax)
            ax.set_ylim(yc - smax, yc + smax)
            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
            nx.draw(
                nx_graph,
                pos=row.pos,
                node_size=4,
                edge_color="lightblue",
                ax=ax,
            )
            # limits = plt.axis("on")  # turns on axis
            # ax.tick_params(
            #     left=True, bottom=True, labelleft=True, labelbottom=True
            # )

            fig.savefig(
                f"{images_export_directory}/{row.id}.png",
                format="png",
            )
            plt.close()

        h_count = 4

        os.makedirs(f"{export_directory}/{d}/", exist_ok=True)
        question_image_export_path = f"{export_directory}/{d}/{qi}.png"

        placement_sorted_df = df.sort_values("placement_number")

        images = []
        tmp = []
        for row in placement_sorted_df.itertuples():
            image_path = f"{images_export_directory}/{row.id}.png"
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            width = img.width // 20
            height = img.height // 20
            font = ImageFont.truetype(font="Arial.ttf", size=width)
            draw.text(
                (width, height), f"{row.placement_number}", "black", font=font
            )

            tmp.append(
                {"placement_number": row.placement_number, "image": img}
            )

            if row.placement_number % h_count == 0:
                images.append(tmp)
                tmp = []

        def get_concat_h(im1, im2):
            dst = Image.new(
                "RGB", (im1.width + im2.width, im1.height), "black"
            )
            dst.paste(im1, (0, 0))
            dst.paste(im2, (im1.width, 0))
            return dst

        def get_concat_v(im1, im2):
            dst = Image.new("RGB", (im1.width, im1.height + im2.height))
            dst.paste(im1, (0, 0))
            dst.paste(im2, (0, im1.height))
            return dst

        dst = None
        for v in images:
            h_dst = None
            for h in v:
                if h_dst is None:
                    h_dst = h["image"]
                    continue
                h_dst = get_concat_h(h_dst, h["image"])
            if dst is None:
                dst = h_dst
                continue
            dst = get_concat_v(dst, h_dst)

        dst.save(question_image_export_path)
        dst = None
        images = None
        tmp = None
        plt.close()
        # shutil.rmtree(images_export_directory)

        # info = [(a["placement_number"], a["type"], a["id"]) for a in data]
        # with open(f"{export_directory}/{d}/{qi}/info.json", mode="w") as f:
        #     json.dump(info, f)
