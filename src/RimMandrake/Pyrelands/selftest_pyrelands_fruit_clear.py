#!/usr/bin/env python3
"""Offline selftest for validation._clear_scorchfruit (PYRE_FIREBORN_DIAGNOSE_TWENTYONE_RETURN, L1 2026-10-15).

In the full 16-chain A run, 21 ScorchFruit stood on the map after the cap-budget clear and scorchfruit_fire_born's burned
cohort grew none; alone after a reload it passed. The clear destroyed plants only in a 40x40 box around each fire pad, so
fruit a stray (non-pad) fire had seeded elsewhere survived it, and that fire kept burning. A fake map holds pad fruit,
off-pad fruit and a stray fire; the clear must leave 0 fruit and no fire. Run: python3 <this file>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import validation as V  # noqa: E402

FRUIT = "RM_FE_Plant_ScorchFruit"


def _in(r, x, z):
    rx, rz, w, h = (int(v) for v in r.split(","))
    return rx <= x < rx + w and rz <= z < rz + h


class FakeT(object):
    def __init__(self, fruit, fires):
        self.session, self.upstream_failed = object(), False
        self.fruit, self.fires, self.notes = list(fruit), set(fires), []

    def _record(self, label, data):
        self.notes.append((label, data))

    def bridge_call(self, tool, **p):
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 250, "sizeZ": 250}
        if tool == "jawa/map_fire" and p.get("action") == "extinguish":
            self.fires = set(c for c in self.fires if not _in(p["rect"], *c))
            return {"success": True}
        if tool == "jawa/destroy_batch":
            if "Plant" in p.get("categories", "Plant") or "All" in p.get("categories", ""):
                for r in p["rects"].split(";"):
                    self.fruit = [c for c in self.fruit if not _in(r if r.count(",") == 3 else r + ",1,1", *c)]
            return {"success": True}
        if tool == "jawa/list_things" and p.get("defName") == FRUIT:
            hit = [c for c in self.fruit if "rect" not in p or _in(p["rect"], *c)]
            rows = [{"id": "F%d" % i, "def": FRUIT, "x": x, "z": z} for i, (x, z) in enumerate(hit)][:p.get("limit", 500)]
            return {"success": True, "things": rows, "countMatched": len(hit), "scanned": 60000}
        return {"success": True}


def off_pad_cells(n):
    out = []
    for x in range(250):
        for z in range(0, 250, 7):
            if not any(abs(x - px) <= 21 and abs(z - pz) <= 21 for px, pz in V.FIRE_PADS):
                out.append((x, z))
                if len(out) == n:
                    return out
    return out


def main():
    probs = []
    stray = off_pad_cells(21)
    if len(stray) != 21:
        probs.append("fixture: only %d off-pad cells on a 250x250 map" % len(stray))
    px, pz = V.PAD_FIRE_TICK
    t = FakeT([(px + 1, pz + 1), (px - 5, pz + 3)] + stray, fires=[stray[0], (px, pz)])
    V._clear_scorchfruit(t)
    left = dict(t.notes).get("ScorchFruit left on the map after the cap-budget clear")
    if left != 0 or t.fruit:
        probs.append("the cap-budget clear left %r ScorchFruit (%d off the pads) -- the L1 'left 21'" % (left, len(t.fruit)))
    if t.fires:
        probs.append("the cap-budget clear left a fire burning at %s: it keeps seeding fruit into the shared cap" % sorted(t.fires))
    # can-fail: the instrument sees off-pad fruit a pad-box-only clear would leave
    t2 = FakeT(stray, fires=[])
    for (qx, qz) in V.FIRE_PADS:
        t2.bridge_call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (qx - 20, qz - 20, 40, 40), categories="Plant")
    if len(t2.fruit) != 21:
        probs.append("can-fail: a pad-box-only clear should leave the 21 off-pad fruit, left %d" % len(t2.fruit))
    print("selftest_pyrelands_fruit_clear: %s" % ("FAIL" if probs else "PASS"))
    for p in probs:
        print("  - " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
