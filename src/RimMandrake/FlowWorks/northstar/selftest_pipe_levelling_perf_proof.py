"""Offline selftest for pipe_levelling_perf_proof.py: verdict functions, layout geometry and the mock paths (fixer I, 2026-10-22)."""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pipe_levelling_perf_proof as L  # noqa: E402

fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


kv = L.parse("LEVELPERF calls=20 msAvg=3.2 msMax=4.8 msPerTick=0.0128 allocKBAvg=210.5 allocCalls=20 gcs=0 links=200")
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
check("layout: two 40,000-square basins", [b[2] * b[3] for b in basins] == [40000, 40000])
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
          "small_map": {"LEVEL_PERF_TICK_TIME": ("UNMEASURED", "SITE"), "LEVEL_PERF_ALLOC": ("UNMEASURED", "SITE")}}
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
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
