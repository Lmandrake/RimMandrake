#!/usr/bin/env python3
"""Offline selftest of objects_sheet.py and river_scenes_walk.py (both authored offline, never yet run live) and their shared
fw_walk_common.py. No game: each walk runs end to end on FakeGame in a temp folder (--mock). Proves the scripts' OWN paths
(staging, rotation read-back, labelling, index.html, the crash handler that keeps a traceback and goes on); proves nothing
about the game. Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_fw_walks.py"""
# selftest temp containment (BENCH, FLOWWORKS_SELFTESTS_FIX_TMPDIR_LEAKS): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_fw_walks_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
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

# ---- styles: the look is read back from the menu, its ": this tank" tail stripped (CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES)
check("look_of strips the tail and (current)", OS_.look_of("Futuristic: this tank (current)") == "Futuristic"
      and OS_.look_of("Scrapper") == "Scrapper" and OS_.look_of("Modern: whole connected run") == "Modern")
rc, out = quiet(OS_.main, ["--mock", "--prove"])
rows = rows_of(OS_.OUT_MOCK)
check("objects_sheet --mock --prove: every style row MATCHES its asked look", all(r["status"] == "MATCHES" for r in rows if r["id"].startswith("styles_")),
      [r for r in rows if r["id"].startswith("styles_") and r["status"] != "MATCHES"][:2])
check("objects_sheet --mock --prove: PROVEN, exit 0, prove.txt says so", rc == 0 and "PROVEN (38 rows" in out
      and open(os.path.join(OS_.OUT_MOCK, "prove.txt"), encoding="utf-8").read().startswith("PROVEN"), (rc, out[-300:]))
_pipe = [r for r in rows if r["id"] == "styles_RM_UniversalPipe.Scrapper"]
check("pipe look picked for the whole connected run", _pipe and "Scrapper" in _pipe[0]["game"], _pipe)
# a style menu that never says which look is current -> UNMEASURED -> NOT PROVEN
_ol = OS_.look_of
OS_.look_of = lambda label: None
rc, out = quiet(OS_.main, ["--mock", "--only", "styles", "--prove"])
OS_.look_of = _ol
check("objects_sheet --prove: unreadable look -> NOT PROVEN, exit 1", rc == 1 and "NOT PROVEN" in out, (rc, out[-300:]))
rc, out = quiet(OS_.main, ["--mock", "--only", "ladders", "--mock-fail", "ladders_raised", "--prove"])
check("objects_sheet --prove: a crashed group -> NOT PROVEN", rc == 1 and "NOT PROVEN" in out, (rc, out[-200:]))
rc, out = quiet(OS_.main, ["--mock", "--only", "ladders", "--no-shots", "--prove"])
check("objects_sheet --prove --no-shots refuses (the sheet is the pictures)", rc == 1 and "the sheet is the pictures" in out, (rc, out[-200:]))
_g = [dict(id=g, images=[("x.png", g)]) for g in OS_.EXPECT["ladders"]]
_r = [dict(id="%s.%s" % (g, n), status="MATCHES", game="") for g in OS_.EXPECT["ladders"] for n in C.ROT_NAMES]
check("prove_verdict: a full ladder family passes", OS_.prove_verdict(_r, _g, ["ladders"]) == [])
check("prove_verdict: one DIFFERS fails", OS_.prove_verdict(_r[:-1] + [dict(_r[-1], status="DIFFERS")], _g, ["ladders"]) != [])
check("prove_verdict: a missing picture fails", OS_.prove_verdict(_r, _g[:-1] + [dict(id=_g[-1]["id"], images=[])], ["ladders"]) != [])
check("prove_verdict: a short group (3 of 4 rows) fails", OS_.prove_verdict(_r[1:], _g, ["ladders"]) != [])
check("prove_verdict: a missing family fails (no vacuous pass)", OS_.prove_verdict([], [], ["river"]) != [])

# review findings (gpt, 2026-11-03): pipe run checked on every cell; unknown --only refused; a neighbour never stands in
_fe = C.FakeGame._style


def _no_run(self, tool, kw):     # a menu offering only ': this one' rows: the run cannot be styled
    r = _fe(self, tool, kw)
    if tool == "rimworld/get_context_menu_options":
        r["options"] = [o for o in r.get("options") or [] if not o.get("_run")]
        self.menu_opts = r["options"]
    return r


