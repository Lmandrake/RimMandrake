#!/usr/bin/env python3
"""Print each chain's own component rows (verdict, name, evidence head) from the visit's pv3_<chain>.json files."""
import glob, json, os, sys
E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence")
want = sys.argv[1:]
for p in sorted(glob.glob(os.path.join(E, "pv3_*.json"))):
    c = os.path.basename(p)[4:-5]
    if want and c not in want:
        continue
    d = json.load(open(p))
    rows = [r for r in d.get("components", []) if r.get("chain") == c]
    if d.get("refused"):
        print("%s REFUSED %s" % (c, d["refused"]))
    for r in rows:
        ev = r.get("evidenceFull") or ""
        print("%-10s %s/%s  %s" % (r.get("verdict"), c, r.get("name"), str(ev)[:int(os.environ.get("W", "220"))]))
