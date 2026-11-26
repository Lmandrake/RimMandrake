#!/usr/bin/env python3
"""Offline selftest of walk_map.py and the walk check of review_map_coverage.py: the plan keeps every rule, and each guard
goes red on a planted break. No game. Run: python3 <this file>"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.dirname(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)
import walk_map as W  # noqa: E402
import walk_principles as WP  # noqa: E402
import review_map_coverage as COV  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


d = W.plan()
check("the plan keeps every rule of the map", not W.problems(d), W.problems(d)[:5])
check("stations numbered 1..N", [st["n"] for st in d.stations] == list(range(1, len(d.stations) + 1)))
check("every station names a principle and an area", all(st["shows"] in WP.by_id() and st["group"] for st in d.stations))
lines, probs = COV.walk_coverage()
check("walk coverage: every principle has a station, every station a principle, every bar placed", not probs, probs[:5])

# the big pit: one call per run digs exactly its squares; the halves match; the shapes he asked for are there
cells = W.big_cells((14, 18))
cov = {}
for x, z, w, lv in W.runs(cells):
    for i in range(w):
        cov[(x + i, z)] = lv / 2.0
check("the basin runs dig every pit square to its depth and no ground square", cov == {k: v for k, v in cells.items() if v > 0})
h = W.big_half()
check("the big pit is at least 30 x 30", 2 * W.BIG_W + 1 >= 30 and W.BIG_H >= 30)
check("the big pit has floors at 0.5 to 8 m and ground left standing in it",
      {0, 0.5, 1, 2, 3, 4, 6, 8} <= set(h.values()), sorted(set(h.values())))
check("the east half holds water over some floors and leaves others dry",
      any(m > W.BIG_WATER_M for m in h.values()) and any(0 < m < W.BIG_WATER_M for m in h.values()))

# can-fail: each guard reads red on a planted break
bad = copy.deepcopy(d.stations)
bad[5]["text"] = "spawn RM_Spikes here"
check("can-fail: a code name on a sign is caught", any("code name" in p for p in W.sign_problems(bad)))
bad = copy.deepcopy(d.stations)
bad[3]["shows"] = None
check("can-fail: a station with no principle is caught", any("no listed principle" in p for p in W.sign_problems(bad)))
bad = copy.deepcopy(d.stations)
bad[0]["do"] = ""
check("can-fail: a sign with no DO line is caught", any("no LOOK or no DO" in p for p in W.sign_problems(bad)))
bad = copy.deepcopy(d.stations)
fire = [st for st in bad if st["shows"] == "tar_fire"][0]
bad[0]["rect"] = (fire["rect"][0] - 5, fire["rect"][1], 3, 3)
check("can-fail: a station within 15 squares of the tar is caught", W.fire_problems(bad), W.fire_problems(bad))
bad = copy.deepcopy(d.stations)
br = [st for st in bad if st["row"] == "kinds"]
for st in br:
    st["rect"] = (st["rect"][0], st["rect"][1] - 2, st["rect"][2], st["rect"][3])
check("can-fail: a row whose clear would wipe its neighbour is caught (the old z 150 kinds row)", W.clear_problems(bad))
big = [st for st in d.stations if st["shows"] == "complex_pit"][0]
tiles = W.shot_tiles(big["rect"])
check("can-fail: one capture of the big pit shows a cell under 40 px (the screen is 1351 px tall)",
      W.px_per_cell((big["rect"][0], big["rect"][1], big["rect"][2], big["rect"][3] + 1)) < W.MIN_PX)
check("so the big pit is captured in tiles, each at >= 40 px a cell, covering it whole",
      len(tiles) > 1 and all(W.px_per_cell(r) >= W.MIN_PX for r in tiles)
      and sum(r[2] * r[3] for r in tiles) == big["rect"][2] * (big["rect"][3] + 1), tiles)
_l, p2 = COV.walk_coverage(stations=[st for st in d.stations if st["shows"] != "hose"])
check("can-fail: a principle with no station is caught", any("hose" in p and "no station" in p for p in p2), p2[:3])
_l, p3 = COV.walk_coverage(not_on_walk={k: v for k, v in WP.NOT_ON_THE_WALK.items() if k != "ice_cuts_and_melts"})
check("can-fail: a locked bar neither served nor listed is caught", any("ice_cuts_and_melts" in p for p in p3), p3[:3])
_l, p4 = COV.walk_coverage(md_text="")
check("can-fail: a principle missing from the page is caught", any("not on the page" in p for p in p4))
check("the plan stands clear of the calm site's own geysers", not W.geyser_problems(d.stations, [(192, 184), (162, 97), (222, 69), (59, 141), (129, 211)]))
check("can-fail: a geyser inside a station is caught (the calm site's 59,141 in the old north-south row)",
      W.geyser_problems([dict(n=1, short="x", shows="bridge_kinds", rect=(57, 140, 3, 6))], [(59, 141)]))
bad = copy.deepcopy(d.stations)
bad[15]["short"] = "1 m of water in a 1 m hole"
check("can-fail: a name longer than its label's room is caught", any("label's room" in p for p in W.sign_problems(bad)))
order = [r[0] for r in W.staging_order(W.ROWS)]
check("the rows that advance the clock are staged before any colonist goes in",
      order[:len(W.TICK_ROWS)] == [r for r in order if r in W.TICK_ROWS], order)
s2 = W.WalkStage(None, True)
import contextlib, io  # noqa: E401,E402
with contextlib.redirect_stdout(io.StringIO()):
    for name, o, fn in W.staging_order(W.ROWS):
        W.stage_row(s2, name, o, fn)
W.renumber(s2.stations, d.stations)
check("staged in that order, the stations keep the plan's numbers", [(st["n"], st["short"]) for st in s2.stations] == [(st["n"], st["short"]) for st in d.stations])
md = W.stations_md(d.stations, "X.rws")
check("stations.md lists every station", all("| %d | " % st["n"] in md for st in d.stations))

# Review-stage swimmers (Steve2 job J20261124T165357Z-e3c928): owner_review_stage.Stage.swimmer defers the joint row's two swimmers to
# place_swimmers(); walk_map reuses that row, so a walk map that never calls it would stage no swimmer at all.
import contextlib  # noqa: E402
import io  # noqa: E402
import tempfile  # noqa: E402
import fw_walk_common as C  # noqa: E402
_games, _Real = [], C.FakeGame


def _mk():
    g = _Real()
    _games.append(g)
    return g


C.FakeGame = _mk
try:
    with contextlib.redirect_stdout(io.StringIO()):
        _rc = W.main(["--mock", "--only", "joint", "--no-save", "--no-shots", "--out", tempfile.mkdtemp(prefix="wm_joint_")])
finally:
    C.FakeGame = _Real
_spawned = {tuple(p) for p in _games[-1].pawns.values()} if _games else set()
check("the walk map's joint row stages both swimmers (placed after the staging's clock steps)",
      _rc == 0 and {(143, 19), (143, 25)} <= _spawned, (_rc, sorted(_spawned)))
print("SELFTEST walk_map: %d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
