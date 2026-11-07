#!/usr/bin/env python3
"""Where the audit's sharp corners are: under a machine's art (hidden, no matter), near a strand's end, or out on the open cord. Runs on lab files."""
import json, sys, math
from collections import Counter
W = json.load(open(sys.argv[1])); L = json.load(open(sys.argv[2]))
def inm(x, z):
    return any(m["x"] <= x <= m["x"] + m["w"] and m["z"] <= z <= m["z"] + m["h"] for m in W["machines"])
blocked = {(a[0], a[1]) for a in W["blocked"]}
c = Counter(); open_rows = []
for r in L["audit"]["rows"]:
    if "sharp" not in r: continue
    x, z = r["sharp"]
    if inm(x, z): c["under machine"] += 1; continue
    if (int(x), int(z)) in blocked: c["in wall"] += 1; continue
    best = None
    for p in L["pieces"]:
        if p["a"] + "|" + p["b"] != r["piece"]: continue
        for s in p["strands"]:
            d0 = math.hypot(s[0][0] - x, s[0][1] - z); d1 = math.hypot(s[-1][0] - x, s[-1][1] - z)
            d = min(d0, d1)
            best = d if best is None else min(best, d)
    kind = "within 0.5 of an end" if best is not None and best < 0.5 else "open"
    c[kind] += 1
    if kind == "open" or len(open_rows) < 8: open_rows.append((x, z, round(best or -1, 2), r["piece"]))
print(dict(c)); print(json.dumps(L["audit"]["corners"]), "corners,", L["audit"]["sharpStrands"], "strands")
for q in open_rows[:int(sys.argv[3]) if len(sys.argv) > 3 else 14]: print(q)
