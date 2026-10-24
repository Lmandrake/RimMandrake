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
# REVIEW_STAGER_FIX_NUMBER_EVERY_STATION: every station numbered, its world label carries the number of its caption line,
# and the default rows are dense (the 2026-10-24 map spaced sprinkler nets 14 apart and bridges 13 apart, unnumbered).
import io  # noqa: E402
import contextlib  # noqa: E402


def dry_stage(rows):
    d = ORS.Stage(None, True)
    L = ORS.layout(100, 100)
    caps = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for row in rows:
            if row == "gates":
                caps["gates_sluice"] = ORS.row_gates(d, L, "RM_Sluice", "gates_sluice", "WoodLog")
                caps["gates_grate"] = ORS.row_gates(d, L, "RM_SecurityGrateDoor", "gates_grate", "Steel")
            else:
                caps[row] = ORS.ROWS[row](d, L)
        ops = d.labels()
    return d, caps, ops


d, caps, ops = dry_stage(ORS.ALL_ROWS)
check("every default row registers stations", {st["row"] for st in d.stations} >= set(ORS.ALL_ROWS) - {"gates"} | {"gates_sluice", "gates_grate"},
      sorted({st["row"] for st in d.stations}))
check("stations numbered 1..N", [st["n"] for st in d.stations] == list(range(1, len(d.stations) + 1)))
lines = [c for row in caps.values() for c in (row if isinstance(row, list) else [])]
check("every caption line is numbered and matches the station list",
      lines == ["%d  %s" % (st["n"], st["text"]) for st in d.stations], lines[:4])
check("one world label per station, its text = the station's number",
      [o.split("|")[2] for o in ops] == [str(st["n"]) for st in d.stations], ops[:3])
check("every label is pinned on the row north of its station",
      all(tuple(map(int, o.split("|")[:2])) == ORS.station_label_cell(st) for o, st in zip(ops, d.stations)))
probs = ORS.layout_problems(d.stations, rows=ORS.ALL_ROWS)
check("default rows are dense, no overlap, no label inside a station", not probs, probs[:6])
bars = [st for st in d.stations if st["row"] in ORS.BARS_ROWS]
check("every bars station sits inside its own row's camera rect",
      all(ORS._inside((st["rect"][0], st["rect"][1]), ORS.bars_row_rect(L, st["row"])) and
          ORS._inside((st["rect"][0] + st["rect"][2] - 1, st["rect"][1] + st["rect"][3]), ORS.bars_row_rect(L, st["row"]))
          for st in bars), [st for st in bars if not ORS._inside((st["rect"][0], st["rect"][1]), ORS.bars_row_rect(L, st["row"]))][:2])
br = [st for st in d.stations if st["row"] in ("bars_bridges", "bars_bridge_kinds") and "bridge" in st["text"] and not st["text"].startswith("concealed")]
check("every bridge spans a pit 3 wide (owner: 'see these bridges over pits')",
      br and all(st["rect"][3] == 3 and "over a 4 m pit" in st["text"] for st in br), [st["text"] for st in br][:3])
# can-fail: the old spacing (sprinkler nets 14 apart, bridges 13 apart) and an unnumbered row are caught
old = [dict(n=k + 1, row="sprinklers", lane=0, rect=(100 + 14 * k, 150, 6, 6), text="net", short="net") for k in range(4)]
check("can-fail: the old 14-apart sprinkler nets read as sparse", any("sparse" in p for p in ORS.layout_problems(old)))
old_tr = [dict(n=k + 1, row="bars_trench", lane=0, rect=(150 + 5 * k, 122, 10, 3), text="t", short="t") for k in range(2)]
check("can-fail: the old trench pitch (shooter inside the next station) reads as overlap",
      any("overlap" in p for p in ORS.layout_problems(old_tr)))
check("can-fail: numbering with a hole is caught",
      any("numbers" in p for p in ORS.layout_problems([dict(old[0]), dict(old[1], n=3)])))
h, hcaps, hops = dry_stage(("hoses", "picks"))
check("optional rows are numbered too (hoses scenes, picks)", len(hops) == len(h.stations) >= 10 and
      all(c.split("  ")[0].isdigit() for c in hcaps["hoses"]["lines"] + hcaps["picks"]), len(hops))
print("selftest_owner_review_stage: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
