"""Offline selftest for pipe_levelling_perf_proof.py: verdict functions, layout geometry and the mock paths (fixer I, 2026-10-22)."""
# selftest temp containment (BENCH, FLOWWORKS_SELFTESTS_FIX_TMPDIR_LEAKS): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_pipe_levelling_perf_proof_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import contextlib
import io
import json
import os
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pipe_levelling_perf_proof as L  # noqa: E402

fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


kv = L.parse("LEVELPERF calls=20 msAvg=3.2 msMax=4.8 msPerTick=0.0128 allocKBAvg=210.5 allocCalls=20 gcs=0 links=200 moves=37")
check("tick: fast, 200 links, staged: PASS", L.tick_verdict(kv, 200, 200, True) == ("PASS", "MOD"))
check("can-fail tick: 40 ms a cycle: FAIL", L.tick_verdict(dict(kv, msAvg="40", msPerTick="0.16"), 200, 200, True)[0] == "FAIL")
check("tick: fewer links than rigs: UNMEASURED/SITE", L.tick_verdict(kv, 12, 200, True) == ("UNMEASURED", "SITE"))
check("tick: basins not fully dug: UNMEASURED/SITE", L.tick_verdict(kv, 200, 200, False) == ("UNMEASURED", "SITE"))
check("tick: unread: UNMEASURED/HARNESS", L.tick_verdict({}, 200, 200, True) == ("UNMEASURED", "HARNESS"))
check("alloc: 210 KB: PASS", L.alloc_verdict(kv, 200, 200, True) == ("PASS", "MOD"))
check("can-fail alloc: 4 MB a cycle: FAIL", L.alloc_verdict(dict(kv, allocKBAvg="4096"), 200, 200, True)[0] == "FAIL")
check("alloc: NaN (GC in every call): UNMEASURED/HARNESS", L.alloc_verdict(dict(kv, allocKBAvg="NaN"), 200, 200, True)
      == ("UNMEASURED", "HARNESS"))

basins, spots, la, lb = L.layout((325, 325), 200, False)
check("layout (interior, default): two 38,125-square basins", [b[2] * b[3] for b in basins] == [38125, 38125])
# PERF_SCENE_REMEASURE_BASINS_OFF_EDGE: the old scene (z2..321) put basin rows inside the 10-square edge band, so with edge
# sinks on both basins drained off the map and the timing measured drain churn. Interior: no basin square in the band.
check("interior: every basin square >= 10 from every edge (no square in the sink band)", L.band_squares(basins, (325, 325)) == 0
      and all(b[0] >= 10 and b[1] >= 10 and b[0] + b[2] <= 315 and b[1] + b[3] <= 315 for b in basins))
eb, es, ela, elb = L.layout((325, 325), 200, False, "edge")
check("edge variant: the old scene, two 40,000-square basins z2..321", [b[2] * b[3] for b in eb] == [40000, 40000]
      and all(b[1] == 2 and b[1] + b[3] == 322 for b in eb))
check("can-fail band_squares: the edge scene has its south 8 (z2..9) and north 7 (z315..321) rows in the band",
      L.band_squares(eb, (325, 325)) == 2 * 125 * 15)
# band_squares against a brute-force count of RM_MapControls.EdgeSinkAt's test over every square, many rects
import random as _r
_rng = _r.Random(5)
_ok = True
for _ in range(300):
    sx, sz = _rng.randint(25, 60), _rng.randint(25, 60)
    x, z = _rng.randint(0, sx - 2), _rng.randint(0, sz - 2)
    w, h = _rng.randint(1, sx - x), _rng.randint(1, sz - z)
    brute = sum(1 for i in range(x, x + w) for j in range(z, z + h) if i < 10 or j < 10 or i >= sx - 10 or j >= sz - 10)
    _ok = _ok and L.band_squares([(x, z, w, h, 1)], (sx, sz)) == brute
check("band_squares equals a brute-force EdgeSinkAt band count on 300 random rects", _ok)
check("drain_free: no band squares -> free whatever the setting", L.drain_free(0, True) and L.drain_free(0, None))
check("drain_free: band squares + sinks off -> free; sinks on or unread -> not",
      L.drain_free(5, False) and not L.drain_free(5, True) and not L.drain_free(5, None))
check("can-fail tick: drain churn (no_drain False) is UNMEASURED/SITE, never a PASS",
      L.tick_verdict(kv, 200, 200, True, False) == ("UNMEASURED", "SITE")
      and L.alloc_verdict(kv, 200, 200, True, False) == ("UNMEASURED", "SITE"))
