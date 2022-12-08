#!/bin/sh

# args: dataset_name
# args: n_seed

# poetry run python generate_opfs.py $1 all $2 angular_resolution &
# poetry run python generate_opfs.py $1 all $2 aspect_ratio &
# poetry run python generate_opfs.py $1 all $2 crossing_angle &
# poetry run python generate_opfs.py $1 all $2 crossing_number &
poetry run python generate_opfs.py $1 all $2 gabriel_graph_property &
poetry run python generate_opfs.py $1 all $2 ideal_edge_length &
poetry run python generate_opfs.py $1 all $2 node_resolution &
poetry run python generate_opfs.py $1 all $2 run_time &
poetry run python generate_opfs.py $1 all $2 shape_based_metrics &
poetry run python generate_opfs.py $1 all $2 stress


# echo 'finished'/data
