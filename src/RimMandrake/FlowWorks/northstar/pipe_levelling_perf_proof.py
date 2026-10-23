"""PIPE LEVELLING PERF live proof: PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A3 (L1) -- "325x325 map, two 40,000-cell basins,
200 links: live tick time and allocations of RM_Levelling.Tick (the dug-run walk is unmeasured offline)". Fixer I, 2026-10-22.

  python.exe src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py [out.json] [--rigs 200] [--calls 20] [--rehearsal]
  python3    src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py --mock [--mock-faults a,b] [--rehearsal]
             offline against FakeBridge (NOT the mod); every row is written SKIP with its would-be verdict under detail.mock

Run from the repo root with python.exe on a 325x325 map (no bridge tool makes one: start the debug game on a 325 map by
hand or from a save); the bridge must be held. On a smaller map every row is UNMEASURED/SITE, unless --rehearsal, which
stages scaled basins and fewer rigs to prove the harness and caps every row at UNMEASURED (rehearsal=True): a rehearsal is
never the A3 measurement. Exit 0 = every row PASS; 1 = a FAIL; 2 = a row could not be measured.

Calls (built 2026-10-22, fixer I): RM_NorthstarProofs.ProofStageBasin (dig + fill a rect through the engine's own Deepen /
TrySetDriverFill, in strips), ProofLevelLink (per-reel levelling state + process counters + intakes/outflows), ProofLevelPerf
(n back-to-back RM_Levelling.Tick calls, Stopwatch + managed-heap delta); RM_LineProofs.ProofHoseRole / ProofHoseLine; the hose
probe verb lay; jawa/build_batch; jawa/map_info.

LAYOUT (absolute map coords on a 325 map): basin A x10..134, basin B x190..314, both z2..321 (125 x 320 = 40,000 squares),
4 notches deep (2 m), A filled F=4 and B F=1 with RM_Fluid_Water (unequal, so links have work). The 55-wide gap holds rigs in
four columns (x 139 / 150 / 161 / 172), one rig per 5 rows from z 4 (the fifth row and the 7-square lanes between columns are
free, so a hose from an inner column can route out): the pond rig's shape (walk_gaps_proof _pond_rig) -- two 2x2
reels on footprints (cx, z) and (cx, z+2), each facing its lip (reel 1 West, reel 2 East: rig_ops), joined by an RM_UniversalPipe run at x cx+2, z..z+3 (rig_ops; NOT a tank: a tank does not conduct); reel 1 laid to A's lip (135, z) and set
Intake, reel 2 laid to B's lip (189, z+2) and set Outflow. A hose holds 40 squares as shipped (HoseMath.DefaultMaxLength) and
the far lip is up to 50 away, so RM_HoseSettings.maxLength is held at 80 (its clamp) for the run and put back after. The pipe-run layout is the one walk_gaps PONDS_* uses after the tank layout read
linked=false (2026-10-22). ProofLevelLink's links counter is
read before the timing; fewer links than --rigs is UNMEASURED/SITE naming intakes/outflows/on, never a PASS.

ROWS (both PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A3; PROVISIONAL bars, no owner number exists):
  LEVEL_PERF_TICK_TIME   ProofLevelPerf over --calls cycles: msAvg <= 16 ms per cycle (a cycle never costs a whole 60 fps
                         frame) and msPerTick = msAvg / 250 <= 0.1 ms.
  LEVEL_PERF_ALLOC       managed-heap growth per cycle (calls with no GC inside them) <= 1024 KB; NaN (every call saw a GC)
                         is UNMEASURED/HARNESS. GC.GetTotalMemory is a lower bound, not an allocation profiler.
LIES: the timed calls are real levelling cycles (water moves); RM_Levelling plans at most 64 links per cycle (MaxLinksPerCycle)
and walks at most 20,000 squares per run (MaxRunCells): a 40,000-square basin is under-walked by design, and that cost is what
is measured. A run whose basins were not fully dug (cells != dug) is SITE.
"""
import argparse
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402

LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
WATER_FLUID = "RM_Fluid_Water"
ITEM, CRIT = "PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL", "A3"
ROW_IDS = ["LEVEL_PERF_TICK_TIME", "LEVEL_PERF_ALLOC"]
MAP_NEED = 325
BAR_MS_CYCLE, BAR_MS_TICK, BAR_ALLOC_KB = 16.0, 0.1, 1024.0
LEVELS, FILL_A, FILL_B = 4, 4, 1


