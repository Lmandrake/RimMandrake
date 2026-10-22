"""Offline checks for deep_lake_proof.py's pure verdicts (POND_ELEVATION_BUILD_LAKES_RUN_DEEP). No bridge."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deep_lake_proof as D  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


BODY = "BODY id=3 cells=5184 limitless=False truncated=False capacity=60000.0 levelUnit=1.000 bedSum=60000 deepest=20"
kv = D.parse(BODY)
check("a 72x72 limited lake past the old cap: PASS", D.body_verdict(kv, 72)[0] == "PASS")
check("can-fail: limitless is FAIL", D.body_verdict(D.parse(BODY.replace("limitless=False", "limitless=True")), 72)[0] == "FAIL")
check("can-fail: a truncated 4000-square body is FAIL",
      D.body_verdict(D.parse(BODY.replace("cells=5184", "cells=4000").replace("truncated=False", "truncated=True")), 72)[0] == "FAIL")
check("can-fail: beds never past 4 is FAIL", D.body_verdict(D.parse(BODY.replace("deepest=20", "deepest=0")), 72)[0] == "FAIL")
check("REFUSED is UNMEASURED", D.body_verdict(D.parse("REFUSED: no natural body at 1,1"), 72)[0] == "UNMEASURED")

SHAPE = ("SHAPE wet=900 dry=4284 receded=4284 deepestDry=19 maxDryBed=19 minWetBed=20 stepDeep=1 stepAll=2 lakebedShallow=276 "
         "lakebedDeep=900 lakebedAbyss=2000 deepestCell=96,96 shelfCell=66,70 hollows=True stock=15000.0 capacity=60000.0 hash=123")
s = D.parse(SHAPE)
check("a gradual drained bowl: PASS", D.hollow_verdict(s)[0] == "PASS")
# LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (owner R11): chasm-like floors are allowed, so sheer steps are recorded, not judged
check("a sheer step inside the deep bed is no longer a FAIL (R11)", D.hollow_verdict(D.parse(SHAPE.replace("stepDeep=1", "stepDeep=3")))[0] == "PASS")
check("can-fail: no dry squares is FAIL", D.hollow_verdict(D.parse(SHAPE.replace("dry=", "dry=0 x=")))[0] != "PASS")
check("can-fail: no bowl past 4 is FAIL", D.hollow_verdict(D.parse(SHAPE.replace("deepestDry=19", "deepestDry=4")))[0] == "FAIL")
check("hollows off is UNMEASURED", D.hollow_verdict(D.parse(SHAPE.replace("hollows=True", "hollows=False")))[0] == "UNMEASURED")
check("shallow dries first: PASS", D.drawdown_verdict(s)[0] == "PASS")
check("can-fail: a deep square dry above a shallower wet one is FAIL",
      D.drawdown_verdict(D.parse(SHAPE.replace("maxDryBed=19", "maxDryBed=20").replace("minWetBed=20", "minWetBed=12")))[0] == "FAIL")
check("fully dry is UNMEASURED for the order row", D.drawdown_verdict(D.parse(SHAPE.replace("wet=900", "wet=0")))[0] == "UNMEASURED")
check("shelf cell parses", D.cell_of(s, "shelfCell") == (66, 70) and D.cell_of({}, "shelfCell") is None)

FULL = "SHAPE wet=5184 dry=0 receded=0 hash=777 hollows=True"
check("refill to the same hash: PASS", D.refill_verdict(D.parse(FULL), D.parse(FULL))[0] == "PASS")
check("can-fail: a different hash is FAIL", D.refill_verdict(D.parse(FULL), D.parse(FULL.replace("hash=777", "hash=778")))[0] == "FAIL")
check("can-fail: a square still on the stack is FAIL",
      D.refill_verdict(D.parse(FULL), D.parse(FULL.replace("receded=0", "receded=1").replace("dry=0", "dry=1")))[0] == "FAIL")
check("a missing read is UNMEASURED", D.refill_verdict({}, D.parse(FULL))[0] == "UNMEASURED")

CL = "CLIMB k=2 held=False trapped=False cell=66,70 | POCKET k=2 comp=0 pocket=False size=900 depth=5 gen=8 built=8 rebuilds=2"
check("free in the bowl: PASS", D.free_verdict(D.parse(CL))[0] == "PASS")
check("can-fail: a pocket is FAIL", D.free_verdict(D.parse(CL.replace("pocket=False", "pocket=True")))[0] == "FAIL")
check("a stale grid is UNMEASURED", D.free_verdict(D.parse(CL.replace("built=8", "built=7")))[0] == "UNMEASURED")

R = (60, 60, 72, 72)
check("walked out: PASS", D.walk_verdict({"orderAccepted": True, "ticksElapsed": 3000, "position": {"x": 58, "z": 70}}, R)[0] == "PASS")
check("can-fail: still in the lake is FAIL", D.walk_verdict({"orderAccepted": True, "ticksElapsed": 3000, "position": {"x": 61, "z": 70}}, R)[0] == "FAIL")
check("no ticks is UNMEASURED", D.walk_verdict({"orderAccepted": True, "ticksElapsed": 0, "position": {"x": 58, "z": 70}}, R)[0] == "UNMEASURED")
check("the save/reload row is owed, not claimed", "DL_save_reload_bowl_identical" in D.OWED)

# DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE (HARNESS): the C# shape read picks shelfCell from any dry square past the deep notch
# (the shallowest such band, then westmost), not depth == 5 exactly, which a rough LAKE_FLOORS floor can skip entirely.
_cs = open(os.path.join(HERE, "..", "Source", "RM_NorthstarProofs.cs"), encoding="utf-8").read()
check("shelfCell: any dry square past the notch, not depth == 5 exactly",
      "d > RM_Volume.LevelsPerSquare && (!shelfCell.IsValid || d < shelfDepth" in _cs
      and "d == RM_Volume.LevelsPerSquare + 1 && (!shelfCell.IsValid" not in _cs)

# DRAWDOWN refill follow-up (HARNESS, fixer G): the colonist rows tick the game between drain and refill; with the pond depth
# model on, live pulses StagePond the body (part-depth stage water off the receded stack) and the LIFO refill cannot undo it.
# The proof must hold pondDepthEnabled off for its run AND restore it (it is in FIELDS, the restore list).
_py = open(os.path.join(HERE, "deep_lake_proof.py"), encoding="utf-8").read()
check("the proof holds the pond depth model off while it ticks (live pulses run the model the proof drives)",
      '("pondDepthEnabled", False)' in _py)
check("and restores it after (pondDepthEnabled is in FIELDS)", '"refillWaitsForOccupants", "pondDepthEnabled")' in _py)

print("%d failed" % len(fails))
sys.exit(1 if fails else 0)
