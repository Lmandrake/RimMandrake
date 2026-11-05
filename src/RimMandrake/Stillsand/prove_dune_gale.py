#!/usr/bin/env python3
"""STILLSAND_DUNE_GALE_LIVE_1 live proofs A1-A4: run the Stillsand gale chain up to its carry row once, then judge
one clause off modcheck's own results JSON (Transient/modcheck/Stillsand_*.json, runner.write_sheet), never the console.

  A1, A3  gale_phases_and_aftermath    the '[Stillsand] dune gale ended on ... (delta ...); cells moved past ...' line
                                       with a non-zero delta or cell count (A1); exactly one emergence letter and every
                                       thing it placed still on the map (A3)
  A2      gale_dims_sun_exposure       a colonist on the open anchor cell reads ~0.2 (0.15..0.25) of its clear-sky
                                       ShadeGrid.ExposureFor in the gale
  A4      gale_carry_drag_and_return   a dragged colonist leaves RM_Filth_DragMark (or a 'Carried off' letter), one
                                       carried off the edge gets 'Carried off' and comes back

One gale serves every clause: a results JSON from the last REUSE_S seconds that holds all three rows is judged
instead of running the chain again, so the four live-proof lines cost one 6000-tick gale.

Exit: 0 PASS, 1 FAIL / UNMEASURED row / row missing / unknown clause, 2 nothing measured: no results JSON written, or
the sheet modcheck wrote is a refusal (summary.refused or summary.unmeasured set, e.g. stale_load: the running game is
not on the composed list) so no gale ran and no Stillsand behaviour was observed.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLAUSES = {"A1": "gale_phases_and_aftermath", "A3": "gale_phases_and_aftermath",
           "A2": "gale_dims_sun_exposure", "A4": "gale_carry_drag_and_return"}
ROWS = ["gale_phases_and_aftermath", "gale_dims_sun_exposure", "gale_carry_drag_and_return"]
REUSE_S = 1800


def _summary(path):
    try:
        summary = json.load(open(path, encoding="utf-8"))["summary"]
    except (OSError, ValueError, KeyError):
        return {}
    return summary if isinstance(summary, dict) else {}


def _refusal(path):
    """The sheet's own refusal (runner.py writes chains=[] with `refused` and/or `unmeasured`), or None."""
    s = _summary(path)
    why, cause = s.get("refused"), s.get("unmeasured")
    if not why and not cause:
        return None
    return "%s%s" % (("[%s] " % cause) if isinstance(cause, str) and cause else "", why or "")


def _components(path):
    summary = _summary(path)
    out = {}
    for ch in summary.get("chains") or []:
        for c in ch.get("components") or []:
            out[c.get("name")] = c
    return out


def _results(since):
    paths = [p for p in glob.glob(os.path.join(ROOT, "Transient", "modcheck", "Stillsand_*.json"))
             if os.path.getmtime(p) >= since]
    return sorted(paths, key=os.path.getmtime, reverse=True)


def _reusable(now):
    for p in _results(now - REUSE_S):
        if all(r in _components(p) for r in ROWS):
            return p
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clause", required=True)
    a = ap.parse_args(argv)
    row = CLAUSES.get(a.clause)
    if row is None:
        print("unknown clause %r (have %s)" % (a.clause, ", ".join(sorted(CLAUSES))))
        return 1
    start = time.time()
    path = _reusable(start)
    if path is None:
        rc = subprocess.call([sys.executable, "-m", "modcheck.cli", "run", "Stillsand", "--rows", ",".join(ROWS),
                              "--item", "STILLSAND_DUNE_GALE_LIVE_1"],
                             cwd=os.path.join(ROOT, "src", "RimMandrake", "Utils"), stdin=subprocess.DEVNULL)
        fresh = _results(start)
        if not fresh:
            print("NO RESULTS: modcheck exited %d and wrote no Stillsand results JSON" % rc)
            return 2
        path = fresh[0]
    c = _components(path).get(row)
    if c is None:
        why = _refusal(path)
        if why:
            print("UNMEASURED: %s %s not run: modcheck refused the run: %s (%s)" % (a.clause, row, why[:600], path))
            return 2
        print("%s %s missing from %s" % (a.clause, row, path))
        return 1
    print("%s %s: %s -- %s (%s)" % (a.clause, row, c.get("verdict"), str(c.get("detail"))[:600], path))
    return 0 if c.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