for _rh in (False, True):
    _sz = (325, 325) if not _rh else (120, 120)
    _b, _s, _la, _lb = L.layout(_sz, 200, _rh)
    check("interior %s: rigs clear of both basins and inside the map" % ("rehearsal 120" if _rh else "325"),
          L.band_squares(_b, _sz) == 0 and _s and all(_la < cx and cx + 3 < _lb and _b[0][1] <= z and z + 3 < _b[0][1] + _b[0][3]
                                                       for cx, z in _s))
check("layout: basins inside 325", all(b[0] + b[2] <= 325 and b[1] + b[3] <= 325 for b in basins))
check("layout: 200 rigs", len(spots) == 200)
check("layout: rigs (3 wide x 4 deep, reels + pipe run) in the gap, clear of both basins",
      all(la < cx and cx + 3 < lb and z + 3 < basins[0][1] + basins[0][3] for cx, z in spots))
check("layout: rigs never overlap", len({(cx + i, z + j) for cx, z in spots for i in range(3) for j in range(4)}) == 12 * len(spots))
ops = L.rig_ops(10, 4)
check("rig: reels joined by a 4-square pipe run, no tank", sum(o.startswith("RM_UniversalPipe") for o in ops) == 4
      and not any("Tank" in o for o in ops))
check("layout: every hose within the 80 clamp (straight-line + 10 detour)",
      all(abs(cx - la) + 10 <= 80 and abs(lb - cx) + 10 <= 80 for cx, _z in spots))
b2, s2, la2, lb2 = L.layout((120, 120), 200, True)
check("rehearsal layout fits a 120 map", all(b[0] + b[2] <= 120 and b[1] + b[3] <= 120 for b in b2) and s2 and lb2 < b2[1][0] + 1)

EXPECT = {"": {}, "old_deploy": {"LEVEL_PERF_TICK_TIME": ("UNMEASURED", "HARNESS"), "LEVEL_PERF_ALLOC": ("UNMEASURED", "HARNESS")},
          "no_link": {"LEVEL_PERF_TICK_TIME": ("UNMEASURED", "SITE"), "LEVEL_PERF_ALLOC": ("UNMEASURED", "SITE")},
          "slow": {"LEVEL_PERF_TICK_TIME": ("FAIL", "MOD")},
          "gc_every": {"LEVEL_PERF_ALLOC": ("UNMEASURED", "HARNESS")},
          "small_map": {"LEVEL_PERF_TICK_TIME": ("UNMEASURED", "SITE"), "LEVEL_PERF_ALLOC": ("UNMEASURED", "SITE")},
          "probe_dead": {"LEVEL_PERF_TICK_TIME": ("UNMEASURED", "HARNESS"), "LEVEL_PERF_ALLOC": ("UNMEASURED", "HARNESS")},
          "mech_raid": {"LEVEL_PERF_TICK_TIME": ("UNMEASURED", "SITE"), "LEVEL_PERF_ALLOC": ("UNMEASURED", "SITE")}}
tmp = tempfile.mkdtemp()
for fault, want in EXPECT.items():
    out = os.path.join(tmp, "lp_%s.json" % (fault or "clean"))
    with contextlib.redirect_stdout(io.StringIO()):
        L.main(["--mock", out] + (["--mock-faults", fault] if fault else []))
    rows = json.load(open(out))["rows"]
    got = {r["id"]: (r["detail"].get("mock"), r["class"]) for r in rows}
    bad = {k: v for k, v in got.items() if v[0] != "PASS"}
    check("mock %-10s -> %s" % (fault or "clean", want or "all PASS"),
          bad == want and len(rows) == 2 and all(r["status"] == "SKIP" and r["criterion"] == "A3" for r in rows))
