#!/usr/bin/env python3
"""Offline selftest of the decilitre / level-water reads of water_scenes_walk.py, its mock, annotate_water_scenes.py and the
ACCUMULATING index.html of river_scenes_walk.py / objects_sheet.py (WALKS_FIX, 2026-10-17). No game: the walk runs on
water_scenes_mock.MockBridge. Proves the scripts' OWN paths and their pure arithmetic against the P3 numbers
(Transient/fw_scenes/p3_build_log.md); proves nothing about the game. Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_water_walks.py"""
import contextlib
import glob
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402
import water_scenes_mock as M  # noqa: E402
import water_scenes_walk as W  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rv = fn(*a, **k)
    return rv, buf.getvalue()


def close(a, b, tol):
    return a is not None and abs(a - b) <= tol


# ---- parse_readout: the strings captured live on 2026-10-17 (live_day2_report.md section 4)
R = W.parse_readout
r = R("OK Hole 0.5 m · Water 0.08 m (167 L)")
check("readout: wet canal sheet -> 1,670 dL", r and r["kind"] == "water" and r["dl"] == 1670 and r["hole_m"] == 0.5 and r["water_m"] == 0.08, r)
r = R("OK Hole 2 m · Water 1.74 m (3,474 L)")
check("readout: thousands separator -> 34,740 dL", r and r["dl"] == 34740 and r["hole_m"] == 2.0, r)
check("readout: dry dug square is 0 dL, not unread", (R("OK Hole 0.5 m · Water 0.00 m (0 L)") or {}).get("dl") == 0)
check("readout: limitless mark has no litres", (R("OK Open water, never runs dry (about 2 m deep)") or {}).get("kind") == "limitless")
check("readout: undug ground is kind none", (R("OK -") or {}).get("kind") == "none")
check("readout: refusal / empty / junk are None, never a zero", R("REFUSED out of bounds") is None and R("") is None and R("OK nonsense") is None
      and R(None) is None)

# ---- level_solution against the P3 oracle's numbers (Transient/fw_scenes/p3_build_log.md stage (a))
s, per = W.level_solution([(9, -2.0), (10, -0.5)], 36 * 10000)
check("S5 A: surface -0.263 m, canal squares 0.237 m (4,737 dL), pond 3,474 L a square", close(s, -0.2632, 5e-4)
      and close(per[1], 4737, 2) and close(per[0], 34737, 2), (s, per))
s, per = W.level_solution([(1, -2.0), (10, -0.5)], 4 * 10000)
check("S5 B: canal sheet 4.5 cm (909 dL a square), pond keeps 3,091 L", close(per[1] / W.DL_PER_METRE, 0.0455, 5e-4)
      and close(per[1], 909, 1) and close(per[0], 30909, 1), per)
s, per = W.level_solution([(36, -1.0)], 8 * 10000)
check("S5 E: 36 squares at 0.111 m (2,222 dL)", close(per[0] / W.DL_PER_METRE, 0.111, 5e-4) and close(per[0], 2222, 1), per)
s, per = W.level_solution([(1, -2.0), (1, -2.0)], 4 * 10000)
check("S5 F: 1.00 m and 1.00 m (20,000 dL each)", close(per[0], 20000, 1) and close(per[1], 20000, 1) and close(s, -1.0, 1e-6), (s, per))
s, per = W.level_solution([(6, -0.5)], 4 * 10000)
check("S5 G: pumped 4,000 L levels over six squares at 0.333 m", close(per[0] / W.DL_PER_METRE, 1 / 3.0, 1e-3), per)
s, per = W.level_solution([(9, -2.0), (10, -0.5)], 36 * 10000)
tot = 9 * per[0] + 10 * per[1]
check("level_solution conserves litres", close(tot, 360000, 1e-3), tot)
try:
    W.level_solution([(1, -0.5)], 10 * 10000)
    check("level_solution refuses water that does not fit", False)
except ValueError:
    check("level_solution refuses water that does not fit", True)

# ---- the tolerance helpers
check("near: within n squares of slack, None never agrees", W.near(1000, 1010) and not W.near(1000, 1011) and W.near(1000, 1030, 3)
      and not W.near(None, 5) and not W.near(5, None))
m = {(0, 0): (1, 0, 4737), (1, 0): (1, 0, 0), (2, 0): (1, 1, None), (3, 0): (0, 0, 0)}
check("wet / holds / dl_sum read decilitres, fall back to whole notches when unread",
      W.wet(m, (0, 0)) and not W.wet(m, (1, 0)) and W.wet(m, (2, 0)) and not W.holds(m, (0, 0), 1) and W.holds(m, (2, 0), 1)
      and W.dl_sum(m, [(0, 0), (1, 0)]) == 4737 and W.dl_sum(m, [(0, 0), (2, 0)]) is None)
