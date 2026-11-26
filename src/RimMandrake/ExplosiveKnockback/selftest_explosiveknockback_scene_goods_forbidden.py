#!/usr/bin/env python3
"""Offline check of the staging fix of RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS.
Fault (printed by the hunt's cause line, 2026-11-26, SteveDesktop lane, long batch 1): a stage-save colonist that is not
a scene pawn picked up a scene's good (`gone(destroyed=False stack=1 holder=Pawn_CarryTracker:<name> job=HaulToCell)`),
so goods_fly_wall read "comp not spawned" and goods_obstacles_control lane D read "not spawned". Fix: the proof staging
helper Item() forbids the good it places (a forbidden thing is never hauled by free will), and the two scenes whose claim
is a haul of that good keep it allowed (pawn_arc's stack, pit_goods_fetch's two stacks).
  F1 Item() takes `bool haulable = false` and sets the placed thing forbidden when it is false
  F2 the forbid is made after the placement and before Track()
  F3 pawn_arc's stack and both pit_goods_fetch stacks pass haulable: true
  F4 no other Item() call passes haulable: true

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_scene_goods_forbidden.py [--src DIR]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + " " + what)
    if not ok:
        fails.append(code + " " + what)


def main():
    root = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else HERE
    src = os.path.join(root, "Source")
    proof = open(os.path.join(src, "RM_KnockbackProof.cs"), encoding="utf-8").read()
    m = re.search(r"private static Thing Item\(([^)]*)\)\s*\{(.*?)\n        \}\n", proof, re.S)
    sig, body = (m.group(1), m.group(2)) if m else ("", "")
    check("F1", "bool haulable = false" in sig and re.search(r"SetForbidden\(\s*true", body) and "!haulable" in body,
          "Item() takes haulable (default false) and forbids the placed good when it is false")
    p, f, t = body.find("TryPlaceThing"), body.find("SetForbidden"), body.find("Track(")
    check("F2", 0 <= p < f < t, "the forbid comes after the placement and before Track()")
    calls = []
    for fn in sorted(os.listdir(src)):
        if fn.endswith(".cs"):
            text = open(os.path.join(src, fn), encoding="utf-8").read()
            for c in re.finditer(r"\bItem\(s, ([^;]*)\);", text):
                calls.append((fn, c.group(1)))
    want = {'"st", "Steel", 20, O(s, 1, 0)': "pawn_arc stack", '"st", "Steel", 20, O(s, 4, 5)': "pit_goods_fetch main stack",
            '"cst", "Steel", 20, O(s, -6, -6)': "pit_goods_fetch control stack"}
    got = {c for fn, c in calls if "haulable: true" in c}
    check("F3", all(any(k in g for g in got) for k in want), "haulable: true on " + ", ".join(want.values()))
    check("F4", len(got) == len(want), "only those %d Item() calls pass haulable: true (found %d)" % (len(want), len(got)))
    print("selftest_explosiveknockback_scene_goods_forbidden: %s" % ("FAIL %d" % len(fails) if fails else "PASS 4"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
