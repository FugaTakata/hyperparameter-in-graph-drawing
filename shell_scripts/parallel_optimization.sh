#!/bin/sh

# args: dataset_name
# args: n_trials
# args: cpu_count

# for Q in angular_resolution aspect_ratio crossing_angle crossing_number gabriel_graph_property ideal_edge_length node_resolution run_time shape_based_metrics stress
# do
# poetry run python parallel_optimization.py $1 $Q $2 $3 &&
# done

poetry run python parallel_optimization.py $1 angular_resolution $2 $3 &&
poetry run python parallel_optimization.py $1 aspect_ratio $2 $3 &&
poetry run python parallel_optimization.py $1 crossing_angle $2 $3 &&
poetry run python parallel_optimization.py $1 crossing_number $2 $3 &&
poetry run python parallel_optimization.py $1 gabriel_graph_property $2 $3 &&
poetry run python parallel_optimization.py $1 ideal_edge_length $2 $3 &&
poetry run python parallel_optimization.py $1 node_resolution $2 $3 &&
poetry run python parallel_optimization.py $1 run_time $2 $3 &&
poetry run python parallel_optimization.py $1 shape_based_metrics $2 $3 &&
poetry run python parallel_optimization.py $1 stress $2 $3
