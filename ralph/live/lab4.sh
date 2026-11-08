#!/bin/bash
# lab4.sh OUTDIR : lay the four played colonies' worlds in the shape lab (one build), print the bar's count
O=$1; mkdir -p $O
for L in Modern Scrapper Industrial Futuristic; do
  python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --lab Transient/lab/ba/worlds/ba_$L.json $O/ba_$L.out.json 2>&1 | grep -E "^bends|error|FAIL" | sed "s/^/$L /"
done