check("fills_str shows litres when decilitres were read, whole notches when not",
      W.fills_str(m, [(0, 0), (1, 0), (2, 0)]) == "474 0 1" and W.dl_str(m, [(0, 0), (2, 0)]) == "4737 ?")
check("stock_dl: notches * 10,000, None-safe", W.stock_dl({"stock": 3.474}) == 34740 and W.stock_dl({"stock": None}) is None
      and W.stock_dl(None) is None)

# ---- S2.d settledness: the live false positive was a 4-pulse plateau at p7-p10, finished at p12
series = [(0,), (1,), (2,), (3,), (3,), (3,), (3,), (3,), (4,), (4,), (4,)] + [(4,)] * 14
old = W.settled_at(series, 3)
check("settled_at: the old 3-pulse test is fooled by a mid-fill plateau (the live bug, reproduced)", old == 3, old)
check("settled_at: N=%d unchanged pulses refuses the plateau and settles at the real end" % W.SETTLE_PULSES,
      W.settled_at(series, W.SETTLE_PULSES) == 8, W.settled_at(series, W.SETTLE_PULSES))
check("settled_at: ok() refuses a settle on a half-filled state",
      W.settled_at([(2,)] * 20, 8, ok=lambda s: s[0] >= 4) is None and W.settled_at([(2,)] * 5 + [(4,)] * 20, 8, ok=lambda s: s[0] >= 4) == 5)
check("settled_at: too short a run is None", W.settled_at([(1,)] * 5, 8) is None)

# ---- ProofLevelSurface parsing
b = W.parse_surface("OK 2 worst 0.0120 m;5,2:10:0.0120:-0.2700:-0.2580;9,9:1:0.0000:-0.5000:-0.5000;")
check("parse_surface: bodies, squares and gap in metres", len(b) == 2 and b[0]["squares"] == 10 and close(b[0]["gap_m"], 0.012, 1e-9)
      and b[1]["at"] == "9,9", b)
for bad in ("REFUSED no current map", "", "OK 1 worst 0 m;1,1:2:0.5"):
    try:
        W.parse_surface(bad)
        check("parse_surface refuses %r" % bad, False)
    except ValueError:
        check("parse_surface refuses %r" % bad, True)

# ---- the whole walk on the mock bridge
tmp = tempfile.mkdtemp(prefix="wwalks_")
W.OUT_MOCK = os.path.join(tmp, "mock")
OUT = W.OUT_MOCK


def rows_of(sid):
    return json.load(open(os.path.join(OUT, "%s_rows.json" % sid), encoding="utf-8"))


rc, out = quiet(W.main, ["all", "--mock", "--no-wait", "--pace", "0", "--no-shots"])
check("walk all --mock exits 0 with no CRASHED row", rc == 0 and "CRASHED" not in out, (rc, out[-200:]))
r5 = rows_of("S5")
ids5 = {x["id"] for x in r5}
check("S5 rows: every sealed-doc id a..i is there (a b c d e f g h i)", {"S5.a", "S5.b", "S5.c", "S5.d", "S5.e", "S5.f", "S5.g", "S5.h", "S5.i"} <= ids5, ids5)
check("S5 level rows for A, F, E, G", {"S5.lvl.A", "S5.lvl.F", "S5.lvl.E", "S5.lvl.G"} <= ids5, ids5)
check("S5 rows carry the level-water expectation and ProofReadout strings verbatim",
      all("level" in x for x in r5 if x["id"] in ("S5.a", "S5.b", "S5.c", "S5.g", "S5.i"))
      and any("Hole" in " ".join(x.get("readout", [])) and "Water" in " ".join(x.get("readout", [])) for x in r5), [x["id"] for x in r5 if "readout" in x])
check("S5 level expectation for A names 4,737 dL and 0.237 m", any("0.237 m" in x.get("level", "") and "4737" in x.get("level", "") for x in r5))
check("S2/S3/S6 have a level row each", any(x["id"] == "S2.lvl.end" for x in rows_of("S2")) and any(x["id"] == "S3.lvl" for x in rows_of("S3"))
      and {"S6.lvl.run1", "S6.lvl.run2"} <= {x["id"] for x in rows_of("S6")})
check("the log prints decilitres (pond dL) and the litres legend", "dL" in out and "LITRES" in out and "level:" in out)
check("only the allowed verdict words", {x["status"] for sid in W.ORDER for x in rows_of(sid)} <= {"MATCHES", "DIFFERS", "UNMEASURED", "OPEN RULING", "MEASURED", "CRASHED"})

