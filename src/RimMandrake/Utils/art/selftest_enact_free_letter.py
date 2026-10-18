#!/usr/bin/env python3
"""A ticked variant installed into a Graphic_Random folder takes its column letter only when that file name is free.

Bug 2026-10-18 (tree_art_picks_sheet): RM_Veluthar_a held _b/_c, RM_Zhorrel_a held _a/_c/_d, RM_Rockfinger held _b;
the new render's column letter (C, D, B) named an occupied file, and enact would have OVERWRITTEN a picture the owner
kept in the pool instead of adding beside it."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import enact as E


class Idx:
    def __init__(self, rels):
        self.live = {("src/RimMandrake/Greentide", r): {"sha": f"s{i}"} for i, r in enumerate(rels)}


g = "Things/Plant/RM_X/RM_X_a"
fails = 0
def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(("PASS " if ok else "FAIL ") + f"{name}: {got!r}" + ("" if ok else f" (want {want!r})"))

idx = Idx([f"{g}/RM_X_a_b.png", f"{g}/RM_X_a_c.png"])
check("free letter kept", E.own_slot(idx, None, g, "single", "D", "RM_X", set())["rel"], f"{g}/RM_X_a_d.png")
check("occupied letter moves to first free", E.own_slot(idx, None, g, "single", "C", "RM_X", set())["rel"], f"{g}/RM_X_a_a.png")
check("planned installs count as taken",
      E.own_slot(idx, None, g, "single", "C", "RM_X", set(), taken={f"{g}/RM_X_a_a.png"})["rel"], f"{g}/RM_X_a_d.png")
print("ALL PASS" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
