#!/bin/bash
# r4_lab.sh OUTDIR : lay the four colonies, print the round-3/4 check counts for each
O=$1; mkdir -p $O
bash ralph/live/lab4.sh $O >/dev/null 2>&1
for L in Modern Scrapper Industrial Futuristic; do
  python3 ralph/live/lab_r3_checks.py Transient/lab/ba/worlds/ba_$L.json $O/ba_$L.out.json | head -1 | sed "s/^/$L /"
done
