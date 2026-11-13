#!/usr/bin/env python3
"""Offline test of geyser_pit_scene.py's pure half (RIMMANDRAKE_FIX_GEYSER_PIT_G2_SCENE_NEEDS_A_LADDER): no bridge, no game.
Run first against the AFK 2026-11-12 night's staging (pits dug with no ladder: the owner could not get a colonist into G2),
which it must flag; then against the shipped plan, which must be enterable; then planted faults and the reach judge."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geyser_pit_scene as S  # noqa: E402

fails = []


def check(ok, why):
    if not ok:
        fails.append(why)


rows = S.plan()
# the night's staging: the same pits, no ladder
night = [dict(r, ladder=None) for r in rows]
p = S.staging_problems(night)
check(len(p) == len(rows) and any(x.startswith("G2_water1m: no ladder") for x in p),
      "the 2026-11-13 staging (no ladders) is flagged on every pit, G2 included (got %d of %d)" % (len(p), len(rows)))
check(S.staging_problems(rows) == [], "the shipped plan is enterable: %s" % S.staging_problems(rows))
check(len(rows) == 11 and len({r["name"] for r in rows}) == 11, "eleven named pits")
for r in rows:
    x0, z0, w, h = r["rect"]
    gx, gz = r["geyser"]
    check(x0 < gx and gx + 1 < x0 + w - 1 and z0 < gz and gz + 1 < z0 + h - 1, "%s: the vent sits inside its pit with floor round it" % r["name"])
# planted faults: each must be flagged
g2 = next(r for r in rows if r["name"] == "G2_water1m")
gx, gz = g2["geyser"]
x0, z0, w, h = g2["rect"]
for why, bad in (("ladder on the south row", dict(g2, ladder=(x0, z0, S.NORTH))),
                 ("ladder outside the pit", dict(g2, ladder=(x0 - 1, z0 + h - 1, S.NORTH))),
                 ("ladder facing south", dict(g2, ladder=(x0, z0 + h - 1, 2))),
                 ("ladder on the vent", dict(g2, ladder=(gx, z0 + h - 1, S.NORTH), geyser=(gx, z0 + h - 2))),
                 ("target on the vent", dict(g2, target=(gx, gz))),
                 ("target off the pit", dict(g2, target=(x0 - 1, gz)))):
    check(S.staging_problems([bad]) != [], "planted fault not flagged: %s" % why)
# the reach judge
good = {"ladder": "LADDER cell=62,101 present=True raised=False want=False", "reach": "REACH veto=False reach=True reachPawnless=True found=True cells=9"}
check(S.judge_reach({"G2": good}) == [], "a lowered ladder and a found route pass")
check(S.judge_reach({"G2": dict(good, ladder="LADDER cell=62,101 present=True raised=True")}) != [], "a raised ladder fails")
check(S.judge_reach({"G2": dict(good, ladder="LADDER cell=62,101 present=False raised=None")}) != [], "a missing ladder fails")
check(S.judge_reach({"G2": dict(good, reach="REACH veto=True reach=False found=False cells=0")}) != [], "no route fails")

for f in fails:
    print("FAIL", f)
print("PASS selftest_geyser_pit_scene" if not fails else "FAILED %d" % len(fails))
sys.exit(1 if fails else 0)
