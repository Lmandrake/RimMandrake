#!/usr/bin/env python3
"""Offline half of alpha_biomes_retired_live.py: the plan is full, every port draws a path our tree holds, and the log
reader goes red on a planted line and stays green on clean ones."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alpha_biomes_retired_live as A  # noqa: E402

FAILS = []


def check(c, what, d=""):
    print(("PASS " if c else "FAIL ") + what + ("" if c else "  -- %s" % (d,)))
    if not c:
        FAILS.append(what)


p, donors, ours = A.plan(), A.donor_names(), A.our_textures()
names = {n for _, n in p["defs"]}
check({"RM_JungleTree", "RM_ToxiGrass", "RM_GiantAgarilux", "RM_MangroveTree"} <= set(p["plants"]), "the plan holds the port plants")
check(not [n for n, t in p["plants"].items() if not t or t.lower() not in ours], "every port plant's picture is in our tree",
      [n for n, t in p["plants"].items() if not t or t.lower() not in ours])
check(not [(n, t) for n, t in p["plants"].items() if "standin/" in t.lower()], "no port plant draws a stand-in")
bad = [(n, v) for n, f in p["terrains"].items() for v in f.values()
       if v and v.startswith("Terrain/Surfaces/AB_") and v.lower() not in ours]
check(not bad, "every port terrain's AB_-named picture is in our tree", bad)
check("things/plants/ab_notours" not in ours, "control: a path nobody holds is not ours")
H = lambda *l: A.log_hits(list(l), donors, names)  # noqa: E731
check([h[1:3] for h in H("Could not resolve cross-reference to Verse.ThingDef named AB_GiantAgarilux (wanter=plant)")] == [("donor", "AB_GiantAgarilux")],
      "planted: an unresolved donor def is a hit")
check([h[1:3] for h in H("Could not load UnityEngine.Texture2D at Things/Plants/RM_JungleTree")] == [("ours", "RM_JungleTree")],
      "planted: a missing picture of a port is a hit")
check([h[1] for h in H("  - sarg.alphabiomes")] == ["donor"], "planted: the donor in the mod list echo is a hit")
check(not H("Loaded RM_JungleTree", "[RimBridge] get_def AB_JungleTree not found", "AB_MiningYield_VeryHigh error", ""),
      "must stay green: a plain mention, the bridge's own read, Alpha Memes' live AB_ def")
T = [{"defName": "RM_Tree", "badTex": True, "thingClass": "RimWorld.Plant"}, {"defName": "RM_Beast", "badTex": True, "thingClass": "Verse.Pawn"},
     {"defName": "RM_Ghost", "badTex": True, "thingClass": "X.Building_Blocker"}, {"defName": "Steel", "badTex": True}]
check(A.bad_drawn(T, lambda ns: {"RM_Ghost"}) == ["RM_Tree"], "planted: a plant of ours that draws BadTex is red")
check(A.bad_drawn(T[1:], lambda ns: {"RM_Ghost"}) == [], "must stay green: a pawn, a thing that draws nothing on purpose")
check(A.bad_drawn(T[2:], lambda ns: set()) == ["RM_Ghost"], "planted: an unread drawerType hides nothing")
print("RESULT: " + ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
