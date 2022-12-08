#!/bin/sh

# args: dataset_name
# args: n_trials
# args: cpu_count



nohup poetry run python p_o.py $1 angular_resolution $2 $3 &&
nohup poetry run python p_o.py $1 aspect_ratio $2 $3 &&
nohup poetry run python p_o.py $1 crossing_angle $2 $3 &&
nohup poetry run python p_o.py $1 crossing_number $2 $3 &&
nohup poetry run python p_o.py $1 gabriel_graph_property $2 $3 &&
nohup poetry run python p_o.py $1 ideal_edge_length $2 $3 &&
nohup poetry run python p_o.py $1 node_resolution $2 $3 &&
nohup poetry run python p_o.py $1 run_time $2 $3 &&
nohup poetry run python p_o.py $1 shape_based_metrics $2 $3 &&
nohup poetry run python p_o.py $1 stress $2 $3
