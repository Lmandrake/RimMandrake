#!/usr/bin/env python3
"""BONES_LEAN_PORT_BUILD_TREELESS_WORLD live proofs G1-G4: run the Bones suite (src/RimMandrake/Bones/validation.py)
once, then judge one clause off modcheck's own results JSON (Transient/modcheck/Bones_*.json), never the console.

  G1  bone_is_woody_stuff_no_donor_defs  RM_Bones is Woody stuff a Wall accepts; stat + floor loaded; no donor def
  G2  donor_bone_defs_load_as_ours        BoneChina/BoneItem/Bonecrete/BonePlastic -> RM_Bones and the five donor
                                          floors -> RM_BoneFloor through the real BackCompatibility entry points
  G3  butchering_yields_bones_gated       real Pawn.ButcherProducts: muffalo yields bones, megascarab none, none off
  G4  no_errors_naming_this_mod           no load error names RimMandrake.Bones / RM_Bones* defs

One run serves every clause: a results JSON from the last REUSE_S seconds that holds all four rows is judged
instead of running the suite again.

Exit: 0 PASS, 1 FAIL / UNMEASURED / row missing / unknown clause, 2 no results JSON written.
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
CLAUSES = {"G1": "bone_is_woody_stuff_no_donor_defs", "G2": "donor_bone_defs_load_as_ours",
           "G3": "butchering_yields_bones_gated", "G4": "no_errors_naming_this_mod"}
ROWS = list(CLAUSES.values())
REUSE_S = 1800


def _components(path):
    try:
        summary = json.load(open(path, encoding="utf-8"))["summary"]
    except (OSError, ValueError, KeyError):
        return {}
    out = {}
    for ch in summary.get("chains") or []:
        for c in ch.get("components") or []:
            out[c.get("name")] = c
    return out


def _results(since):
    paths = [p for p in glob.glob(os.path.join(ROOT, "Transient", "modcheck", "Bones_*.json"))
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
        rc = subprocess.call([sys.executable, "-m", "modcheck.cli", "run", "Bones", "--rows", ",".join(ROWS),
                              "--item", "BONES_LEAN_PORT_BUILD_TREELESS_WORLD"],
                             cwd=os.path.join(ROOT, "src", "RimMandrake", "Utils"), stdin=subprocess.DEVNULL)
        fresh = _results(start)
        if not fresh:
            print("NO RESULTS: modcheck exited %d and wrote no Bones results JSON" % rc)
            return 2
        path = fresh[0]
    c = _components(path).get(row)
    if c is None:
        print("%s %s missing from %s" % (a.clause, row, path))
        return 1
    print("%s %s: %s -- %s (%s)" % (a.clause, row, c.get("verdict"), str(c.get("detail"))[:600], path))
    return 0 if c.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
