# Standard Library
from itertools import combinations


def is_edge_crossing(p1, p2, p3, p4):
    tc1 = (p1[0] - p2[0]) * (p3[1] - p1[1]) + (p1[1] - p2[1]) * (p1[0] - p3[0])
    tc2 = (p1[0] - p2[0]) * (p4[1] - p1[1]) + (p1[1] - p2[1]) * (p1[0] - p4[0])
    td1 = (p3[0] - p4[0]) * (p1[1] - p3[1]) + (p3[1] - p4[1]) * (p3[0] - p1[0])
    td2 = (p3[0] - p4[0]) * (p2[1] - p3[1]) + (p3[1] - p4[1]) * (p3[0] - p2[0])
    return tc1 * tc2 < 0 and td1 * td2 < 0


def edge_crossing_finder_naive(nx_graph, pos):
    edges = {}
    for s1, t1, attr1 in nx_graph.edges(data=True):
        id1 = attr1["id"]
        if id1 not in edges:
            edges[id1] = {}
        for s2, t2, attr2 in nx_graph.edges(data=True):
            id2 = attr2["id"]
            crossing = is_edge_crossing(pos[s1], pos[t1], pos[s2], pos[t2])
            edges[id1][id2] = crossing

    return edges


def edge_crossing_finder(nx_graph, pos):
    edges = {
        ((s1, t1), (s2, t2))
        for (s1, t1), (s2, t2) in combinations(nx_graph.edges(), 2)
        if is_edge_crossing(pos[s1], pos[t1], pos[s2], pos[t2])
    }
    return edges