C.FakeGame._style = _no_run
rc, out = quiet(OS_.main, ["--mock", "--only", "styles", "--prove"])
C.FakeGame._style = _fe
rows = rows_of(OS_.OUT_MOCK)
check("pipe with no whole-run option -> its styled rows not MATCHES, NOT PROVEN",
      rc == 1 and all(r["status"] != "MATCHES" for r in rows if r["id"].startswith("styles_RM_UniversalPipe.") and not r["id"].endswith("default")),
      [r for r in rows if r["id"].startswith("styles_RM_UniversalPipe.")][:2])
rc, out = quiet(OS_.main, ["--mock", "--only", "styels", "--prove"])
check("--only with an unknown family refuses (exit 2)", rc == 2 and "--only takes" in out, (rc, out[-200:]))
check("prove_verdict: unknown family / empty selection fail", OS_.prove_verdict([], [], ["styels"]) != [] and OS_.prove_verdict([], [], []) != [])
_fw = C.make_walk(type("A", (), dict(mock=True, no_shots=True, pace=0.0, mock_fail=None, fresh_map=False))(), tempfile.mkdtemp())
C.place(_fw, "RM_UniversalPipe", (10, 10), rot=0)
_fb = _fw.B.call


def _refuse(tool, **kw):
    return {"success": False, "error": "refused"} if tool == "jawa/build_batch" else _fb(tool, **kw)


_fw.B.call = _refuse
_pr = C.place(_fw, "RM_UniversalPipe", (11, 10), rot=0)
check("place(): a failed build next to an earlier one is not survived", _pr["survived"] is False, _pr)
check("prove_verdict: a group owing 5 pictures with 4 fails",
      OS_.prove_verdict([dict(id="river_fords", status="MATCHES")] + [dict(id="river_weirs.%s" % l, status="MATCHES") for l in OS_.STYLE_LABEL],
                        [dict(id="river_fords", images=[1]), dict(id="river_weirs", images=[1, 2, 3, 4], shots_owed=5)], ["river"]) != [])

_fw2 = C.make_walk(type("A", (), dict(mock=True, no_shots=True, pace=0.0, mock_fail=None, fresh_map=False))(), tempfile.mkdtemp())
C.place(_fw2, "RM_UniversalPipe", (10, 10), rot=0)
_fb2 = _fw2.B.call
_fw2.B.call = lambda tool, **kw: ({"success": False} if tool in ("jawa/list_things", "jawa/build_batch") else _fb2(tool, **kw))
_pr = C.place(_fw2, "RM_UniversalPipe", (10, 10), rot=0)
check("place(): an unreadable pre-build list is not survived", _pr["survived"] is False and "unreadable" in _pr["note"], _pr)
# a default pipe whose third cell wears a named style -> the default row is not MATCHES
_cl = OS_.current_look
OS_.current_look = lambda w, cell: "Scrapper" if tuple(cell) == (152, 168) else _cl(w, cell)
rc, out = quiet(OS_.main, ["--mock", "--only", "styles", "--prove"])
OS_.current_look = _cl
rows = rows_of(OS_.OUT_MOCK)
_d = [r for r in rows if r["id"] == "styles_RM_UniversalPipe.default"]
check("default pipe: a styled non-first cell -> DIFFERS, NOT PROVEN", rc == 1 and _d and _d[0]["status"] == "DIFFERS", _d)

# a lowered ladder that reads raised=True is not "slid down"
_st = C.FakeGame._static
C.FakeGame._static = lambda self, typ, m, arg: ({"success": True, "result": "LADDER cell=%s present=True raised=True inspect=x" % arg}
                                                if m == "ProofLadder" else _st(self, typ, m, arg))
rc, out = quiet(OS_.main, ["--mock", "--only", "ladders", "--prove"])
C.FakeGame._static = _st
rows = rows_of(OS_.OUT_MOCK)
check("ladders_lowered reading raised=True -> DIFFERS, NOT PROVEN", rc == 1 and all(r["status"] == "DIFFERS" for r in rows if r["id"].startswith("ladders_lowered.")),
      [r for r in rows if r["id"].startswith("ladders_lowered.")][:1])

_orig = C.thing_rot
C.thing_rot = lambda t: None
rc, out = quiet(OS_.main, ["--mock", "--only", "styles", "--prove"])
C.thing_rot = _orig
rows = rows_of(OS_.OUT_MOCK)
check("styles: unreadable rotation -> UNMEASURED on every style row, NOT PROVEN", rc == 1 and all(r["status"] == "UNMEASURED" for r in rows if r["id"].startswith("styles_")), rows[:1])

# a style pick that turns the thing: the verdict uses the rotation read AFTER the pick
def _turns(self, tool, kw):
    t = getattr(self, "menu", None)
    r = _fe(self, tool, kw)
    if tool == "rimworld/execute_context_menu_option" and t:
        t["rotation"] = "East"
    return r