# PERF_SCENE_REMEASURE_BASINS_OFF_EDGE end to end: the edge scene with sinks on is SITE; --sinks-off sets the setting false
# for the run and puts the value it found back; the interior default never touches the setting
for args, faults, want_mock, want_sets in ((["--basins", "edge"], [], "UNMEASURED", []),
                                           (["--basins", "edge", "--sinks-off"], [], "PASS", ["False", "True"]),
                                           ([], [], "PASS", []),
                                           # review: a drain-edge setter keeps the kernel's gate open with the setting off
                                           (["--basins", "edge", "--sinks-off"], ["drain_edge"], "UNMEASURED", ["False", "True"]),
                                           # review: an unread setting is put back to the shipped True, never left off
                                           (["--basins", "edge", "--sinks-off"], ["sinks_unread"], "PASS", ["False", "True"])):
    fb = L.FakeBridge(faults, L.MAP_NEED)
    orig = L.FakeBridge

    class _Same(orig):
        def __new__(cls, *a, **k):
            return fb
    L.FakeBridge = _Same
    out = os.path.join(tmp, "lp_edge_%d_%s.json" % (len(args), "-".join(faults)))
    with contextlib.redirect_stdout(io.StringIO()):
        L.main(["--mock", out] + args)
    L.FakeBridge = orig
    res = json.load(open(out))
    rows = res["rows"]
    check("mock %s %s -> %s, setting writes %s" % (" ".join(args) or "(interior)", ",".join(faults), want_mock, want_sets),
          len(rows) == 2 and all(r["detail"].get("mock") == want_mock for r in rows)
          and getattr(fb, "sink_sets", []) == want_sets
          and all(r["detail"]["noDrain"] == (want_mock == "PASS") for r in rows)
          and (want_mock == "PASS" or all(r["class"] == "SITE" and "drain churn" in r["detail"]["why"] for r in rows)))
# can-fail: the old tank rig (two reels touching a tank, no pipe run) makes no link, so the rows are UNMEASURED/SITE, never PASS
good_ops = L.rig_ops
L.rig_ops = lambda cx, z, *_lips: [L.V.reel_west((cx, z)), L.V.reel_west((cx, z + 2)), "RM_LiquidTank:%d,%d" % (cx + 2, z + 1)]
out = os.path.join(tmp, "lp_tank.json")
with contextlib.redirect_stdout(io.StringIO()):
    L.main(["--mock", out])
rows = json.load(open(out))["rows"]
check("can-fail: the old tank rig links nothing -> UNMEASURED/SITE",
      all(r["detail"].get("mock") == "UNMEASURED" and r["class"] == "SITE" and r["detail"]["links"] == 0 for r in rows) and len(rows) == 2)
L.rig_ops = good_ops
out = os.path.join(tmp, "lp_reh.json")
with contextlib.redirect_stdout(io.StringIO()):
    L.main(["--mock", out, "--rehearsal"])
rows = json.load(open(out))["rows"]
check("rehearsal: rows capped at UNMEASURED/SITE, would-be verdict kept",
      all(r["detail"].get("mock") == "UNMEASURED" and r["class"] == "SITE" and r["detail"].get("rehearsalVerdict") == "PASS"
          for r in rows))
# LEVEL_REHEARSAL_UNSTICK_WAITS_FOR_GODOT: a dead probe channel ends the run after 3 replies, not 400 lays x 20 s
fb = L.FakeBridge(["probe_dead"], 120)
orig = L.FakeBridge


class _One(orig):
    def __new__(cls, *a, **k):
        return fb


L.FakeBridge = _One
out = os.path.join(tmp, "lp_dead.json")
with contextlib.redirect_stdout(io.StringIO()):
    L.main(["--mock", out, "--rehearsal", "--mock-faults", "probe_dead"])
L.FakeBridge = orig
res = json.load(open(out))
check("watchdog: dead probe channel stops after 3 replies and is named", fb.hps == 3 and "probe channel dead" in res.get("watchdog", ""))
out = os.path.join(tmp, "lp_budget.json")
with contextlib.redirect_stdout(io.StringIO()):
    L.main(["--mock", out, "--budget-s", "-1"])
res = json.load(open(out))
check("watchdog: a spent budget writes both rows UNMEASURED/HARNESS",
      [(r["detail"].get("mock"), r["class"]) for r in res["rows"]] == [("UNMEASURED", "HARNESS")] * 2 and "budget" in res["watchdog"])
# a budget spent AFTER maxLength was set to 80 must still put the shipped length back: the restore bypasses the watchdog
# (before the fix it went through it, raised WatchdogAbort again and left the live game at 80)


class _LenBridge(orig):
    def __init__(self, *a, **k):
        orig.__init__(self, *a, **k)
        self.sets = []

    def call(self, tool, **kw):
        if tool == "jawa/mod_settings_field":
            if kw.get("action") == "get":
                return {"success": True, "value": 40}
            self.sets.append(kw.get("value"))
            return {"success": True}
        return orig.call(self, tool, **kw)


lb = _LenBridge([], 120)
L.FakeBridge = type("_OneLen", (orig,), {"__new__": lambda cls, *a, **k: lb})
real_wd = L.V.Watchdog
# the clock runs out once the rigs are built (pipes exist), i.e. after the set-80 and before the first lay
L.V.Watchdog = lambda B, budget, **kw: real_wd(B, budget, clock=lambda: 1e12 if lb.pipes else 0.0)
try:
    out = os.path.join(tmp, "lp_len.json")
    with contextlib.redirect_stdout(io.StringIO()):
        L.main(["--mock", out, "--rehearsal", "--budget-s", "100"])
