#!/usr/bin/env python3
"""Offline selftest of objects_sheet.py and river_scenes_walk.py (both authored offline, never yet run live) and their shared
fw_walk_common.py. No game: each walk runs end to end on FakeGame in a temp folder (--mock). Proves the scripts' OWN paths
(staging, rotation read-back, labelling, index.html, the crash handler that keeps a traceback and goes on); proves nothing
about the game. Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_fw_walks.py"""
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402
import objects_sheet as OS_  # noqa: E402
import river_scenes_walk as RS  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def quiet(fn, *a, **k):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rv = fn(*a, **k)
    return rv, buf.getvalue()


# ---- pure helpers
check("norm_rot reads names, ints, letters, junk", [C.norm_rot(v) for v in ("North", 1, "S", "Rot4:West", "x", None)] == [0, 1, 2, 3, None, None])
check("wall_cell: middle of each side", [OS_.wall_cell((10, 20), r) for r in range(4)] == [(11, 22), (12, 21), (11, 20), (10, 21)])
terr = {(x, z): ("WaterMovingShallow" if z in (50, 51) else "Soil") for x in range(100) for z in range(100)}
bc = C.bank_cells(terr, (100, 100), margin=12)
check("bank_cells: moving cells with dry on a side, rot points at the dry side", bc and all(terr[c] == "WaterMovingShallow" for c, _ in bc)
      and {r for c, r in bc if c[1] == 51} == {0} and {r for c, r in bc if c[1] == 50} == {2}, bc[:3])
check("spread keeps candidates apart", all(max(abs(a[0][0] - b[0][0]), abs(a[0][1] - b[0][1])) >= 7
                                           for i, a in enumerate(C.spread(bc, 5)) for b in C.spread(bc, 5)[i + 1:]))
check("ford_line: 4 straight shallow cells", len(OS_.ford_line(terr, (100, 100))) == 4)
check("ford_line: none when the river is one cell wide in a bend-free map of Soil", OS_.ford_line({(1, 1): "Soil"}, (100, 100)) == [])
check("shallow_pair: a 2-cell run with a rotation", RS.shallow_pair(terr, (100, 100)) is not None)
check("nearest_moving honours away_from", RS.nearest_moving(terr, (100, 100), away_from=[(50, 50)], min_d=4) != (50, 50))
check("displacement None-safe", RS.displacement(None, (1, 1)) is None and RS.displacement((0, 0), (2, 3)) == 5)

tmp = tempfile.mkdtemp(prefix="fwwalks_")
OS_.OUT_MOCK = os.path.join(tmp, "objects")
RS.OUT_MOCK = os.path.join(tmp, "rivers")


def rows_of(d):
    return json.load(open(os.path.join(d, "rows.json"), encoding="utf-8"))


# ---- objects_sheet, clean
rc, out = quiet(OS_.main, ["--mock"])
rows = rows_of(OS_.OUT_MOCK)
check("objects_sheet --mock exits 0", rc == 0, rc)
ids = [r["id"] for r in rows]
check("objects_sheet: 12 ladder rows, 20 style rows, 5 weirs, ford", sum(i.startswith("ladders_") for i in ids) == 12
      and sum(i.startswith("styles_") for i in ids) == 20 and sum(i.startswith("river_weirs.") for i in ids) == 5 and "river_fords" in ids, len(ids))
check("objects_sheet: every ladder row read its rotation back and MATCHES", all(r["status"] == "MATCHES" for r in rows if r["id"].startswith("ladders_")),
      [r for r in rows if r["id"].startswith("ladders_") and r["status"] != "MATCHES"][:2])
check("objects_sheet: autoturn rows show asked != read in their text", all("asked" in r["game"] for r in rows if r["id"].startswith("ladders_autoturn")))
check("objects_sheet: labelled pictures + index.html written", len(glob.glob(os.path.join(OS_.OUT_MOCK, "*_labelled.png"))) >= 9
      and "looks right" in open(os.path.join(OS_.OUT_MOCK, "index.html"), encoding="utf-8").read())
# ---- objects_sheet, a crash in one group goes on
rc, out = quiet(OS_.main, ["--mock", "--only", "ladders", "--mock-fail", "ladders_raised"])
rows = rows_of(OS_.OUT_MOCK)
check("objects_sheet crash: CRASHED row + traceback file + next group still ran, exit 1",
      rc == 1 and any(r["status"] == "CRASHED" for r in rows) and glob.glob(os.path.join(OS_.OUT_MOCK, "ladders_raised_traceback_*.txt"))
      and any(r["id"].startswith("ladders_autoturn") for r in rows) and "CRASHED (traceback kept" in out, (rc, out[-300:]))
# ---- a rotation the game does not report is UNMEASURED, never assumed
_orig = C.thing_rot
C.thing_rot = lambda t: None
rc, out = quiet(OS_.main, ["--mock", "--only", "ladders"])
C.thing_rot = _orig
rows = rows_of(OS_.OUT_MOCK)
check("objects_sheet: unreadable rotation -> UNMEASURED on every ladder row", all(r["status"] == "UNMEASURED" for r in rows if r["id"].startswith("ladders_")), rows[:2])

# ---- river_scenes_walk, clean
rc, out = quiet(RS.main, ["all", "--mock"])
check("river_scenes_walk all --mock exits 0", rc == 0, (rc, out[-300:]))
allrows = []
for f in glob.glob(os.path.join(RS.OUT_MOCK, "R*_rows.json")):
    allrows += json.load(open(f, encoding="utf-8"))
check("river scenes: all five scenes wrote rows", {r["scene"] for r in allrows if "scene" in r} == set(RS.ORDER))
check("river scenes: caption panels and index.html written", len(glob.glob(os.path.join(RS.OUT_MOCK, "R*_panel.png"))) >= 10
      and os.path.exists(os.path.join(RS.OUT_MOCK, "index.html")))
check("river scenes: only the words MATCHES/DIFFERS/UNMEASURED/CRASHED", {r["status"] for r in allrows} <= {"MATCHES", "DIFFERS", "UNMEASURED", "CRASHED"})
check("river scenes: R3.d letters row is UNMEASURED with its reason", any(r["id"] == "R3.d" and r["status"] == "UNMEASURED" for r in allrows))
# ---- crash goes on
rc, out = quiet(RS.main, ["all", "--mock", "--mock-fail", "R2"])
tb = glob.glob(os.path.join(RS.OUT_MOCK, "R2_traceback_*.txt"))
check("river crash: R2 traceback kept, R3..R5 still ran, exit 1", rc == 1 and tb and "R5.c" in out and "R3.a" in out, (rc, out[-200:]))
# ---- no river: refuses with a reason, never a crash
_fg = C.FakeGame


class Dry(_fg):
    def __init__(self):
        _fg.__init__(self)
        self.terrain = {}


C.FakeGame = Dry
rc, out = quiet(RS.main, ["all", "--mock"])
C.FakeGame = _fg
check("river walk on a map with no river: exit 2 and says why", rc == 2 and "NOT A RIVER SITE" in out, (rc, out[-200:]))
print("selftest_fw_walks: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
