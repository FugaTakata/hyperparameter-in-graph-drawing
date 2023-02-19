# Standard Library
import argparse
import json
import os
import statistics

# Third Party Library
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

# First Party Library
from quality_metrics import (
    angular_resolution,
    aspect_ratio,
    crossing_angle,
    crossing_number,
    gabriel_graph_property,
    ideal_edge_length,
    node_resolution,
    shape_based_metrics,
    stress,
)
from utils.dataset import dataset_names

mpl.use("Agg")


SS = "SS"
FR = "FR"

QUALITY_METRICS = {
    "angular_resolution": angular_resolution,
    "aspect_ratio": aspect_ratio,
    "crossing_angle": crossing_angle,
    "crossing_number": crossing_number,
    "gabriel_graph_property": gabriel_graph_property,
    "ideal_edge_length": ideal_edge_length,
    "node_resolution": node_resolution,
    "shape_based_metrics": shape_based_metrics,
    "stress": stress,
}

NAME_ABBREVIATIONS = {
    "angular_resolution": "ANR",
    "aspect_ratio": "AR",
    "crossing_angle": "CA",
    "crossing_number": "CN",
    "gabriel_graph_property": "GB",
    "ideal_edge_length": "IE",
    "node_resolution": "NR",
    "run_time": "RT",
    "shape_based_metrics": "SB",
    "stress": "ST",
}

# box plot width [0,1]
BOX_PLOT_WIDTH = 0.4

ALL_QUALITY_METRICS_NAMES = sorted([name for name in QUALITY_METRICS])


layout_name_abbreviations = [
    SS,
    FR,
]


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", choices=dataset_names, required=True, help="dataset name"
)
parser.add_argument(
    "-a", help="adjust randomized long beard", action="store_true"
)
parser.add_argument(
    "-o", help="adjust randomized long beard", action="store_true"
)
parser.add_argument(
    "-t",
    choices=ALL_QUALITY_METRICS_NAMES,
    nargs="*",
    required=True,
    help="target quality metrics names",
)
parser.add_argument(
    "-l",
    choices=layout_name_abbreviations,
    required=True,
    help="layout name",
)

args = parser.parse_args()


L = "SS"
D = "USpowerGrid"
ADJUST_RANDOMIZED_LONG_BEARD = args.a
REMOVE_OUTLIER = args.o
TARGET_QUALITY_METRICS = [
    "angular_resolution",
    "crossing_number",
    "ideal_edge_length",
    "node_resolution",
    "shape_based_metrics",
    "stress",
]

if ADJUST_RANDOMIZED_LONG_BEARD and REMOVE_OUTLIER:
    raise ValueError("do not use -a with -o")

export_path = f"data/compare_us/{L}/{D}"
if ADJUST_RANDOMIZED_LONG_BEARD:
    export_path = f"data/compare_us_adjusted/{L}/{D}"
if REMOVE_OUTLIER:
    export_path = f"data/compare_us_no_outlier/{L}/{D}"


os.makedirs(export_path, exist_ok=True)


# rpfs_df = pd.read_pickle(f"{export_path}/rpfs_data.pkl")
# exfs_df = pd.read_pickle(f"{export_path}/exfs_data.pkl")
rpfs_df = pd.read_pickle(f"data/rpfs_ex/{L}/{D}/ignore_100rp_1fs.pkl")
exfs_df = pd.read_pickle(f"data/experienced/{L}/{D}/ignore_50fs.pkl")
paretofs_df = pd.read_pickle(f"data/paretofs/{L}/{D}/{','.join(args.t)}.pkl")
pattern_les_df = pd.read_pickle(
    f'data/paretofs/SS/les_miserables-USpowerGrid/{",".join(args.t)}.pkl'
)
pattern_bus_df = pd.read_pickle(
    f'data/paretofs/SS/1138_bus-USpowerGrid/{",".join(args.t)}.pkl'
)

# n_pareto = len(mopfs_df)
# rpfs_df = rpfs_df.sample(n=n_pareto)
# exfs_df = exfs_df.sample(n=n_pareto)

# rpfs_df.to_pickle(f"{export_path}/rpfs_data.pkl")
# exfs_df.to_pickle(f"{export_path}/exfs_data.pkl")
q_pattern_les_fs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_pattern_les_fs[name] = []
for row in pattern_les_df.itertuples():
    for name in row.quality_metrics:
        q_pattern_les_fs[name].append(row.quality_metrics[name])

q_pattern_bus_fs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_pattern_bus_fs[name] = []
for row in pattern_bus_df.itertuples():
    for name in row.quality_metrics:
        q_pattern_bus_fs[name].append(row.quality_metrics[name])

q_paretofs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_paretofs[name] = []
for row in paretofs_df.itertuples():
    for name in row.quality_metrics:
        q_paretofs[name].append(row.quality_metrics[name])

