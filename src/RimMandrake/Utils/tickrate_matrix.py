#!/usr/bin/env python3
"""tickrate_matrix.py -- a controlled ticks/s benchmark: minimal list vs full list, empty vs busy map
(PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES, fast-testing #8; "60-280 ticks/s" was the only figure on file).

    python3 src/RimMandrake/Utils/tickrate_matrix.py run --cell T1      # one cell on the running game (a live proof)
    python3 src/RimMandrake/Utils/tickrate_matrix.py report             # the 2x2 matrix from the newest JSON per cell
    python3 src/RimMandrake/Utils/tickrate_matrix.py --mock             # the selftest: every path against a fake game

CELLS (each is one live-proof clause of infrastructure/state/live_proofs/PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES.txt):
  T1 minimal list, empty map    T2 minimal list, busy map
  T3 full list,    empty map    T4 full list,    busy map
The map is held fixed so only the cell's two factors move: every trial reloads the same test site save (`calm`,
test_site_saves.py: every non-colonist and every ruin removed), and "busy" is that map plus BUSY_N wild Muffalo spawned
at its centre (Core's PawnKindDef, on every list). The list is read, never assumed: jawa/running_mods must count
<= MINIMAL_MAX packages for a minimal cell and >= FULL_MIN for a full one (the bar the full-list proofs use), else the
cell exits 2 WRONG_LIST and measures nothing.

A trial is vanilla's own loop: Ultrafast, no UltraSpeedBoost, unpaused for WINDOW_S of wall clock after a WARMUP_S
unpaused warm-up, ticksGame read before and after (jawa/time_clock). ticks/s = moved ticks / wall seconds. REPEATS
trials per cell, each after its own reload (and, busy, its own spawn).

Exit codes of `run`: 0 every trial measured and the spread holds (max-min <= SPREAD_MAX of the mean); 1 measured but
uncontrolled (spread over the bar, or a busy map that did not gain the pawns it was given); 2 UNMEASURED with its reason
(no bridge, wrong list, a site that would not load, a clock that did not move). The JSON is written either way:
<agent storage>\\rimmandrake\\tickrate\\<cell>_<stamp>.json.
"""
import argparse
import glob
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CELLS = {"T1": ("minimal", "empty"), "T2": ("minimal", "busy"), "T3": ("full", "empty"), "T4": ("full", "busy")}
SITE = "calm"
BUSY_KIND, BUSY_N = "Muffalo", 60
# jawa/spawn_pawn refuses count > 50 (JawaBenchTerrainTools.cs SpawnPawn), so BUSY_N goes in calls of at most this.
SPAWN_CAP = 50
MINIMAL_MAX, FULL_MIN = 100, 300
WARMUP_S, WINDOW_S, REPEATS = 5.0, 20.0, 3
SPREAD_MAX = 0.5
UNMEASURED = "UNMEASURED"


def out_dir(arg=None):
    if arg:
        return arg
    from rmpaths import rm_str
    return rm_str("tickrate")


def list_check(call, want):
    """-> (count, why or None). want: minimal | full."""
    r = call("jawa/running_mods") or {}
    ids = r.get("packageIds")
    if not isinstance(ids, list):
        return None, "WRONG_LIST: jawa/running_mods gave no packageIds (%s)" % str(r)[:160]
    n = len(ids)
    if want == "minimal" and n > MINIMAL_MAX:
        return n, "WRONG_LIST: %d running mods, a minimal cell needs <= %d" % (n, MINIMAL_MAX)
    if want == "full" and n < FULL_MIN:
        return n, "WRONG_LIST: %d running mods, a full cell needs >= %d" % (n, FULL_MIN)
    return n, None


def pawns(call):
    r = call("jawa/list_pawns", limit=5000) or {}
    p = r.get("pawns")
    return len(p) if isinstance(p, list) else None


def ticks(call):
    r = call("jawa/time_clock") or {}
    try:
        return int(r.get("ticksGame"))
    except (TypeError, ValueError):
        return None


