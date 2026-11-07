#!/usr/bin/env python3
"""prove_shock_outlives_wire_verdict.py <flips.json>: the verdict step of GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE's live line.

Reads the JSON `validation_aerial.py --flips` wrote this run. Exit 0: row M20e_shock_cells_die_with_wire PASS. Exit 1: that row
FAIL. Exit 2 with `UNMEASURED: <reason>` as the last line: anything else, since a run that never measured the row says nothing
about the mod. The 2026-11-06T15:01Z run aborted at A_probe_channel with no map; its inline verdict read that as exit 1, a FAIL
against a mod the run never asked. A file this script cannot parse is the same case: a traceback here would also exit 1.
"""
import json
import os
import sys
import time

ROW = "M20e_shock_cells_die_with_wire"
FRESH_S = 1800      # the line removes the old file first; this is the second lock against an earlier run's verdict


def unmeasured(why):
    print("UNMEASURED: M20e not measured: " + why)
    return 2


def main(argv):
    if len(argv) != 2:
        return unmeasured("the verdict step takes one path")
    try:
        age = time.time() - os.path.getmtime(argv[1])
        with open(argv[1], encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as ex:         # never written (a crash, a dead bridge), or half written
        return unmeasured("no readable flips.json from this run (%s)" % type(ex).__name__)
    if age >= FRESH_S:
        return unmeasured("flips.json is from an earlier run")
    if not isinstance(d, dict) or not isinstance(d.get("rows"), list):
        return unmeasured("flips.json holds no row list")
    rows = [r for r in d["rows"] if isinstance(r, dict)]
    hits = [r for r in rows if r.get("id") == ROW]
    if not hits:
        others = [(r.get("id"), r.get("status")) for r in rows if r.get("status") != "PASS"]
        return unmeasured("the run has no such row (aborted: %s; not PASS: %s)" % (d.get("aborted"), others))
    row = hits[0]
    status = row.get("status")
    if status not in ("PASS", "FAIL"):
        return unmeasured("the row reads %s %s: %s" % (status, row.get("class"), row.get("detail")))
    print("%s: %s %s %s" % (ROW, status, row.get("class"), json.dumps(row.get("detail"), default=str)))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
