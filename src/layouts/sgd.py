# Third Party Library
from egraph import Coordinates, Rng, SparseSgd


def sgd(eg_graph, eg_indices, params, seed):
    drawing = Coordinates.initial_placement(eg_graph)
    rng = Rng.seed_from(seed)
    sparse_sgd = SparseSgd(
        eg_graph,
        lambda _: params["edge_length"],
        params["number_of_pivots"],
        rng,
    )
    scheduler = sparse_sgd.scheduler(
        params["number_of_iterations"],
        params["eps"],
    )

    def step(eta):
        sparse_sgd.shuffle(rng)
        sparse_sgd.apply(drawing, eta)

    scheduler.run(step)

    pos = {u: (drawing.x(i), drawing.y(i)) for u, i in eg_indices.items()}

    return pos
