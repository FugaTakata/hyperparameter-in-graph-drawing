from egraph import Coordinates, KamadaKawai


def kamada_kawai(graph, indices, params):
    drawing = Coordinates.initial_placement(graph)
    kamada_kawai = KamadaKawai(graph, lambda _: params['edge_length'])
    kamada_kawai.eps = params['eps']
    kamada_kawai.run(drawing)

    pos = {u: (drawing.x(i), drawing.y(i)) for u, i in indices.items()}

    return pos
