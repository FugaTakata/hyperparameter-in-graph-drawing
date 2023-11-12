
poetry run python generate_grid.py -d 1138_bus --seeds 0 -n 10 && \
poetry run python optimize_scaled_sum.py -d 1138_bus -n 500 && \
poetry run python generate_grid.py -d USpowerGrid --seeds 0 -n 10 && \
poetry run python optimize_scaled_sum.py -d USpowerGrid -n 500 && \
say finished