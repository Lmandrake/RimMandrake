#!/usr/bin/env python3
"""repeats.py - runs of one same not-DONE note, one after the other, on one game. 'Saved' = the run less its first two."""
import collections, re
from common import *
R, _ = records(); out = []
key = lambda d: None if d["result"].get("outcome") == "DONE" else re.sub(r"[0-9a-f]{6,}|\d+", "#", str(d["result"].get("note")))[:60]
for h in (None, "stevedesktop.b"):
    prev, n, first = None, 0, None
    for d in [x for x in R if x.get("host") == h] + [None]:
        k = key(d) if d else None
        if k and k == prev: n += 1
        else:
            if prev and n >= 3: out.append((n, h or "Steve1", first["_fin"].strftime("%m-%d %H:%MZ"), prev))
            n, first = 1, d
        prev = k
out.sort(reverse=True)
for o in out: print(o)
print("runs of 3 or more:", len(out), "jobs", sum(o[0] for o in out), "saved by a stop after two:", sum(o[0] - 2 for o in out), "of them Steve2 refusals", sum(o[0] - 2 for o in out if "is running" in o[3]))