# the level row can go RED: the mock reports a 5 cm gap
_init = M.MockBridge.__init__


def red_init(self, *a, **k):
    _init(self, *a, **k)
    self.mock_gap = "0.0500"


M.MockBridge.__init__ = red_init
rc, out = quiet(W.main, ["go", "S2", "--mock", "--pace", "0", "--no-shots"])
M.MockBridge.__init__ = _init
lvl = [x for x in rows_of("S2") if x["id"] == "S2.lvl.end"]
check("level row goes DIFFERS on a 5 cm gap and keeps the per-body gap", lvl and lvl[0]["status"] == "DIFFERS" and lvl[0].get("gaps")
      and "0.0500" in lvl[0]["gaps"][0], lvl)
# ...and UNMEASURED (never a pass) when the DLL predates the method
_st = M.MockBridge._static


def refusing(self, method, arg):
    if method == "ProofLevelSurface":
        return {"success": True, "result": "REFUSED no such method"}
    return _st(self, method, arg)


M.MockBridge._static = refusing
rc, out = quiet(W.main, ["go", "S2", "--mock", "--pace", "0", "--no-shots"])
M.MockBridge._static = _st
lvl = [x for x in rows_of("S2") if x["id"] == "S2.lvl.end"]
check("level row is UNMEASURED when ProofLevelSurface refuses", lvl and lvl[0]["status"] == "UNMEASURED", lvl)

rc, out = quiet(W.main, ["all", "--mock", "--no-wait", "--pace", "0", "--no-shots", "--mock-fail", "S4"])
check("mock crash in S4: traceback kept, S5 and S6 still ran, exit 1", rc == 1 and glob.glob(os.path.join(OUT, "S4_traceback_*.txt"))
      and "S5.i" in out and "S6.c" in out, (rc, out[-200:]))

# ---- the shelf pin (v2 triage 2026-10-18): off during a scene, previous value back after, also when the scene dies
import argparse as _ap  # noqa: E402
_w = W.Walk(_ap.Namespace(mock=True, mock_fail=None, fresh_map=False, no_shots=True, pace=0.0))
_w.B.call("jawa/mod_settings_field", typeName=W.S_FW, action="set", field="deepBedsEnabled", value="True")
_seen = []
_old_stage = W.STAGE["S1"]
W.STAGE["S1"] = lambda w_: _seen.append(w_.call("jawa/mod_settings_field", typeName=W.S_FW, action="get", field="deepBedsEnabled")["value"])
quiet(W.do_scene, _w, "S1", True, False)
_after = _w.call("jawa/mod_settings_field", typeName=W.S_FW, action="get", field="deepBedsEnabled")["value"]
check("scene pin: deepBedsEnabled is False while staging, True again after", _seen == ["False"] and _after == "True", (_seen, _after))
def _die(w_):
    raise KeyboardInterrupt()
W.STAGE["S1"] = _die
try:
    quiet(W.do_scene, _w, "S1", True, False)
except BaseException:  # noqa: BLE001
    pass
_after = _w.call("jawa/mod_settings_field", typeName=W.S_FW, action="get", field="deepBedsEnabled")["value"]
W.STAGE["S1"] = _old_stage
check("scene pin: restored after a crash that escapes the scene", _after == "True", _after)
check("scene pin: restore verb's SHIPPED list carries deepBedsEnabled True", W.SHIPPED.get("deepBedsEnabled") is True)

# ---- annotate_water_scenes: prints the readout string and the per-body gap
import annotate_water_scenes as A  # noqa: E402
live = os.path.join(tmp, "live")
os.makedirs(live)
C.synthetic_png(os.path.join(live, "S5AB_p20.png"), tag="S5AB_p20")
C.synthetic_png(os.path.join(live, "S2_p10.png"), tag="S2_p10")
RO = "132,32: Hole 0.5 m · Water 0.24 m (474 L)"
GAP = "body at 74,32: 19 sq, gap 0.0001 m (surface -0.2632..-0.2631 m)"
json.dump([dict(id="S5.b", status="MATCHES", doc="The pond holds less water than at the start.", game="pond 312660 dL",
                level="pond 312632 dL, each canal square 4737 dL", readout=[RO]),
           dict(id="S5.lvl.A", status="MATCHES", doc="One surface.", game="worst gap 0.0001 m", gaps=[GAP])],
          open(os.path.join(live, "S5_rows.json"), "w", encoding="utf-8"))
json.dump([dict(id="S2.a", status="MATCHES", doc="Pond full.", game="pulse 12")], open(os.path.join(live, "S2_rows.json"), "w"))
open(os.path.join(live, "S5_20261017T000000.txt"), "w", encoding="utf-8").write(
    "  step AB: parts A, B and F together\n  pulse 20  A canal [474 474] pond 312660 dL\n  step G: pump ON\n  pulse 20  canal [10 20]\n")
