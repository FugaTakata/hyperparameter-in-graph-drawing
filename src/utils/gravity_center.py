def gravity_center(pos):
    gx = 0
    gy = 0
    for node_id in pos:
        x, y = pos[node_id]
        gx += x
        gy += y

    gx /= len(pos)
    gy /= len(pos)

    return gx, gy