q_exfs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_exfs[name] = []
    for row in exfs_df.itertuples():
        q_exfs[name].append(row.quality_metrics[name])

# q_rpfs = {}
# for name in ALL_QUALITY_METRICS_NAMES:
#     q_rpfs[name] = []
# q_tmp = {}
# s = 0
# for q in rpfs_df["quality_metrics"]:
#     if s == 0:
#         for name in ALL_QUALITY_METRICS_NAMES:
#             q_tmp[name] = []
#     for name in ALL_QUALITY_METRICS_NAMES:
#         q_tmp[name].append(q[name])
#     if s == 49:
#         for name in ALL_QUALITY_METRICS_NAMES:
#             q_rpfs[name].append(q_tmp[name])
#     s += 1
#     if s == 50:
#         s = 0

q_rpfs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_rpfs[name] = []
for q in rpfs_df["quality_metrics"]:
    for name in ALL_QUALITY_METRICS_NAMES:
        q_rpfs[name].append(q[name])


for name in TARGET_QUALITY_METRICS:
    rpfs_bin = q_rpfs[name]
    # if ADJUST_RANDOMIZED_LONG_BEARD and (
    #     name == "crossing_number"
    #     or name == "ideal_edge_length"
    #     or name == "stress"
    # ):
    #     max_threshold = max(
    #         np.percentile(rpfs_bin, 75),
    #         max(q_pattern_les_fs[name]),
    #         max(q_pattern_bus_fs[name]),
    #         max(q_paretofs[name]),
    #         max(q_exfs[name]),
    #     )
    #     rpfs_bin = [min(v, max_threshold * 1.5) for v in q_rpfs[name]]
    bins = [
        q_paretofs[name],
        q_pattern_bus_fs[name],
        q_pattern_les_fs[name],
        q_exfs[name],
        rpfs_bin,
    ]
    for b in bins:
        print(len(b))
    direction = QUALITY_METRICS[name].direction
    # plt.title(f'{name} {"+" if direction == "maximize" else "-"}')
    plt.figure(figsize=(3, 2))
    plt.subplots_adjust(left=0.3, top=0.8, bottom=0.2)
    plt.tick_params(axis="x", labelsize=18)
    plt.tick_params(axis="y", labelsize=14)
    # plt.title(f"{NAME_ABBREVIATIONS[name]}", fontsize=18)
    plt.title(
        f'{NAME_ABBREVIATIONS[name]} {"+" if direction == "maximize" else "-"}',
        fontsize=18,
    )
    if REMOVE_OUTLIER:
        plt.boxplot(
            bins,
            labels=[f"({c})" for c in ["a", "b", "c", "d", "e"]],
            # whis=float("inf"),
            widths=BOX_PLOT_WIDTH,
            sym="",
        )
    else:
        plt.boxplot(
            bins,
            labels=[f"({c})" for c in ["a", "b", "c", "d", "e"]],
            whis=float("inf"),
            widths=BOX_PLOT_WIDTH,
        )
    # plt.xticks(rotation=-60, ha="center")
    plt.savefig(
        f"{export_path}/{name}.png",
        format="png",
        dpi=300,
        facecolor="white",
    )
    plt.close()


dst_export_path = f"{export_path}/all.png"
images = []
tmp = []
for quality in TARGET_QUALITY_METRICS:
    image_path = f"{export_path}/{quality}.png"
    img = Image.open(image_path)

    tmp.append({"image": img})

    if len(tmp) == 6:
        images.append(tmp)
        tmp = []


def get_concat_h(im1, im2):
    dst = Image.new("RGB", (im1.width + im2.width, im1.height), "black")
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new("RGB", (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def get_concat_h_blank(im1, im2, color=(0, 0, 0)):
    dst = Image.new(
        "RGB", (im1.width + im2.width, max(im1.height, im2.height)), color
    )
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v_blank(im1, im2, color=(0, 0, 0)):
    dst = Image.new(
        "RGB", (max(im1.width, im2.width), im1.height + im2.height), color
    )
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
        h_dst = get_concat_h_blank(h_dst, h["image"])
    if dst is None:
        dst = h_dst
        continue
    # dst = get_concat_v_blank(dst, h_dst)
    dst = h_dst

dst.save(dst_export_path)
# os.removedirs(images_export_directory)


#  poetry run python -u compare_us.py -d USpowerGrid -l SS -t angular_resolution crossing_number ideal_edge_length node_resolution shape_based_metrics stress && \
# poetry run python -u compare_us.py -a -d USpowerGrid -l SS -t angular_resolution crossing_number ideal_edge_length node_resolution shape_based_metrics stress && \
# poetry run python -u compare_us.py -o -d USpowerGrid -l SS -t angular_resolution crossing_number ideal_edge_length node_resolution shape_based_metrics stress && \
# say finished
