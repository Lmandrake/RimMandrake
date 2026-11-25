#!/usr/bin/env python3
"""Outcome check of RIMMANDRAKE_TRACE_FLOWWORKS_BOTTLE_LOOP_EMPTY_GONE_NONE_FILLED: a LIVE run of FlowWorks
toggle_bottle_loop with the map-wide census (landed at REPAIR_SHA) read bottle_loop_on PASS and bottle_loop_off PASS.
A modcheck JSON carries no build sha, so "the repaired chain ran" is read from the run itself: each component's
evidence holds a ProofBottleCount BOTTLES reading, which the old plot-only chain never made.

The proof is the run's own modcheck JSON, committed in this folder (Transient/ is untracked, so a Transient path proves
nothing on origin/main). A recorded `verify --result pass` alone is paper and does not count.

    python3 design/specs/2026-11-25-bottle-loop-map-wide/accept_live.py

Exit 0: such a run is here. 1: none yet (the need is unmet, or not yet shown). 2: could not look.
How to satisfy it: run `extension_proof.py --live --chains toggle_bottle_loop` (or a testq job with
--chains toggle_bottle_loop) on a free game, copy its FlowWorks_<stamp>.json here as live_<stamp>.json, commit it.
If bottle_loop_on reads FAIL there, its detail now names where every bottle is and what the colonists do: class it
(a bottle lost by the fill is a MOD fault, fix JobDriver_FillBottle) before anything is committed here.
"""
import glob
import json
import os
import sys

REPAIR_SHA = "35eb8208a17dc62e3bc68d06f241777172afdca1"   # where the map-wide census landed (provenance)
HERE = os.path.dirname(os.path.abspath(__file__))
WANT = ("bottle_loop_on", "bottle_loop_off")


def chain_rows(path):
    """{component: (verdict, counted map-wide)} of the toggle_bottle_loop chain in a modcheck JSON; None if absent."""
    with open(path) as f:
        d = json.load(f)
    for ch in (d.get("summary") or {}).get("chains") or []:
        if ch.get("name") == "toggle_bottle_loop":
            out = {}
            for c in ch.get("components") or []:
                mw = any("ProofBottleCount" in str((e.get("result") or {}).get("method"))
                         and str((e.get("result") or {}).get("result", "")).startswith("BOTTLES")
                         for e in c.get("evidence") or [])
                out[c.get("name")] = (c.get("verdict"), mw)
            return out
    return None


def main():
    runs = sorted(glob.glob(os.path.join(HERE, "live_*.json")))
    if not runs:
        print("NOT MET: no live run of toggle_bottle_loop is committed in %s" % HERE)
        return 1
    for p in runs:
        try:
            v = chain_rows(p)
        except (OSError, ValueError) as e:
            print("COULD NOT LOOK: %s unreadable: %s" % (p, e))
            return 2
        if v is None:
            print("skip %s: no toggle_bottle_loop chain" % os.path.basename(p))
            continue
        if not all(v.get(k, (None, False))[1] for k in WANT):
            print("skip %s: not the map-wide chain (no ProofBottleCount reading): %s" % (os.path.basename(p), v))
            continue
        if all(v[k][0] == "PASS" for k in WANT):
            print("MET: %s reads %s" % (os.path.basename(p), v))
            return 0
        print("skip %s: %s" % (os.path.basename(p), v))
    print("NOT MET: no committed live run on the repaired build reads bottle_loop_on and bottle_loop_off PASS")
    return 1


if __name__ == "__main__":
    sys.exit(main())
