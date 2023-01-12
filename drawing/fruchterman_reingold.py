# Third Party Library
import networkx as nx


def fruchterman_reingold(nx_graph, params):
    pos = nx.spring_layout(
        G=nx_graph,
        k=params["k"],
        fixed=params["fixed"],
        iterations=params["iterations"],
        threshold=params["threshold"],
        weight=params["weight"],
        scale=params["scale"],
        center=params["center"],
        dim=params["dim"],
        seed=params["seed"],
        pos=params["pos"],
    )

    for key in pos:
        p = pos[key]
        pos[key] = [float(p[0]), float(p[1])]

    return pos
