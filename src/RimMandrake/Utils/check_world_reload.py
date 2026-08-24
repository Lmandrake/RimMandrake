#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_world_reload.py - score the 2026-08-24 world reload in one command.

Written BEFORE the load, deliberately: every threshold in here is a prediction made
while the evidence was still in the running game, so it cannot be retrofitted to
whatever the reload happens to produce. The matching prose is
`infrastructure/state/EXPECTED_FAILURES_next_load.md` §21.

🔴 RUN WITH python.exe, NOT python3 - the bridge binds Windows loopback.

    python.exe src/RimMandrake/Utils/check_world_reload.py

It is READ-ONLY apart from one export to a temp path. It needs the world loaded;
no map is required.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORLD = os.path.join(REPO, "world")
BASELINE = os.path.join(WORLD, "ASHKARR_DRAFT_2026-08-24_tiles.csv")
PROBE_EXPORT = os.path.join(WORLD, "_reload_probe_tiles.csv")

# The eleven settlements moved on 2026-08-24, and where they must be.
MOVED = {
    "No Master": 19350, "Second Speaker": 9936, "Helix Landing": 11944,
    "The Coil": 15926, "Quiet Lab": 5499, "The Free Charge": 3653,
    "Cell Seven": 11250, "No Owner": 21549, "Vent Forty": 11243,
    "Vent Twelve": 14480, "The Cracking Yard": 13180,
}

results = []


def score(name, ok, detail):
    results.append((ok, name, detail))
    print("%-6s %-34s %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    if not os.path.exists(BASELINE):
        sys.exit("missing baseline: " + BASELINE)
    base = {int(r["tile"]): r for r in csv.DictReader(open(BASELINE))}
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=900.0) as rb:

        # P1 - the companion registered. Companions register at RimBridgeServer
        # startup only, so a low count means the deploy did not take.
        tools = rb.call("rimbridge/get_bridge_status", {})
        names = []
        try:
            names = [t["name"] if isinstance(t, dict) else t for t in (rb.list_tools() or [])]
        except Exception:
            pass
        jawa = [n for n in names if n.startswith("jawa/")]
        score("P1 companion registered", len(jawa) >= 121,
              "%d jawa/ tools (predicted >= 121)" % len(jawa) if jawa
              else "could not enumerate; check bridge status manually")

        # P2 - THE DEPLOY PROOF. pollution became BASE column 10 in commit ab02ef75.
        # If the old DLL is live this comes back with nine columns and NO error,
        # which is the whole reason this check exists.
        exp = rb.call("jawa/world_tile_export", {"path": PROBE_EXPORT})
        cols = exp.get("columns") or []
        score("P2 pollution is base col 10",
              len(cols) == 10 and cols[9] == "pollution",
              "%d columns, last = %r" % (len(cols), cols[-1] if cols else None))

        # P3 - the Cathedral's poison survived the save/load round trip.
        cath = [t for t, r in base.items() if float(r.get("pollution") or 0) >= 0.90]
        sample = cath[:60]
        got = rb.call("jawa/world_tile_get", {"tiles": ",".join(str(t) for t in sample)})
        pol = [t["pollution"] for t in got.get("tiles", [])]
        score("P3 Cathedral pollution survived",
              bool(pol) and min(pol) >= 0.85,
              "%d sampled of %d at >=0.90, min read back %.2f"
              % (len(pol), len(cath), min(pol) if pol else -1))

        # P4 - the whole planet matches what was harvested before the quit.
        val = rb.call("jawa/world_tile_validate",
                      {"path": BASELINE, "expectTiles": 21872})
        score("P4 planet matches the harvest",
              val.get("success") and val.get("mismatched") == 0,
              "%s/%s matched, byField=%s"
              % (val.get("matched"), val.get("rows"), val.get("byField")))

        # P5 - lint. 18 roadless settlements is INTENT as of 2026-08-24 (9 Tusken
        # holdings + 5 droid seats + 3 unplanned + the rest), not a regression.
        lint = rb.call("jawa/world_lint", {})
        checks = lint.get("checks", {})
        noroad = (checks.get("settlementsWithNoRoad") or {}).get("count")
        trunk = (checks.get("riverSystems") or {}).get("trunkSystemsReachingNoSea")
        score("P5 lint unchanged", noroad == 18 and trunk == 1,
              "noRoad=%s (predicted 18), orphanTrunks=%s (predicted 1)" % (noroad, trunk))

        # P6 - the settlements are where they were put.
        objs = rb.call("jawa/world_objects_get", {"limit": 4000})
        pos = {(o.get("name") or o.get("label")): o["tile"]
               for o in objs.get("objects", []) if o.get("isSettlement")}
        wrong = {k: (pos.get(k), v) for k, v in MOVED.items() if pos.get(k) != v}
        score("P6 moved settlements held",
              len(pos) == 124 and not wrong,
              "%d settlements, %d of 11 moves intact %s"
              % (len(pos), 11 - len(wrong), wrong if wrong else ""))

    try:
        os.remove(PROBE_EXPORT)
    except OSError:
        pass
    bad = [r for r in results if not r[0]]
    print("\n%d/%d passed." % (len(results) - len(bad), len(results)))
    if bad:
        print("🔴 FAILED: " + ", ".join(r[1] for r in bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
