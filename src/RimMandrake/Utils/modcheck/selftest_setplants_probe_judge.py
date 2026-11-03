#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1: offline proof that the live A2 probe (setplants_reason_probe.py) can tell the fixed
set_plants from the pre-fix one, so a green A2 means the clause holds and not that the judge is loose.

The probe's verdict is the pure function judge(result). Here it is fed results shaped exactly as JawaBenchTerrainTools.cs
set_plants builds them (Reject("terrain or conditions cannot support <def>: <why>"), one rejectedCells row of
x/z/terrain/fertility/fertilityMin/polluted/blocker/reason) and must:
  - accept the fixed tool's answer on a PackedDirt cell (Core: fertility 0 < Plant_Grass fertilityMin 0.05);
  - reject the pre-fix answer (generic reason, no rejectedCells) and every single-field break of the fixed one;
  - send a blocked cell to 'blocker' (try another cell), never to 'ok'.
Sanity probe: a judge that answers 'ok' to anything must fail this test (checked in-process below).
Exit 0 all hold, 1 any fails.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import setplants_reason_probe as probe  # noqa: E402

REASON = "Need more fertile terrain."
FIXED = {
    "planted": 0, "rejected": 1,
    "rejectionReasons": {probe.GENERIC + ": " + REASON: 1},
    "rejectedCells": [{"x": 10, "z": 12, "terrain": "PackedDirt", "fertility": 0.0, "fertilityMin": 0.05,
                       "polluted": False, "blocker": None, "reason": REASON}],
}
PREFIX = {"planted": 0, "rejected": 1, "rejectionReasons": {probe.GENERIC: 1}}


def variant(**edits):
    """FIXED with top-level ('planted') or row ('row.terrain') fields replaced; a reason edit moves both copies."""
    r = copy.deepcopy(FIXED)
    for k, v in edits.items():
        if k.startswith("row."):
            r["rejectedCells"][0][k[4:]] = v
        elif k == "reason":
            r["rejectionReasons"] = {probe.GENERIC + ": " + v: 1}
            r["rejectedCells"][0]["reason"] = v
        else:
            r[k] = v
    return r


CASES = [
    ("fixed tool on PackedDirt", FIXED, "ok"),
    ("pre-fix tool (generic reason, no rejectedCells)", PREFIX, "fail"),
    ("no result object", None, "fail"),
    ("planted 1", variant(planted=1, rejected=0), "fail"),
    ("rejectedCells empty", variant(rejectedCells=[]), "fail"),
    ("rejectedCells two rows", variant(rejectedCells=FIXED["rejectedCells"] * 2), "fail"),
    ("reason 'no reason given'", variant(reason="no reason given"), "fail"),
    ("reason empty", variant(reason=""), "fail"),
    ("reason not about fertility", variant(reason="Polluted terrain."), "fail"),
    ("row reason disagrees with rejectionReasons", variant(**{"row.reason": "Too cold."}), "fail"),
    ("terrain not PackedDirt", variant(**{"row.terrain": "Soil"}), "fail"),
    ("fertility not below fertilityMin", variant(**{"row.fertility": 0.05}), "fail"),
    ("fertilityMin not Plant_Grass's 0.05", variant(**{"row.fertilityMin": 0.1}), "fail"),
    ("fertility absent", variant(**{"row.fertility": None}), "fail"),
    ("blocked cell", variant(**{"row.blocker": "Rock"}), "blocker"),
]


def run(judge):
    fails = []
    for name, res, want in CASES:
        got = judge(res)[0]
        if got != want:
            fails.append("%s: judge said %s, want %s" % (name, got, want))
    return fails


def main():
    fails = run(probe.judge)
    for name, _, want in CASES:
        bad = [f for f in fails if f.startswith(name + ":")]
        print("%s  %s -> %s" % ("FAIL" if bad else "PASS", name, bad[0] if bad else want))
    # Sanity probe: this test must see a judge that accepts anything, and one that rejects everything.
    blind = run(lambda res: ("ok", "loose"))
    print("%s  sanity: an always-ok judge fails %d case(s)" % ("PASS" if len(blind) >= 10 else "FAIL", len(blind)))
    strict = run(lambda res: ("fail", "strict"))
    print("%s  sanity: an always-fail judge fails %d case(s)" % ("PASS" if len(strict) >= 2 else "FAIL", len(strict)))
    ok = not fails and len(blind) >= 10 and len(strict) >= 2
    print("RESULT: %s (%d cases)" % ("PASS" if ok else "FAIL", len(CASES)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
