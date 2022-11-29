def fm3(tlp_graph, params):
    pos = {}

    position = tlp_graph.getLayoutProperty('position')
    tlp_graph.applyLayoutAlgorithm('FM^3 (OGDF)', position, params)

    pos = {}

    for i in tlp_graph.getNodes():
        node = tlp_graph.getNodePropertiesValues(i)
        pos[node['nx_id']] = [position[i][0], position[i][1]]

    return pos
