#!/bin/zsh
# usage: batch.sh <ModFolder> <Biome or ->
cd /home/mandrake/rm/foundry
if [ "$2" != "-" ]; then timeout 400 python.exe Transient/acc_biomes/retile.py $2 > Transient/acc_biomes/retile_$1.txt 2>&1; fi
timeout 1500 python.exe Transient/acc_biomes/run_live_suite.py $1 > Transient/acc_biomes/run_$1.txt 2>&1
echo "$1 done $?"
