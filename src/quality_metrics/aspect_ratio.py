# Third Party Library
import numpy as np
from scipy.spatial import ConvexHull

# First Party Library
from utils import gravity_center

direction = "maximize"


def quality(nx_graph, pos):
    N = 7
    gx, gy = gravity_center.gravity_center(pos)
    centered_pos = {}
    for node_id in nx_graph.nodes:
        x, y = pos[node_id]
        centered_pos[node_id] = [x - gx, y - gy]

    centered_pos_array = [centered_pos[id] for id in centered_pos]
    ch = ConvexHull(centered_pos_array)

    ch_array = []
    for i in ch.vertices:
        x, y = centered_pos_array[i]
        ch_array.append([x, y])

    q = 1
    for k in range(N):
        max_x = -float("inf")
        min_x = float("inf")
        max_y = -float("inf")
        min_y = float("inf")

        theta = (2 * np.pi * k) / N
        c = np.cos(theta)
        s = np.sin(theta)

        for ch_pos in ch_array:
            x, y = ch_pos

            rx = x * c - y * s
            ry = x * s + y * c

            if rx < min_x:
                min_x = rx
            if max_x < rx:
                max_x = rx
            if ry < min_y:
                min_y = ry
            if max_y < ry:
                max_y = ry

        w = max_x - min_x
        h = max_y - min_y

        ar = min(w, h) / max(w, h)

        if ar < q:
            q = ar

    return q