res, aout = quiet(A.main, live)
meas = [m for (s, n, mo, sc, mm) in res if n == "S5AB_p20" for m in mm]
check("annotate: S5 is no longer 'under redesign'", res and not any("redesign" in m for m in meas) and any("pulse 20: A canal" in m for m in meas), meas)
check("annotate: prints the ProofReadout string verbatim", any(RO in m for m in meas), meas)
check("annotate: prints the per-body surface gap", any(GAP in m for m in meas), meas)
check("annotate: prints the level-water expectation", any("each canal square 4737 dL" in m for m in meas), meas)
check("annotate: a step key picks its own pulse line (G pulse 20 is not AB pulse 20)",
      A.pulse_line("S5", "G", 20).endswith("canal [10 20]") and "A canal [474 474]" in A.pulse_line("S5", "AB", 20))
check("annotate: png and index.html written, index holds the readout and the gap",
      os.path.exists(os.path.join(live, "annotated", "S5AB_p20.png")) and RO in open(os.path.join(live, "annotated", "index.html"), encoding="utf-8").read()
      and GAP in open(os.path.join(live, "annotated", "index.html"), encoding="utf-8").read())

# ---- index.html accumulation (river_scenes_walk, objects_sheet, write_index)
import objects_sheet as OS_  # noqa: E402
import river_scenes_walk as RS  # noqa: E402

idx = os.path.join(tmp, "idx", "index.html")
C.write_index(idx, "t", "i", [dict(id="R1", title="one", readings=[("MATCHES", "a")])])
C.write_index(idx, "t", "i", [dict(id="R2", title="two", readings=[("MATCHES", "b")])])
C.write_index(idx, "t", "i", [dict(id="R1", title="one again", readings=[("DIFFERS", "c")])])
page = open(idx, encoding="utf-8").read()
check("write_index accumulates: R1 (newest text), R2 both on the page, R1 once, in first-seen order",
      "one again" in page and ">two<" in page and page.count("id='R1'") == 1 and page.index("id='R1'") < page.index("id='R2'")
      and ">one<" not in page, page[:300])
C.write_index(idx, "t", "i", [dict(id="R3", title="three")], accumulate=False)
page = open(idx, encoding="utf-8").read()
check("write_index accumulate=False starts afresh", "three" in page and "one again" not in page)
open(os.path.splitext(idx)[0] + ".groups.json", "w").write("{not json")
C.write_index(idx, "t", "i", [dict(id="R4", title="four")])
check("write_index: a corrupt sidecar is a fresh index, not a crash", "four" in open(idx, encoding="utf-8").read())

RS.OUT_MOCK = os.path.join(tmp, "rivers")
OS_.OUT_MOCK = os.path.join(tmp, "objects")
rc1, _ = quiet(RS.main, ["go", "R1", "--mock"])
rc2, _ = quiet(RS.main, ["go", "R2", "--mock"])
page = open(os.path.join(RS.OUT_MOCK, "index.html"), encoding="utf-8").read()
check("river index: `go R1` then `go R2` leaves BOTH scenes on index.html", rc1 == 0 and rc2 == 0 and "id='R1'" in page and "id='R2'" in page, (rc1, rc2))
rc3, _ = quiet(RS.main, ["go", "R2", "--mock"])
page = open(os.path.join(RS.OUT_MOCK, "index.html"), encoding="utf-8").read()
check("river index: re-running R2 replaces its section, keeps R1", page.count("id='R2'") == 1 and "id='R1'" in page)
rc4, _ = quiet(RS.main, ["go", "R3", "--mock", "--reset-index"])
page = open(os.path.join(RS.OUT_MOCK, "index.html"), encoding="utf-8").read()
check("river index: --reset-index starts afresh", "id='R3'" in page and "id='R1'" not in page and "id='R2'" not in page)
rc5, _ = quiet(OS_.main, ["--mock", "--only", "ladders"])
rc6, _ = quiet(OS_.main, ["--mock", "--only", "styles"])
ob = json.load(open(os.path.splitext(os.path.join(OS_.OUT_MOCK, "index.html"))[0] + ".groups.json", encoding="utf-8"))
page = open(os.path.join(OS_.OUT_MOCK, "index.html"), encoding="utf-8").read()
check("objects index: two runs on different groups leave both families on index.html", rc5 == 0 and rc6 == 0
      and any(g["id"].startswith("ladders_") for g in ob) and any(g["id"].startswith("styles_") for g in ob)
      and "ladders_" in page and "styles_" in page, [g["id"] for g in ob][:6])

print("selftest_water_walks: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
