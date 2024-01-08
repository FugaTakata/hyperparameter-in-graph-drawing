poetry run python generate_grid.py -d 1138_bus -n 5 --seed 10 & 
sleep 10 
poetry run python generate_grid.py -d 1138_bus -n 5 --seed 11 & 
sleep 10 
poetry run python generate_grid.py -d 1138_bus -n 5 --seed 12 & 
sleep 10 
poetry run python generate_grid.py -d 1138_bus -n 5 --seed 13 & 
sleep 10 
poetry run python generate_grid.py -d 1138_bus -n 5 --seed 14 & 
sleep 10 
wait 
poetry run python generate_grid.py -d USpowerGrid -n 5 --seed 10 & 
sleep 10 
poetry run python generate_grid.py -d USpowerGrid -n 5 --seed 11 & 
sleep 10 
poetry run python generate_grid.py -d USpowerGrid -n 5 --seed 12 & 
sleep 10 
poetry run python generate_grid.py -d USpowerGrid -n 5 --seed 13 & 
sleep 10 
poetry run python generate_grid.py -d USpowerGrid -n 5 --seed 14 & 
sleep 10 
wait 
poetry run python generate_grid.py -d dwt_1005 -n 5 --seed 10 & 
sleep 10 
poetry run python generate_grid.py -d dwt_1005 -n 5 --seed 11 & 
sleep 10 
poetry run python generate_grid.py -d dwt_1005 -n 5 --seed 12 & 
sleep 10 
poetry run python generate_grid.py -d dwt_1005 -n 5 --seed 13 & 
sleep 10 
poetry run python generate_grid.py -d dwt_1005 -n 5 --seed 14 & 
sleep 10 
wait 
poetry run python generate_grid.py -d poli -n 5 --seed 10 & 
sleep 10 
poetry run python generate_grid.py -d poli -n 5 --seed 11 & 
sleep 10 
poetry run python generate_grid.py -d poli -n 5 --seed 12 & 
sleep 10 
poetry run python generate_grid.py -d poli -n 5 --seed 13 & 
sleep 10 
poetry run python generate_grid.py -d poli -n 5 --seed 14 & 
sleep 10 
wait 
poetry run python generate_grid.py -d qh882 -n 5 --seed 10 & 
sleep 10 
poetry run python generate_grid.py -d qh882 -n 5 --seed 11 & 
sleep 10 
poetry run python generate_grid.py -d qh882 -n 5 --seed 12 & 
sleep 10 
poetry run python generate_grid.py -d qh882 -n 5 --seed 13 & 
sleep 10 
poetry run python generate_grid.py -d qh882 -n 5 --seed 14 & 
sleep 10 
wait 
curl -X POST -H "Content-Type: application/json" -d '{"content":"yu :100 12/08 16:58:00"}' https://discord.com/api/webhooks/1077614514792562720/9zpqdP7ec4r5ZjNUc3gTygVBTU8tGI7ownYk5CUbbFb2r3mG6kZwElOgL3fAZDYpjX8K