def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def fnum(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def layout(size, rigs, rehearsal):
    """(basins [(x,z,w,h,fill)], rig corners [(cx,z)], lipA x, lipB x). On a map smaller than 325 only with rehearsal."""
    if not rehearsal:
        bw, bh, ax, bx, z0 = 125, 320, 10, 190, 2
    else:
        bh = max(20, min(320, size[1] - 6))
        bw = max(10, min(125, (size[0] - 70) // 2))
        ax, z0 = 5, 2
        bx = ax + bw + 55
    cols = (ax + bw + 5, ax + bw + 16, ax + bw + 27, ax + bw + 38)
    spots = [(cx, z) for z in range(z0 + 2, z0 + bh - 5, 5) for cx in cols]
    return ([(ax, z0, bw, bh, FILL_A), (bx, z0, bw, bh, FILL_B)], spots[:rigs], ax + bw, bx - 1)


def rig_ops(cx, z, lip_a=None, lip_b=None):
    """Build ops of one rig: two 2x2 reels on footprints (cx, z) and (cx, z+2), each facing its hose's lip (reel 1 West to A's lip
    lip_a, reel 2 East to B's lip lip_b; West when a lip is None -- PROOF_REELS_FIX_STILL_STAGED_WEST), whose East edges both touch ONE RM_UniversalPipe
    run x cx+2, z..z+3. A pipe conducts; an RM_LiquidTank does NOT (RM_NetComponents.Build attaches it as a member and never walks
    through it), so two reels on one tank were two components with one port each and levelled nothing (walk_gaps_proof, 2026-10-22)."""
    ta = None if lip_a is None else (lip_a, z)
    tb = None if lip_b is None else (lip_b, z + 2)
    # reel 2 East would face the pipe run built against its east edge: blocked, West (PROOF_REELS_FIX_STILL_STAGED_WEST)
    return [V.reel_toward((cx, z), ta, roomy=True), V.reel_toward((cx, z + 2), tb, blocked=(1,))] + ["RM_UniversalPipe:%d,%d" % (cx + 2, z + j) for j in range(4)]


def tick_verdict(kv, links, want_links, staged_ok):
    avg, tick = fnum(kv.get("msAvg")), fnum(kv.get("msPerTick"))
    if avg is None or tick is None:
        return "UNMEASURED", "HARNESS"
    if not staged_ok or links is None or links < want_links:
        return "UNMEASURED", "SITE"
    return ("PASS" if avg <= BAR_MS_CYCLE and tick <= BAR_MS_TICK else "FAIL"), "MOD"


def alloc_verdict(kv, links, want_links, staged_ok):
    kb = fnum(kv.get("allocKBAvg"))
    if kb is None:
        return "UNMEASURED", "HARNESS"
    if not staged_ok or links is None or links < want_links:
        return "UNMEASURED", "SITE"
    return ("PASS" if kb <= BAR_ALLOC_KB else "FAIL"), "MOD"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--rigs", type=int, default=200)
    ap.add_argument("--calls", type=int, default=20, help="levelling cycles timed (1..200)")
    ap.add_argument("--rehearsal", action="store_true", help="scaled layout on a smaller map; rows capped at UNMEASURED")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-faults", default="", help="comma list: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    if a.mock:
        raw = FakeBridge(faults, 120 if a.rehearsal else MAP_NEED)
    else:
        import proof_hose as PH          # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
    B = V.guard(raw)
    out = a.out or (os.path.join(tempfile.gettempdir(), "level_perf_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "level_perf_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "pipe_levelling_perf_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    if a.mock:
        res["mode"] = "mock"
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, det, cls="MOD"):
        st, cls, det = V.PRE.judge(st, cls, det)
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"
        if a.rehearsal and st != "UNMEASURED":
            det = dict(det, rehearsalVerdict=st)
            st, cls = "UNMEASURED", "SITE"
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "criterion": CRIT, "detail": dict(det, rehearsal=a.rehearsal)})
        print("%-22s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def finish(code):
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        if a.mock:
            bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
            print("MOCK: level perf: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
            return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
        print("level perf: %d rows -> %s" % (len(rows), out))
        return code

    def all_rows(st, why, cls):
        for rid in ROW_IDS:
            row(rid, st, {"why": why}, cls=cls)

    def static(method, arg, ty=NPROOF):
        r = B.call("jawa/static_call", type=ty, method=method, args=arg, _answer=True) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        ok = r.get("success") is True and not txt.startswith("REFUSED")
        return (parse(txt) if ok else {}), txt

    # ------------------------------------------------------------------ preflight
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        all_rows("UNMEASURED", "no game in Playing", "HARNESS")
        return finish(2)
    probe = static("ProofLevelPerf", "0")[1]
    if "arg must be" not in probe:
        all_rows("UNMEASURED", "ProofLevelPerf not in the loaded FlowWorks (old deploy?): " + probe[:160], "HARNESS")
        return finish(2)
    mi = B.call("jawa/map_info", _answer=True) or {}
    size = (mi.get("sizeX"), mi.get("sizeZ") or mi.get("sizeY"))
    res["mapSize"] = size
    if not size[0] or not size[1]:
        all_rows("UNMEASURED", "jawa/map_info gave no size: %s" % str(mi)[:160], "HARNESS")
        return finish(2)
    big = size[0] >= MAP_NEED and size[1] >= MAP_NEED
    if not big and not a.rehearsal:
        all_rows("UNMEASURED", "A3 needs a 325x325 map; this one is %sx%s (no tool makes one: load or start one by hand)" % size,
                 "SITE")
        return finish(2)
    basins, spots, lip_a, lip_b = layout(size, a.rigs, a.rehearsal or not big)
    res["layout"] = {"basins": basins, "rigs": len(spots), "lipA": lip_a, "lipB": lip_b}

    # ------------------------------------------------------------------ stage the basins (strips of <= 12,500 squares)
    staged = []
    for (x, z, w, h, fill) in basins:
        cells = dug = 0
        step = max(1, 12500 // w)
        for zz in range(z, z + h, step):
            kv, txt = static("ProofStageBasin", "%d;%d;%d;%d;%d;%d;%s" % (x, zz, w, min(step, z + h - zz), LEVELS, fill, WATER_FLUID))
            if not kv:
                staged.append({"basin": (x, z, w, h), "refused": txt[:200]})
                break
            cells += int(kv.get("cells", 0))
            dug += int(kv.get("dug", 0))
        else:
            staged.append({"basin": (x, z, w, h), "cells": cells, "dug": dug})
    res["staged"] = staged
    staged_ok = all(s.get("cells") and s["cells"] == s["dug"] == s["basin"][2] * s["basin"][3] for s in staged)

    # ------------------------------------------------------------------ the rigs (hose length held at 80 for the run)
    HS = "RimMandrake.FlowWorks.Hose.RM_HoseSettings"
    len0 = (B.call("jawa/mod_settings_field", typeName=HS, action="get", field="maxLength", _answer=True) or {}).get("value")
    lr80 = B.call("jawa/mod_settings_field", typeName=HS, action="set", field="maxLength", value="80", _answer=True) or {}
    res["hoseMaxLength"] = {"before": len0, "set80": lr80.get("success")}
    try:
        return _rigs_and_time(a, B, static, row, res, spots, lip_a, lip_b, staged_ok, size, finish, rows)
    finally:
        if len0 is not None:
            B.call("jawa/mod_settings_field", typeName=HS, action="set", field="maxLength", value=str(len0), _answer=True)


def _rigs_and_time(a, B, static, row, res, spots, lip_a, lip_b, staged_ok, size, finish, rows):
    for i in range(0, len(spots), 40):
        ops = []
        for cx, z in spots[i:i + 40]:
            ops += rig_ops(cx, z, lip_a, lip_b)
        B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False)
    B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
    lay_fail = 0
    for cx, z in spots:
        for r, to, role in (((cx, z), (lip_a, z), "Intake"), ((cx, z + 2), (lip_b, z + 2), "Outflow")):
            lr = B.hp("lay:%d,%d,%d,%d" % (r + to), answer=True) or {}
            if lr.get("success") is not True:
                lay_fail += 1
                continue
            static("ProofHoseRole", "%d,%d;%s" % (r + (role,)), ty=LPROOF)
    res["layFailures"] = lay_fail
    B.call("rimworld/step_game_ticks", ticks=260, pauseFirst=True, timeoutMs=120000)
    kl, tl = static("ProofLevelLink", "%d,%d" % spots[0]) if spots else ({}, "no rigs")
    links = int(kl["links"]) if kl.get("links", "").isdigit() else None
    want = len(spots)
    perf, tp = static("ProofLevelPerf", str(max(1, min(200, a.calls))))
    det = {"perf": tp[:300], "levelLink": tl[:300], "links": links, "wantLinks": want, "stagedOk": staged_ok,
           "layFailures": lay_fail, "mapSize": size}
    st, cls = tick_verdict(perf, links, want, staged_ok)
    row("LEVEL_PERF_TICK_TIME", st, det, cls=cls)
    st, cls = alloc_verdict(perf, links, want, staged_ok)
    row("LEVEL_PERF_ALLOC", st, det, cls=cls)
    fails = [r for r in rows if r["status"] == "FAIL"]
    return finish(1 if fails else (2 if any(r["status"] != "PASS" for r in rows) else 0))


# ====================================================================== offline stand-in
class FakeBridge(object):
    """Answers in the live tools' and proofs' shapes; knows nothing about the game (proves control flow and the split only).
      old_deploy   ProofLevelPerf missing                   -> both rows UNMEASURED/HARNESS
      no_link      the rigs make no levelling link          -> both rows UNMEASURED/SITE
      slow         MOD: a cycle costs 40 ms                  -> LEVEL_PERF_TICK_TIME FAIL
      gc_every     every timed call saw a collection         -> LEVEL_PERF_ALLOC UNMEASURED/HARNESS
      small_map    the map is 250x250 (no --rehearsal)       -> both rows UNMEASURED/SITE"""
    FAULTS = ("old_deploy", "no_link", "slow", "gc_every", "small_map")

    def __init__(self, faults=(), size=MAP_NEED):
        self.f = set(faults)
        self.size = 250 if "small_map" in self.f else size
        self.reels = {}
        self.pipes = set()
        self.dug = 0

    def static(self, ty, m, arg):
        if m == "ProofLevelPerf":
            if "old_deploy" in self.f:
                return None
            if arg == "0":
                return "REFUSED: arg must be n (1..200) on the current map"
            ms = 40.0 if "slow" in self.f else 3.2
            alloc = "NaN" if "gc_every" in self.f else "210.5"
            return "LEVELPERF calls=%s msAvg=%.3f msMax=%.3f msPerTick=%.5f allocKBAvg=%s allocCalls=%d gcs=0 links=%d moves=3 " \
                   "cycleTicks=250" % (arg, ms, ms * 1.5, ms / 250, alloc, 0 if alloc == "NaN" else int(arg), self.links())
        if m == "ProofStageBasin":
            x, z, w, h, lv, fill, fl = arg.split(";")
            n = int(w) * int(h)
            return "BASIN cells=%d dug=%d filled=%d refused=0 maxDepth=%s" % (n, n, n, lv)
        if m == "ProofLevelLink":
            return "LEVELLINK reel=1 state=Flowing role=Intake laid=True intakes=1 outflows=1 on=True cycles=3 links=%d moves=1 " \
                   "movedDl=10" % self.links()
        if m == "ProofHoseRole":
            c, role = arg.split(";")
            self.reels.setdefault(c, {})["role"] = role
            return "ROLE role=" + role
        return "REFUSED: unknown " + m

    def links(self):
        """A link = an Intake reel and an Outflow reel whose East-edge neighbours lie on ONE 4-connected run of built pipes
        (a tank, or no pipe, joins nothing: the same coupling rule walk_gaps_proof.pond_rig_problems models)."""
        if "no_link" in self.f:
            return 0
        comp, n = {}, 0
        for p in sorted(self.pipes):
            if p in comp:
                continue
            n += 1
            todo = [p]
            while todo:
                q = todo.pop()
                if q in comp or q not in self.pipes:
                    continue
                comp[q] = n
                todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
        roles = {}
        for c, r in self.reels.items():
            x, z = (int(v) for v in c.split(","))
            runs = {comp[(x + 2, z + j)] for j in (0, 1) if (x + 2, z + j) in comp}
            if len(runs) == 1 and r.get("role"):
                roles.setdefault(runs.pop(), set()).add(r["role"])
        return sum(1 for rs in roles.values() if {"Intake", "Outflow"} <= rs)

    def hp(self, cmd, wait_s=20.0, answer=False):
        return {"success": True, "layOk": True}

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            txt = self.static(kw.get("type"), kw.get("method"), kw.get("args") or "")
            if txt is None:
                return {"success": False, "error": "Method not found"}
            return {"success": True, "result": txt}
        if tool == "jawa/build_batch":
            for op in str(kw.get("ops", "")).split(";"):
                name, _, xy = op.partition(":")
                if name == "RM_UniversalPipe":
                    self.pipes.add(tuple(int(v) for v in xy.split(",")[:2]))
            return {"success": True}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": self.size, "sizeZ": self.size}
        return {"success": True}


if __name__ == "__main__":
    sys.exit(main())
