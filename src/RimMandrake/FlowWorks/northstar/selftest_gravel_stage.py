"""Offline: gravel_stage stages fill material for validation_v2's fill-in scenes (V2_FILLIN_SCENE_STAGE_FILL_MATERIAL)."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gravel_stage as G  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s %s %s" % ("PASS" if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


calls = []


def fake(tool, **kw):
    calls.append((tool, kw))
    return {"success": True}


ok, why = G.spawn_fill_material(fake, [(1, 2), (3, 4)])
check("two spots, two spawn_thing calls", ok and len(calls) == 2 and all(c[0] == "rimworld/spawn_thing" for c in calls), calls)
check("RM_Gravel, enough for a notch", all(c[1]["defName"] == "RM_Gravel" and c[1]["stackCount"] >= 1 for c in calls))
ok, why = G.spawn_fill_material(lambda t, **k: {"success": False, "error": "no such def"}, [(1, 2)])
check("a refused spawn is not ok", not ok and "refused" in why, why)

src = open(os.path.join(HERE, "validation_v2.py"), encoding="utf-8").read()
i = src.index("g = L.probe(c, kind=kind")
j = src.index("spawn_fill_material", 0)  if "spawn_fill_material" in src else -1
check("validation_v2 stages fill material before the selection probe", 0 < j < i, (j, i))
print("SELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
sys.exit(1 if FAILS else 0)
