from egraph import Graph, Coordinates, Rng, SparseSgd


def sgd(graph, indices, params, seed=0):
    drawing = Coordinates.initial_placement(graph)
    rng = Rng.seed_from(seed)
    sparse_sgd = SparseSgd(
        graph,
        lambda _: params['edge_length'],
        params['number_of_pivots'],
        rng
    )
    scheduler = sparse_sgd.scheduler(
        params['number_of_iterations'],  # number of iterations
        params['eps'],  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    def step(eta):
        sparse_sgd.shuffle(rng)
        sparse_sgd.apply(drawing, eta)

    scheduler.run(step)

    pos = {u: (drawing.x(i), drawing.y(i))
           for u, i in indices.items()}

    return pos
