#!/usr/bin/env python3
"""Offline selftest of owner_review_stage.py: every failure a staging call can have must land in Stage.notes (never a silent
success), and each bars row frames its OWN rect. No game: FakeGame. Run: python3 <this file>"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402
import owner_review_stage as ORS  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


class A(object):
    mock = True
    no_shots = True
    mock_fail = None


class Bad(C.FakeGame):
    """Refuses excavation, build and proofs, answers nothing for spawn_batch."""
    def call(self, tool, **kw):
        if tool in ("jawa/flowworks_excavation_drive",):
            return {"success": False, "message": "refused"}
        if tool == "jawa/build_batch":
            return {"success": False, "failed": "nope"}
        if tool == "jawa/spawn_batch":
            return None
        if tool == "jawa/static_call":
            return {"success": True, "result": "REFUSED: no"}
        return C.FakeGame.call(self, tool, **kw)


def stage(game_cls):
    import tempfile
    w = C.make_walk(A(), tempfile.mkdtemp())
    w.B = game_cls()
    return ORS.Stage(w, False)


s = stage(Bad)
s.dig((100, 100), 2)
s.fill((100, 100), 1)
s.place("RM_Ladder", (101, 101), rot=0)
s.item("RM_ClimbingGear", (102, 102))
ok, _ = s.proof(ORS.SUSP, "ProofBuild", "1,1;5,1;rope;god")
s.store((103, 103))
n = " | ".join(s.notes)
check("refused dig is noted", "dig (100, 100)" in n, n)
check("refused fill is noted", "fill (100, 100)" in n, n)
check("a thing not on the map is noted", "place RM_Ladder" in n and "NOT on the map" in n, n)
check("empty spawn_batch reply is noted", "item RM_ClimbingGear" in n, n)
check("a REFUSED proof is noted and returns not-ok", (not ok) and "ProofBuild" in n, n)
check("a refused tank fill is noted", "tank at (103, 103) NOT filled" in n, n)
g = stage(C.FakeGame)
g.dig((100, 100), 2)
g.fill((100, 100), 1)
check("honest fake: no false notes from dig/fill", not g.notes, g.notes)
L = ORS.layout(100, 100)
rects = [ORS.bars_row_rect(L, r) for r in ORS.BARS_ROWS]
check("each bars row has its own rect", len(set(rects)) == len(ORS.BARS_ROWS), rects)
bx, bz, bw, bh = L["bars_rect"]
check("every bars row rect sits inside the bars site", all(bx <= r[0] and r[0] + r[2] <= bx + bw and bz <= r[1] and r[1] + r[3] <= bz + bh for r in rects), rects)
# WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT: the swatch verdict and the whole-row framing
check("good temperate water (83,93,97) reads as water", ORS.water_verdict([83, 93, 97]) is True)
check("can-fail: the grey Rot pit water (67,61,47) does not", ORS.water_verdict([67, 61, 47]) is False)
check("an unread picture is no verdict", ORS.water_verdict(None) is None and ORS.water_verdict([1, None, 3]) is None)
sw = ORS.swatch_rect(100, 100)
rx, rz, rw, rh = L["rect"]
check("the swatch sits inside the cleared site, clear of the ladders row (z >= 100)",
      rx <= sw[0] and sw[0] + sw[2] <= rx + rw and rz <= sw[1] and sw[1] + sw[3] <= 100, (sw, L["rect"]))
import water_scenes_walk as WSW  # noqa: E402
fr = WSW.fit_root_size((97, 131, 66, 12))
check("a 66-wide row is framed whole (16:9 view %.0f cells wide >= 70)" % (2 * fr * WSW.SCREEN_ASPECT), 2 * fr * WSW.SCREEN_ASPECT >= 70, fr)
check("a small rect never zooms below the engine floor 11 (the old rootSize 8 sat under it)", WSW.fit_root_size((0, 0, 3, 3)) == WSW.ROOT_FLOOR)
check("the 64x70 overview fits top to bottom", 2 * WSW.fit_root_size(L["rect"]) >= 74)
print("selftest_owner_review_stage: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