finally:
    L.FakeBridge, L.V.Watchdog = orig, real_wd
res = json.load(open(out))
check("watchdog abort mid-run still restores hose maxLength (sets %s)" % lb.sets,
      "budget" in res.get("watchdog", "") and lb.sets[:1] == ["80"] and lb.sets[-1:] == ["40"])
check("phased lays: --lay A:B slices, clips and 0:0 lays none (LEVEL_PERF_PROOF_FIX_LAYS_OUTRUN_BUDGET)",
      L.lay_slice(None, 400) == (0, 400) and L.lay_slice("0:100", 400) == (0, 100) and L.lay_slice("100:200", 400) == (100, 200)
      and L.lay_slice("300:900", 400) == (300, 400) and L.lay_slice("0:0", 400) == (0, 0) and L.lay_slice("50:10", 400) == (50, 50))
# LEVEL_PERF_PROOF_SHRINK_TO_FIT_BUDGET: any --budget-s fits the 540 s foreground cap, restores included, and a call into a
# frozen main thread is abandoned at the budget (the 2026-10-24 run: budget 500, killed at 535, two calls reconciled by hand)
for req in (None, 0, 100, 480, 500, 900, 1e9):
    bud, rs, cc = L.fit_budget(req)
    if not (bud + 2 * rs + min(20.0, 0.04 * 540) <= 540 and 0 < cc <= 120 or bud <= 0):
        check("fit_budget(%s) fits 540: budget %.1f restore %.1f callcap %.1f" % (req, bud, rs, cc), False)
check("fit_budget: 900 is clamped below 540 with room for both restores",
      L.fit_budget(900)[0] < 540 - 2 * L.fit_budget(900)[1] and L.fit_budget(900)[0] == L.fit_budget(None)[0])
check("fit_budget: a request that fits is kept", L.fit_budget(100)[0] == 100.0)
out = os.path.join(tmp, "lp_900.json")
with contextlib.redirect_stdout(io.StringIO()):
    L.main(["--mock", out, "--budget-s", "900"])
res = json.load(open(out))
check("--budget-s 900: recorded clamped, effective under the cap",
      "clamped" in res["budget"] and res["budget"]["effective"] < 540 and res["budget"]["callCapS"] <= 120)
# the hung call: the game freezes at the first hose lay; every later call (the maxLength restore too) never returns
alive0 = threading.active_count()
out = os.path.join(tmp, "lp_freeze.json")
t = time.time()
with contextlib.redirect_stdout(io.StringIO()):
    code = L.main(["--mock", out, "--mock-faults", "freeze", "--budget-s", "900", "--hard-cap-s", "4", "--restore-length", "40"])
wall = time.time() - t
res = json.load(open(out))
check("hung call: watchdog kills it, run ends inside the 4 s cap (%.2f s), exit 2" % wall, wall < 4.0 and code == 2)
check("hung call: both rows UNMEASURED/HARNESS naming the never-returned call (%s)" % res.get("watchdog"),
      [(r["detail"].get("mock"), r["class"]) for r in res["rows"]] == [("UNMEASURED", "HARNESS")] * 2
      and "never returned" in res.get("watchdog", ""))
check("hung call: the frozen maxLength restore is abandoned and recorded, not waited on (%s)" % res.get("restoreTimeouts"),
      any("maxLength" in w for w in res.get("restoreTimeouts") or []))
# the Watchdog's per-call deadline on its own (validation_core.Watchdog call_cap_s)
class _Hang(object):
    def call(self, tool, **kw):
        threading.Event().wait()
t = time.time()
try:
    L.V.Watchdog(_Hang(), 100, call_cap_s=0.3).call("x")
    hit = False
except L.V.WatchdogAbort as ex:
    hit = "never returned" in str(ex)
check("Watchdog call_cap_s: a call that never returns raises WatchdogAbort at the cap (%.2f s)" % (time.time() - t),
      hit and time.time() - t < 1.5)
t = time.time()
try:
    L.V.Watchdog(_Hang(), 0.3, call_cap_s=60).call("x")
    hit = False
except L.V.WatchdogAbort:
    hit = True
check("Watchdog call_cap_s: the budget left bounds the call deadline (%.2f s)" % (time.time() - t), hit and time.time() - t < 1.5)
check("Watchdog call_cap_s: a returning call passes its value and its exception through",
      L.V.Watchdog(type("_R", (), {"call": lambda self, t: 7})(), 10, call_cap_s=5).call("x") == 7)
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
