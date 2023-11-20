# Third Party Library
import numpy as np

direction = "minimize"


# pivots (|E| + |V| log |V|) + iterations (pivots |V| + |E|)
def measure(pivots, iterations, n_nodes, n_edges):
    return pivots * (n_edges + n_nodes * np.log2(n_nodes)) + iterations * (
        pivots * n_nodes + n_edges
    )
