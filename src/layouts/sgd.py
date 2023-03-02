# Third Party Library
from egraph import Rng, SparseSgd


def sgd(eg_graph, eg_indices, eg_drawing, params, seed):
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
        sparse_sgd.apply(eg_drawing, eta)

    scheduler.run(step)

    pos = {
        u: (eg_drawing.x(i), eg_drawing.y(i)) for u, i in eg_indices.items()
    }

    return pos
