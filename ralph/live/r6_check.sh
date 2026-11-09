#!/bin/bash
# r6_check.sh OUTDIR : lay the four looks, print unforced bends per look and those within 0.75 cell of a strip end (strip_exit) and those near an end sharper than 60 deg within 0.1 cell (sharp_exit, the squared elbows the judge sees; baseline 2/3/4/4)
O=${1:-Transient/r6/cur}; mkdir -p $O
bash ralph/live/lab4.sh $O 2>&1 | grep -E "error|FAIL"
for L in Modern Scrapper Industrial Futuristic; do
  python3 - "$O/ba_$L.out.json" $L <<'P'
import json, sys
d = json.load(open(sys.argv[1])); u = [r for r in d["bends"]["rows"] if r["why"] == "unforced"]
s = [r for r in u if r["fromEnd"] <= 0.75 and r["piece"].startswith("junction")]
sh = [r for r in u if r["fromEnd"] <= 0.8 and r["sharp"] > 60]
print("%s unforced=%d strip_exit=%d sharp_exit=%d" % (sys.argv[2], len(u), len(s), len(sh)))
P
done
