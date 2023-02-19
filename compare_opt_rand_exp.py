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
    "-l",
    choices=layout_name_abbreviations,
    required=True,
    help="layout name",
)

args = parser.parse_args()

ADJUST_RANDOMIZED_LONG_BEARD = args.a


export_path = f"data/c_opt_rand_exp_m/{args.l}/{args.d}"
if ADJUST_RANDOMIZED_LONG_BEARD:
    export_path = f"data/c_opt_rand_exp_adjusted_m/{args.l}/{args.d}"
os.makedirs(export_path, exist_ok=True)

l = args.l
d = args.d

rpfs_df = pd.read_pickle(f"data/rpfs/{l}/{d}/ignore_20rp_50fs.pkl")
opfs_df = pd.read_pickle(f"data/opfs_m/{l}/{d}/ignore_all.pkl")
exfs_df = pd.read_pickle(f"data/experienced/{l}/{d}/ignore_50fs.pkl")

q_opfs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_opfs[name] = []
for name in ALL_QUALITY_METRICS_NAMES:
    tdf = opfs_df[opfs_df["target"] == name]
    for q in tdf["quality_metrics"]:
        q_opfs[name].append(q[name])


q_exfs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_exfs[name] = []
    for row in exfs_df.itertuples():
        q_exfs[name].append(row.quality_metrics[name])

q_rpfs = {}
for name in ALL_QUALITY_METRICS_NAMES:
    q_rpfs[name] = []
q_tmp = {}
s = 0
for q in rpfs_df["quality_metrics"]:
    if s == 0:
        for name in ALL_QUALITY_METRICS_NAMES:
            q_tmp[name] = []
    for name in ALL_QUALITY_METRICS_NAMES:
        q_tmp[name].append(q[name])
    if s == 49:
        for name in ALL_QUALITY_METRICS_NAMES:
            q_rpfs[name].append(q_tmp[name])
    s += 1
    if s == 50:
        s = 0


optimized = []
counts = {}
opfs_mean = {}
rpfs_means = {}
border = 15
for name in ALL_QUALITY_METRICS_NAMES:
    direction = QUALITY_METRICS[name].direction
    opfs_mean[name] = statistics.median(q_opfs[name])
    count = 0

    if name not in rpfs_means:
        rpfs_means[name] = []
    for vs in q_rpfs[name]:
        rpfs_means[name].append(statistics.median(vs))

    for mean in rpfs_means[name]:
        if direction == "maximize":
            if mean <= opfs_mean[name]:
                count += 1
        elif direction == "minimize":
            if opfs_mean[name] <= mean:
                count += 1
    if border <= count:
        optimized.append(name)
    counts[name] = count
dict_data = {"optimized": optimized, "counts": counts}
with open(f"{export_path}/result.json", mode="w") as f:
    json.dump(dict_data, f)


for name in ALL_QUALITY_METRICS_NAMES:
    rpfs_bin = sum(q_rpfs[name], [])
    if ADJUST_RANDOMIZED_LONG_BEARD and (
        name == "crossing_number"
        or name == "ideal_edge_length"
        or name == "stress"
    ):
        max_threshold = max(
            np.percentile(rpfs_bin, 75), max(q_opfs[name]), max(q_exfs[name])
        )
        rpfs_bin = [min(v, max_threshold * 1.5) for v in rpfs_bin]
    bins = [q_opfs[name], q_exfs[name], rpfs_bin]
    direction = QUALITY_METRICS[name].direction
    plt.title(f'{name} {"+" if direction == "maximize" else "-"}')
    labels = [f"o_{NAME_ABBREVIATIONS[name]}"] + ["exp"] + ["rand"]
    plt.boxplot(
        bins,
        labels=labels,
        whis=float("inf"),
        # sym="",
    )
    plt.xticks(rotation=-60, ha="center")
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
for quality in ALL_QUALITY_METRICS_NAMES:
    image_path = f"{export_path}/{quality}.png"
    img = Image.open(image_path)

    tmp.append({"image": img})

    if len(tmp) == 3:
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
    dst = get_concat_v_blank(dst, h_dst)

dst.save(dst_export_path)
# os.removedirs(images_export_directory)
