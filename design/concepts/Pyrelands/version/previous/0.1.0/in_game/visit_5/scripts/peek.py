#!/usr/bin/env python3
"""Print each pv5_<label>.json's component verdicts in one line (non-PASS components named)."""
import glob, json, os, sys
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence")
for p in sorted(glob.glob(os.path.join(d, "pv5_*.json")), key=os.path.getmtime):
    j = json.load(open(p))
    cs = [c for c in j.get("components", []) if not str(c.get("name")).startswith("skipped")]
    bad = ["%s=%s" % (c.get("name"), c.get("verdict")) for c in cs if c.get("verdict") != "PASS"]
    print("%-40s %d comps, %d PASS %s %s" % (os.path.basename(p)[4:-5], len(cs), len(cs) - len(bad),
          ("refused: " + str(j["refused"])) if j.get("refused") else "", " ".join(bad)))
