#!/bin/sh

# rpfs: random params, free seed. rpfsで作成した描画結果を量産する。

CORE=1
DATASET_NAME=USpowerGrid

for core in `seq $CORE`
do
  nohup poetry run python generate_rp_pos.py $core $DATASET_NAME &
done