def trial(call, sleep, clock):
    """One vanilla Ultrafast window -> {tps, moved, wallS} or {unmeasured}."""
    call("rimworld/set_time_speed", speed="Ultrafast", ultraSpeedBoost=False)
    call("rimworld/pause_game", pause=False)
    sleep(WARMUP_S)
    p0 = call("jawa/time_perf") or {}
    t0, w0 = ticks(call), clock()
    sleep(WINDOW_S)
    t1, w1 = ticks(call), clock()
    p1 = call("jawa/time_perf") or {}
    call("rimworld/pause_game", pause=True)
    call("rimworld/set_time_speed", speed="Normal", ultraSpeedBoost=False)
    for when, p in (("start", p0), ("end", p1)):    # a dialog that pauses, or a refused speed, is no vanilla Ultrafast rate
        if p.get("paused") is not False or p.get("curTimeSpeed") != "Ultrafast" or p.get("ultraSpeedBoost") is True:
            return {"unmeasured": "not unpaused Ultrafast at the window's %s (time_perf paused=%s speed=%s boost=%s)"
                    % (when, p.get("paused"), p.get("curTimeSpeed"), p.get("ultraSpeedBoost"))}
    if t0 is None or t1 is None or w1 <= w0 or t1 <= t0:
        return {"unmeasured": "the clock did not move (ticks %s -> %s over %.1f s)" % (t0, t1, w1 - w0)}
    return {"tps": round((t1 - t0) / (w1 - w0), 2), "moved": t1 - t0, "wallS": round(w1 - w0, 3)}


