#!/bin/sh

# args: dataset_name
# args: n_seed
# args: params_from

# poetry run python apply.py $1 all $2 angular_resolution $3 &
# poetry run python apply.py $1 all $2 aspect_ratio $3 &
# poetry run python apply.py $1 all $2 crossing_angle $3 &
# poetry run python apply.py $1 all $2 crossing_number $3 &
poetry run python apply.py $1 all $2 gabriel_graph_property $3 &
poetry run python apply.py $1 all $2 ideal_edge_length $3 &
poetry run python apply.py $1 all $2 node_resolution $3 &
poetry run python apply.py $1 all $2 run_time $3 &
poetry run python apply.py $1 all $2 shape_based_metrics $3 &
poetry run python apply.py $1 all $2 stress $3


# echo 'finished'/data
