#!/usr/bin/env python3
"""scene_rows_add.py -- one rows.jsonl row from a `validation.py --scene <entry> --out <json>` result (the 0.1.1 self-built scenes).

    python3 scene_rows_add.py <scene json> --test sc_x --identity <identity.json> [--class HARNESS --why "..."]
        [--repair '<json>'] [--held a,b]
The verdict is the result's own status (its SCENE_ row), never set by hand; --class/--why/--repair only describe it.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import visit_rows as VR  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("result")
ap.add_argument("--test", required=True)
ap.add_argument("--identity", required=True)
ap.add_argument("--label", required=True)
ap.add_argument("--klass", dest="klass")
ap.add_argument("--why")
ap.add_argument("--repair")
ap.add_argument("--held", default="")
a = ap.parse_args()
res = json.load(open(a.result))
ident = json.load(open(a.identity))
VR.IDENT.update(ident)
VR.HELD.extend(h for h in a.held.split(",") if h)
t = VR.stage6()[a.test]
rows = {r["id"]: r["status"] for r in res.get("rows") or []} or {k: res[k] for k in ("result", "save", "rect") if k in res}
row = {"test": a.test, "verdict": res.get("status") or res.get("result"), "site_checked": True, "game": "archmagi", "mod_sha": ident["mod_sha"],
       "command": t["command"], "evidence": os.path.relpath(os.path.abspath(a.result), VR.REPO), "run": a.label,
       "detail": rows, "game_instance": "ArchBig"}
if a.klass:
    row["class"] = a.klass
if a.why:
    row["why"] = a.why
if a.repair:
    row["repair"] = json.loads(a.repair)
VR.append(row)
print("appended %s %s" % (a.test, row["verdict"]))