def run_cell(call, cell, reload, sleep=time.sleep, clock=time.time, repeats=REPEATS):
    """-> (exit, result dict)."""
    lst, mp = CELLS[cell]
    res = {"item": "PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES", "cell": cell, "list": lst, "map": mp, "site": SITE,
           "busy": {"kind": BUSY_KIND, "n": BUSY_N} if mp == "busy" else None, "warmupS": WARMUP_S,
           "windowS": WINDOW_S, "repeats": repeats, "trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    n, why = list_check(call, lst)
    res["runningMods"] = n
    if why:
        res["unmeasured"] = why
        return 2, res
    for i in range(repeats):
        tr = {"trial": i}
        rl = reload(SITE) or {}
        tr["reload"] = rl
        if not rl.get("verified"):
            res["trials"].append(tr)
            res["unmeasured"] = "the %s site did not load: %s" % (SITE, str(rl.get("problems"))[:200])
            return 2, res
        before = pawns(call)
        if mp == "busy":
            calls, left = [], BUSY_N
            while left > 0:
                k = min(left, SPAWN_CAP)
                sp = call("jawa/spawn_pawn", kindDef=BUSY_KIND, x=125, z=125, faction="none", count=k) or {}
                calls.append({"count": k, "success": sp.get("success"), "error": sp.get("error")})
                left -= k
            tr["spawn"] = {"success": all(c["success"] is True for c in calls), "calls": calls}
        after = pawns(call)
        tr["pawns"] = after
        if mp == "busy" and (before is None or after is None or after - before < BUSY_N):
            res["trials"].append(tr)
            errs = [c["error"] for c in tr.get("spawn", {}).get("calls", []) if c.get("error")]
            res["uncontrolled"] = "the busy map gained %s pawns of %d%s" % (
                None if before is None or after is None else after - before, BUSY_N,
                (" (spawn_pawn: %s)" % "; ".join(str(e)[:160] for e in errs)) if errs else "")
            return 1, res
        tr.update(trial(call, sleep, clock))
        res["trials"].append(tr)
        if "unmeasured" in tr:
            res["unmeasured"] = tr["unmeasured"]
            return 2, res
    tps = [t["tps"] for t in res["trials"]]
    mean = statistics.mean(tps)
    res.update(meanTps=round(mean, 2), minTps=min(tps), maxTps=max(tps), spread=round((max(tps) - min(tps)) / mean, 4))
    if res["spread"] > SPREAD_MAX:
        res["uncontrolled"] = "trials spread %.0f%% of the mean (bar %.0f%%)" % (100 * res["spread"], 100 * SPREAD_MAX)
        return 1, res
    return 0, res


def write(res, d):
    os.makedirs(d, exist_ok=True)
    now = time.time()
    p = os.path.join(d, "%s_%s%06dZ.json" % (res["cell"], time.strftime("%Y%m%dT%H%M%S", time.gmtime(now)),
                                            int((now % 1) * 1e6)))      # sorts by time: matrix() takes the last
    with open(p, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return p


def matrix(d):
    """-> {cell: newest measured result or None}: a cell with no clean JSON reads UNMEASURED."""
    out = {}
    for cell in CELLS:
        best = None
        for p in sorted(glob.glob(os.path.join(d, "%s_*.json" % cell))):
            try:
                with open(p, encoding="utf-8") as f:
                    r = json.load(f)
            except (OSError, ValueError):
                continue
            if r.get("meanTps") is not None and not r.get("uncontrolled") and not r.get("unmeasured"):
                best = dict(r, path=p)
        out[cell] = best
    return out


def report_lines(m):
    def v(c):
        return UNMEASURED if m.get(c) is None else "%.0f ticks/s (n=%d, spread %.0f%%)" % (
            m[c]["meanTps"], len(m[c]["trials"]), 100 * m[c]["spread"])

    def ratio(a, b):
        return UNMEASURED if m.get(a) is None or m.get(b) is None else "%.2f" % (m[a]["meanTps"] / m[b]["meanTps"])
    return ["ticks/s, vanilla Ultrafast on the %s site (newest clean run per cell):" % SITE,
            "                 empty map                        busy map (+%d %s)" % (BUSY_N, BUSY_KIND),
            "  minimal list   %-32s %s" % (v("T1"), v("T2")),
            "  full list      %-32s %s" % (v("T3"), v("T4")),
            "  full/minimal: empty %s, busy %s; busy/empty: minimal %s, full %s"
            % (ratio("T3", "T1"), ratio("T4", "T2"), ratio("T2", "T1"), ratio("T4", "T3"))]


# ---------------------------------------------------------------- selftest
class Game(object):
    """A fake running game: `mods` packages, a clock whose rate falls with pawns (cost_ms per tick per pawn)."""
    def __init__(self, mods=40, base_ms=2.0, pawn_ms=0.05, spawn_gain=None, jitter=(), load_ok=True, frozen=False,
                 force_pause=False, refuse_speed=False):
        self.mods, self.base_ms, self.pawn_ms, self.load_ok, self.frozen = mods, base_ms, pawn_ms, load_ok, frozen
        self.force_pause, self.refuse_speed, self.speed = force_pause, refuse_speed, "Normal"
        self.spawn_gain, self.jitter = spawn_gain, list(jitter)
        self.t, self.wall, self.paused, self.n, self.calls = 1000, 0.0, True, 3, []

    def __call__(self, tool, **kw):
        self.calls.append(tool)
        if tool == "jawa/running_mods":
            return {"packageIds": ["m%d" % i for i in range(self.mods)]}
        if tool == "jawa/list_pawns":
            return {"pawns": [{}] * self.n}
        if tool == "jawa/spawn_pawn":
            if kw["count"] > SPAWN_CAP:  # the live tool's own refusal, so the mock cannot hide an over-cap ask
                return {"success": False, "error": "count %d > 50. Spawn fewer, or call again." % kw["count"]}
            self.n += kw["count"] if self.spawn_gain is None else self.spawn_gain
            return {"success": True}
        if tool == "jawa/time_clock":
            return {"ticksGame": self.t}
        if tool == "rimworld/pause_game":
            self.paused = kw["pause"] or self.force_pause
        if tool == "rimworld/set_time_speed":
            self.speed = kw["speed"] if not self.refuse_speed else "Normal"
        if tool == "jawa/time_perf":
            return {"success": True, "paused": self.paused, "curTimeSpeed": self.speed, "ultraSpeedBoost": False}
        return {"success": True}

    def reload(self, site):
        self.n = 3
        return {"verified": self.load_ok, "problems": None if self.load_ok else ["missing save"]}

    def sleep(self, s):
        if not self.paused and not self.frozen:
            ms = (self.base_ms + self.pawn_ms * self.n) * (self.jitter.pop(0) if self.jitter else 1.0)
            self.t += int(s * 1000.0 / ms)
        self.wall += s

    def clock(self):
        return self.wall


def selftest():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append((name, detail))

    def go(cell, g, **kw):
        return run_cell(g, cell, g.reload, sleep=g.sleep, clock=g.clock, **kw)

    rc, r = go("T1", Game())
    check("T1: measured, exit 0", rc == 0 and r["meanTps"] is not None, r)
    # 2.0 + 0.05 * 3 pawns = 2.15 ms a tick -> int(20 s * 1000 / 2.15) = 9302 ticks in 20 s = 465.1 ticks/s
    check("T1: ticks/s is moved ticks over the wall window, warm-up excluded", r["trials"][0]["tps"] == 465.1, r["trials"])
    check("T1: three trials, each after its own reload", len(r["trials"]) == 3
          and all(t["reload"]["verified"] for t in r["trials"]), r)
    g = Game()
    rc2, r2 = go("T2", g)
    check("T2: busy is slower than empty on the same game", rc2 == 0 and r2["meanTps"] < r["meanTps"], (r["meanTps"], r2))
    check("T2: the busy map holds the spawned pawns", r2["trials"][0]["pawns"] == 3 + BUSY_N, r2["trials"][0])
    check("T2: Muffalo spawned wild in two capped calls (50 + 10) per trial", g.calls.count("jawa/spawn_pawn") == 6
          and [c["count"] for c in r2["trials"][0]["spawn"]["calls"]] == [50, 10] and r2["trials"][0]["spawn"]["success"],
          (g.calls, r2["trials"][0]))
    g = Game()
    check("mock spawn_pawn refuses an over-cap ask as the live tool does", g("jawa/spawn_pawn", count=60)["success"]
          is False and g.n == 3, g.n)
    rc, r = go("T3", Game(mods=40))
    check("T3 on a 40-mod list: UNMEASURED WRONG_LIST, nothing run", rc == 2 and r["unmeasured"].startswith("WRONG_LIST")
          and not r["trials"], r)
    rc, r = go("T1", Game(mods=320))
    check("T1 on a 320-mod list: WRONG_LIST", rc == 2 and "WRONG_LIST" in r["unmeasured"], r)
    rc, r = go("T4", Game(mods=320))
    check("T4 on a 320-mod list: measured", rc == 0, r)
    rc, r = go("T2", Game(spawn_gain=0))
    check("a spawn that adds no pawns is uncontrolled (exit 1), not a busy figure", rc == 1 and "gained 0" in
          r["uncontrolled"], r)
    g = Game()
    real = g.__call__
    g.__class__ = type("RefusingGame", (Game,), {"__call__": lambda self, tool, **kw: (
        self.calls.append(tool) or {"success": False, "error": "No PawnKindDef named 'Muffalo'."})
        if tool == "jawa/spawn_pawn" else real(tool, **kw)})
    rc, r = go("T2", g)
    check("a refused spawn names the tool's error in the uncontrolled verdict", rc == 1
          and "No PawnKindDef named" in r["uncontrolled"], r)
    rc, r = go("T1", Game(load_ok=False))
    check("a site that will not load: UNMEASURED", rc == 2 and "did not load" in r["unmeasured"], r)
    rc, r = go("T1", Game(force_pause=True))
    check("a game that stays paused (a dialog): UNMEASURED", rc == 2 and "not unpaused Ultrafast" in r["unmeasured"], r)
    rc, r = go("T1", Game(refuse_speed=True))
    check("a refused Ultrafast: UNMEASURED, never a low PASS", rc == 2 and "speed=Normal" in r["unmeasured"], r)
    rc, r = go("T1", Game(frozen=True))
    check("a clock that did not move: UNMEASURED, never 0 ticks/s", rc == 2 and "did not move" in r["unmeasured"], r)
    # warm-up then window per trial: 6 sleeps, jitter consumed per sleep -> the windows run at 1x, 3x, 1x
    rc, r = go("T1", Game(jitter=[1, 1, 1, 3, 1, 1]))
    check("a 3x trial is over the spread bar: exit 1", rc == 1 and "spread" in r["uncontrolled"], r)
    d = os.path.join("/tmp", "tickrate_selftest_%d" % os.getpid())
    for cell, g in (("T1", Game()), ("T2", Game()), ("T3", Game(mods=40))):
        write(go(cell, g)[1], d)
    m = matrix(d)
    lines = report_lines(m)
    check("matrix: measured cells read, a WRONG_LIST cell and a never-run cell UNMEASURED",
          m["T1"] and m["T2"] and m["T3"] is None and m["T4"] is None, m)
    check("report: UNMEASURED printed, ratios only where both cells exist",
          "UNMEASURED" in lines[3] and "busy/empty: minimal 0." in lines[4] and "full/minimal: empty UNMEASURED" in lines[4],
          lines)
    for p in glob.glob(os.path.join(d, "*.json")):
        os.remove(p)
    os.rmdir(d)
    if fails:
        print(json.dumps(fails, default=str)[:3000])
    print("tickrate_matrix selftest:", "FAIL" if fails else "OK")
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", choices=("run", "report"))
    ap.add_argument("--cell", choices=sorted(CELLS))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--mock", action="store_true", help="the selftest (no bridge)")
    a = ap.parse_args(argv)
    if a.mock or not a.cmd:
        return selftest()
    d = out_dir(a.out_dir)
    if a.cmd == "report":
        print("\n".join(report_lines(matrix(d))))
        return 0
    if not a.cell:
        print("UNMEASURED: run needs --cell")
        return 2
    try:
        import tickburst_bench as TB
        call = TB.real_call()
        reload = TB._site_reloader(call)
    except Exception as e:      # noqa: BLE001
        print("UNMEASURED: bridge unreachable (%s: %s)" % (type(e).__name__, " ".join(str(e).split())[:300]))
        return 2
    rc, res = run_cell(call, a.cell, reload)
    p = write(res, d)
    if rc == 2:
        print("UNMEASURED: %s (%s)" % (res.get("unmeasured"), p))
    elif rc == 1:
        print("FAIL %s: %s (%s)" % (a.cell, res.get("uncontrolled"), p))
    else:
        print("PASS %s %s/%s: %.1f ticks/s mean of %d (spread %.0f%%) (%s)" % (
            a.cell, res["list"], res["map"], res["meanTps"], len(res["trials"]), 100 * res["spread"], p))
    return rc


if __name__ == "__main__":
    sys.exit(main())
