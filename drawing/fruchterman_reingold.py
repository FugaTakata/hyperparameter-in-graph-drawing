import networkx as nx


def fruchterman_reingold(nx_graph, initial_pos, params):
    pos = nx.spring_layout(
        nx_graph,
        k=params['k'],
        fixed=params['fixed'],
        iterations=params['iterations'],
        threshold=params['threshold'],
        weight=params['weight'],
        scale=params['scale'],
        center=params['center'],
        dim=params['dim'],
        seed=params['seed'],
        pos=initial_pos
    )

    return pos