C.FakeGame._style = _turns
rc, out = quiet(OS_.main, ["--mock", "--only", "styles", "--prove"])
C.FakeGame._style = _fe
rows = rows_of(OS_.OUT_MOCK)
check("a style pick that turns the tank -> DIFFERS (rotation re-read after the pick)", rc == 1 and any(
    r["id"] == "styles_RM_LiquidTank.Futuristic" and r["status"] == "DIFFERS" for r in rows), [r for r in rows if r["id"].startswith("styles_RM_LiquidTank.")][:2])

# blind check 2026-11-03 (gen 3): the river group's own verdicts. Ford stones that do not land, or cannot be read back,
# and a weir whose style pick does not take (or cannot be read), must each go red, never MATCHES.
_fc = C.FakeGame.call


def _ford_ignored(self, tool, **kw):       # set_terrain_batch "succeeds" but lays nothing
    if tool == "jawa/set_terrain_batch" and OS_.FORD in str(kw.get("ops")):
        return {"success": True}
    return _fc(self, tool, **kw)


def _ford_unreadable(self, tool, **kw):    # after the stones are laid, the terrain read is refused
    if tool == "jawa/set_terrain_batch" and OS_.FORD in str(kw.get("ops")):
        self._ford_laid = True
    if tool == "jawa/get_terrain_batch" and getattr(self, "_ford_laid", False):
        return {"success": False, "error": "refused"}
    return _fc(self, tool, **kw)


for _fn, _want, _nm in ((_ford_ignored, "DIFFERS", "ford stones not laid -> DIFFERS"), (_ford_unreadable, "UNMEASURED", "ford stones unreadable -> UNMEASURED")):
    C.FakeGame.call = _fn
    rc, out = quiet(OS_.main, ["--mock", "--only", "river", "--prove"])
    C.FakeGame.call = _fc
    rows = rows_of(OS_.OUT_MOCK)
    _f = [r for r in rows if r["id"] == "river_fords"]
    check(_nm + ", NOT PROVEN", rc == 1 and "NOT PROVEN" in out and _f and _f[0]["status"] == _want, (rc, _f))
rc, out = quiet(OS_.main, ["--mock", "--only", "river", "--prove"])
check("river family clean -> PROVEN (the probes above are not red by accident)", rc == 0, (rc, out[-300:]))


def _weir_sticks(self, tool, kw):          # the weir's style pick is accepted but the look does not change
    t = getattr(self, "menu", None)
    if tool == "rimworld/execute_context_menu_option" and t and t["defName"] == OS_.WEIR:
        self.menu = None
        return {"success": True}
    return _fe(self, tool, kw)


C.FakeGame._style = _weir_sticks
rc, out = quiet(OS_.main, ["--mock", "--only", "river", "--prove"])
C.FakeGame._style = _fe
rows = rows_of(OS_.OUT_MOCK)
_w = {r["id"]: r["status"] for r in rows if r["id"].startswith("river_weirs.")}
check("weir style pick that does not take -> styled weirs DIFFERS, NOT PROVEN",
      rc == 1 and len(_w) == len(OS_.STYLE_LABEL) and all(v == "DIFFERS" for k, v in _w.items() if not k.endswith("." + OS_.STYLE_LABEL[0])), (rc, _w))
_cl = OS_.current_look
OS_.current_look = lambda w, cell: OS_.STYLE_LABEL[-1]   # every weir reads Scrapper: the default one is wrong too
rc, out = quiet(OS_.main, ["--mock", "--only", "river", "--prove"])
OS_.current_look = _cl
rows = rows_of(OS_.OUT_MOCK)
_w = {r["id"]: r["status"] for r in rows if r["id"].startswith("river_weirs.")}
check("default weir wearing a named look -> DIFFERS, NOT PROVEN", rc == 1 and _w.get("river_weirs." + OS_.STYLE_LABEL[0]) == "DIFFERS", (rc, _w))
OS_.look_of = lambda label: None
rc, out = quiet(OS_.main, ["--mock", "--only", "river", "--prove"])
OS_.look_of = _ol
rows = rows_of(OS_.OUT_MOCK)
_w = {r["id"]: r["status"] for r in rows if r["id"].startswith("river_weirs.")}
check("weir look unreadable -> every weir UNMEASURED, NOT PROVEN", rc == 1 and len(_w) == len(OS_.STYLE_LABEL) and all(v == "UNMEASURED" for v in _w.values()), (rc, _w))

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
