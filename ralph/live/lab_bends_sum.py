#!/usr/bin/env python3
"""Sum the lab's never_taut_straight_cord count (LabWorld "bends") per look and piece kind. python3 ralph/live/lab_bends_sum.py OUTDIR"""
import json, sys, glob, os
from collections import Counter
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.out.json"))):
    B = json.load(open(f))["bends"]
    c = Counter()
    for r in B["rows"]:
        if r["why"] != "unforced": continue
        a = r["piece"].split("|")
        kind = a[0].split(":")[0] + "|" + (a[1].split(":")[0] if len(a) > 1 else "")
        c[(kind, "end" if r["fromEnd"] < 0.75 else "mid")] += 1
    print(os.path.basename(f), "unforced", B["unforced"], B["why"])
    print("   ", ", ".join("%s %s:%d" % (k[0], k[1], v) for k, v in c.most_common()))
