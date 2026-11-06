"""TICKBURST_PROVE_MANY_TICKS_ONE_FRAME: measure jawa/safe_advance (many ticks per frame) against rimworld/step_game_ticks
(one tick per frame) and vanilla's own unpaused loop, then check that three existing proofs give the same verdicts under
each. Design: design/RimMandrake/tickburst_2026-11-06/final.md. Nothing here adopts anything: a proof moves off
step_game_ticks only after its B arm matched R in every trial (final.md §2.3, adoption rule).

Subcommands (each prints one row per criterion, the verdict LAST; exit 0 PASS, 1 FAIL, 2 UNMEASURED with its reason):
  sanity     A1  60 requested ticks move ticksGame by exactly 60 under A, B (40 ms) and C (200 ms); R reaches its target
  throughput A2  ticks/s for A, B40, B100, C, U, U+ (3 repeats, balanced random order, 600-tick warm-up), per-frame tick
                 histogram, p99 / worst frame ms, round trips, UltraSpeedBoost read back -> <out>/<list>/throughput_*.json
  equiv      A6  each proof config under R, A, B, C, `--trials` fixture reloads per arm; resumable (state file in <out>),
                 so a live round that runs out of time exits 2 "trials still owed" and the next round continues;
                 once every trial is in it ADOPTS (acceptance 9): a proof whose B and C matched R in every trial
                 defaults to `gate` (clockgate.advance_chunk) through <out>/equiv/adoption.json, one that did not keeps
                 `step` and gets a filed lesson (first divergent checkpoint, both digests, guard G#); each proof's own
                 selftest is run under its new default. A divergence is the finding (exit 0); a failed adoption exits 1
  sweep      A7  LINES and glowtank-at-dusk at perFrameTickCap {1, 30, 60, 61, max}
  readback   A8  safe_advance reports perFrameTickCap and stepMs, and a cap of 7 is never exceeded in any frame
  --mock         the selftest: every subcommand against an in-memory game (no bridge), plus the pure comparators

Every result row carries provenance: mod-list hash, fixture hash, DLL hashes, arm, N per frame, camera, autosave state.
The fresh-process trial per arm (final.md §2.3) needs a game restart, which a live proof may not do: it is written OWED.
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import tickburst_step as TS  # noqa: E402

BOUNDS = os.path.join(REPO, "design", "RimMandrake", "tickburst_2026-11-06", "bounds.json")
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
MODSCONFIG = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml")
SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"
DLLS = ("BridgeTools/JawaBench/JawaBench.BridgeTools.dll", "Mods/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll")
WARMUP, MEASURE, REPEATS = 600, 20000, 3
SWEEP_CAPS = (1, 30, 60, 61, 0)          # 0 = max (no cap, 200 ms budget)
EQUIV_ARMS = ("R", "A", "B", "C")
ARM_OPTS = {"R": ("play", 40.0, 0), "A": ("step", 40.0, 0), "B": ("safe", 40.0, 0), "C": ("safe", 200.0, 0)}
THROUGHPUT_ARMS = ("A", "B40", "B100", "C", "U", "U+")
UNPAUSED_S = 20.0                        # wall window of an unpaused Ultrafast throughput arm


# ---------------------------------------------------------------- pure helpers (the selftest sweeps these)
def rate(t0, t1, wall_s):
    """ticks/s, or None when either clock read is missing or the clock did not move (a rate off a still clock is a bug)."""
    if t0 is None or t1 is None or wall_s is None or wall_s <= 0 or t1 <= t0:
        return None
    return (t1 - t0) / wall_s


def balanced_order(arms, repeats, seed):
    """`repeats` blocks, each a shuffled copy of `arms` (balanced: every arm once per block)."""
    rng = random.Random(seed)
    out = []
    for _ in range(repeats):
        b = list(arms)
        rng.shuffle(b)
        out.extend(b)
    return out


def flatten(x, pre=""):
    out = {}
    if isinstance(x, dict):
        for k in sorted(x):
            out.update(flatten(x[k], "%s.%s" % (pre, k) if pre else str(k)))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            out.update(flatten(v, "%s[%d]" % (pre, i)))
    else:
        out[pre] = x
    return out


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def load_bounds(path=BOUNDS):
    with open(path, encoding="utf-8") as f:
        b = json.load(f)
    b["_compiled"] = [(re.compile(c["key"]), c) for c in b.get("continuous", [])]
    b["_ignore"] = [re.compile(p) for p in b.get("ignore", [])]
    return b


def classify(key, bounds):
    """-> ('ignore'|'continuous'|'discrete', rule or None). The first matching rule wins; unmatched keys are DISCRETE."""
    if any(p.search(key) for p in bounds["_ignore"]):
        return "ignore", None
    for rx, c in bounds["_compiled"]:
        if rx.search(key):
            return "continuous", c
    return "discrete", None


def within(a, b, rule):
    fa, fb = _num(a), _num(b)
    if fa is None or fb is None:
        return a == b
    if math.isnan(fa) or math.isnan(fb):
        return False
    tol = max(float(rule.get("abs", 0.0)), float(rule.get("rel", 0.0)) * max(abs(fa), abs(fb)))
    return abs(fa - fb) <= tol


def compare(ref, got, bounds):
    """Two checkpoint dicts (flattenable) -> {same, verdictDiffs, discreteDiffs, continuousOut, nan, first}.
    `verdict`-named leaves are verdict diffs; every other key is discrete (exact) unless a bounds rule makes it continuous.
    A NaN anywhere is counted and never 'within'."""
    fr, fg = flatten(ref), flatten(got)
    res = {"verdictDiffs": [], "discreteDiffs": [], "continuousOut": [], "nan": 0, "missing": []}
    for k in sorted(set(fr) | set(fg)):
        for v in (fr.get(k), fg.get(k)):
            if isinstance(v, float) and math.isnan(v):
                res["nan"] += 1
        kind, rule = classify(k, bounds)
        if kind == "ignore":
            continue
        if k not in fr or k not in fg:
            res["missing"].append(k)
            continue
        a, b = fr[k], fg[k]
        if re.search(r"(^|\.)verdict$|(^|\.)status$", k):
            if a != b:
                res["verdictDiffs"].append({"key": k, "ref": a, "got": b})
        elif kind == "continuous":
            if not within(a, b, rule):
                res["continuousOut"].append({"key": k, "ref": a, "got": b, "rule": rule.get("key")})
        elif a != b:
            res["discreteDiffs"].append({"key": k, "ref": a, "got": b})
    diffs = res["verdictDiffs"] + res["discreteDiffs"] + res["continuousOut"] + [{"key": k} for k in res["missing"]]
    res["first"] = sorted(diffs, key=lambda d: d["key"])[0] if diffs else None
    res["same"] = not diffs and res["nan"] == 0
    return res


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def hist_stats(frame_ticks, frame_ms):
    h = {}
    for t in frame_ticks or []:
        h[str(t)] = h.get(str(t), 0) + 1
    ms = sorted(frame_ms or [])

    def pct(p):
        if not ms:
            return None
        return ms[max(0, min(len(ms) - 1, int(math.ceil(p / 100.0 * len(ms))) - 1))]
    return {"ticksPerFrame": dict(sorted(h.items(), key=lambda kv: int(kv[0]))), "p99Ms": pct(99), "maxFrameMs": ms[-1] if ms else None}


def owed_trials(state, configs, arms, trials):
    """(config, arm, trial) still to run, in a balanced order: trial-major, arms in a fixed rotation."""
    done = {(r["config"], r["arm"], r["trial"]) for r in state.get("runs", []) if r.get("complete")}
    out = []
    for t in range(trials):
        for c in configs:
            rot = list(arms[t % len(arms):]) + list(arms[:t % len(arms)])
            out.extend((c, a, t) for a in rot if (c, a, t) not in done)
    return out


def equiv_verdict(runs, configs, arms, trials):
    """-> (exit, rows). Per config: B (and C) vs R in every trial. Any owed trial -> 2."""
    rows, owed, bad = [], 0, 0
    for c in configs:
        by = {}
        for r in runs:
            if r["config"] == c and r.get("complete"):
                by[(r["arm"], r["trial"])] = r
        for a in arms:
            if a == "R":
                continue
            per = []
            for t in range(trials):
                ref, got = by.get(("R", t)), by.get((a, t))
                if ref is None or got is None:
                    owed += 1
                    per.append("owed")
                    continue
                if ref.get("unmeasured") or got.get("unmeasured"):
                    owed += 1
                    per.append("unmeasured")
                    continue
                per.append("same" if got["compare"]["same"] else "diff")
            n_diff = per.count("diff")
            bad += n_diff
            rows.append({"config": c, "arm": a, "trials": per,
                         "verdict": "UNMEASURED" if "owed" in per or "unmeasured" in per else ("PASS" if not n_diff else "DIFF")})
    if owed:
        return 2, rows
    return (0 if not bad else 1), rows


# ---------------------------------------------------------------- provenance
def _sha_file(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()[:16]
    except OSError:
        return None


def modlist_hash(path=MODSCONFIG):
    import xml.etree.ElementTree as ET
    try:
        act = ET.parse(path).getroot().find("activeMods")
        ids = [li.text.strip().lower() for li in act.findall("li") if li.text]
    except (OSError, ET.ParseError, AttributeError):
        return None, None
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()[:16], len(ids)


def provenance(call, arm, n_per_frame, fixture=None, mock=False):
    p = {"arm": arm, "nPerFrame": n_per_frame, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "repoHead": _git_head()}
    if mock:
        p.update(modListHash="mock", modCount=0, fixtureHash="mock", dllHashes={"mock": "mock"}, camera={"mock": True},
                 autosave={"mock": True})
        return p
    p["modListHash"], p["modCount"] = modlist_hash()
    p["fixture"] = fixture
    p["fixtureHash"] = _sha_file(os.path.join(SAVES, fixture + ".rws")) if fixture else None
    p["dllHashes"] = {d: _sha_file(os.path.join(GAME, d)) for d in DLLS}
    cam = call("rimworld/get_camera_state") or {}
    p["camera"] = {k: cam.get(k) for k in ("rootSize", "position", "rootPos", "zoom", "success") if k in cam}
    pr = call("jawa/prefs") or {}
    pv = pr.get("before") or pr.get("after") or pr
    p["autosave"] = {k: pv.get(k) for k in ("autosaveIntervalDays", "autosavesCount") if isinstance(pv, dict)}
    return p


def _git_head():
    try:
        return subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------- the bridge
def real_call():
    import rimbridge_client as rb
    h, p, t = rb.resolve_endpoint()
    S = rb.RimBridge(host=h, port=p, token=t, timeout=600.0)
    S.connect()
    counter = {"n": 0}

    def call(tool, **kw):
        counter["n"] += 1
        r = S.call(tool, kw, check=False) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                return json.loads(r["content"][0]["text"])
            except (ValueError, KeyError, IndexError, TypeError):
                return {"success": False, "raw": str(r)[:300]}
        return r
    call.counter = counter
    return call


class MockGame:
    """An in-memory clock with RimWorld's shape: a frame runs `ms_per_tick` per tick; step_game_ticks steps one tick per
    frame; safe_advance runs NextChunk-sized chunks inside the frame budget (budget read only between chunks); unpaused
    Normal runs 60 ticks/s of wall. `faults`: 'stall_play' (unpause leaves it paused), 'short_safe' (safe_advance runs one
    tick short), 'cap_overshoot' (ignores perFrameTickCap)."""

    def __init__(self, ms_per_tick=0.5, frame_overhead_ms=16.7, faults=()):
        self.t, self.ms, self.ovh, self.f = 1000, ms_per_tick, frame_overhead_ms, set(faults)
        self.wall = 0.0
        self.paused, self.speed, self.usb = True, "Paused", False
        self.calls = 0

    @staticmethod
    def next_chunk(chunk, remaining, cap, done):      # the C# V.NextChunk, line for line
        if chunk < 1 or remaining <= 0:
            return 0
        n = min(chunk, remaining)
        if cap > 0:
            n = min(n, cap - done)
        return n if n > 0 else 0

    def __call__(self, tool, **kw):
        self.calls += 1
        fn = getattr(self, "t_" + tool.replace("/", "_"), None)
        return fn(**kw) if fn else {"success": False, "error": "mock: no tool " + tool}

    def t_jawa_time_clock(self):
        if not self.paused and "stall_play" not in self.f:
            self.t += 1                                   # every read costs a few frames of unpaused play
            self.wall += 1 / 60.0
        return {"success": True, "ticksGame": self.t, "paused": self.paused, "curTimeSpeed": self.speed}

    def t_jawa_time_perf(self):
        return {"success": True, "curTimeSpeed": self.speed, "paused": self.paused, "ultraSpeedBoost": self.usb, "ticksThisFrame": 1}

    def t_rimworld_set_time_speed(self, speed="Normal", ultraSpeedBoost=False):
        self.speed, self.usb = speed, bool(ultraSpeedBoost)
        return {"success": True}

    def t_rimworld_pause_game(self, pause=True):
        self.paused = bool(pause) or "stall_play" in self.f
        return {"success": True}

    def t_rimworld_step_game_ticks(self, ticks=1, pauseFirst=True, timeoutMs=0):
        self.t += int(ticks)
        self.wall += int(ticks) * (self.ovh + self.ms) / 1000.0
        self.frames_last = [1] * int(ticks)
        return {"success": True}

    def t_jawa_safe_advance(self, action="start", ticks=0, chunk=60, frameBudgetMs=40.0, perFrameTickCap=0, timeoutMs=0,
                            frameSamples=False, raw=False, **kw):
        if action == "status":
            return {"success": True, "state": "idle", "ticksGame": self.t}
        if action != "start":
            return {"success": True}
        cap = 0 if "cap_overshoot" in self.f else int(perFrameTickCap)
        left, ft, fm, step_ms = int(ticks) - (1 if "short_safe" in self.f else 0), [], [], 0.0
        while left > 0:
            done, ms = 0, 0.0
            while True:
                if ms >= frameBudgetMs:
                    break
                n = self.next_chunk(chunk, left, cap, done)
                if n <= 0:
                    break
                done += n
                left -= n
                ms += n * self.ms
            ft.append(done)
            fm.append(ms)
            step_ms += ms
            self.wall += (self.ovh + ms) / 1000.0
            if done == 0:
                break
        executed = sum(ft)
        self.t += executed
        st = hist_stats(ft, fm)
        st.update(sampled=len(ft))
        if raw:
            st.update(frameTicks=ft, frameMs=fm)
        return {"success": True, "state": "done", "requested": ticks, "executed": executed, "frames": len(ft),
                "perFrameTickCap": int(perFrameTickCap), "frameBudgetMs": frameBudgetMs, "stepMs": round(step_ms, 3),
                "maxFrameMs": max(fm) if fm else 0.0, "frameStats": st if frameSamples else None, "ticksGame": self.t}

    def t_rimworld_get_camera_state(self):
        return {"success": True, "rootSize": 24}

    def t_jawa_prefs(self):
        return {"success": True, "before": {"autosaveIntervalDays": 1.0, "autosavesCount": 5}}

    def unpaused_window(self, seconds):
        """Mock of an unpaused Ultrafast wall window: 900 ticks/s (9000 with the boost), capped by tick cost."""
        tps = min(9000.0 if self.usb else 900.0, 1000.0 / self.ms)
        self.t += int(tps * seconds)
        self.wall += seconds


# ---------------------------------------------------------------- subcommands
def _rows_print(rows):
    for r in rows:
        print("%-22s %-11s %s" % (r.get("id"), r.get("verdict"), json.dumps({k: v for k, v in r.items() if k not in ("id", "verdict")},
                                                                               default=str)[:400]))


def _wall(call, mock):
    return (lambda: call.__self__.wall) if False else (lambda: call.wall) if mock else time.time


def cmd_sanity(call, mock=False):
    """A1: 60 ticks in A, B, C move ticksGame by exactly 60; R is seen to reach its target."""
    rows = []
    for arm in ("A", "B", "C", "R"):
        mode, budget, cap = ARM_OPTS[arm]
        st = TS.Stepper(call, mode, budget, cap, log_path="", label="sanity")
        if mock and mode == "play":
            TS.PLAY_POLL_S = 0.0
        r = st.advance(60, timeout_ms=120000, why="sanity")
        if mode == "play":
            ok = r["ok"] and (r.get("moved") or 0) >= 60
            rows.append({"id": "A1_" + arm, "verdict": "PASS" if ok else ("UNMEASURED" if r.get("unmeasured") else "FAIL"),
                         "moved": r.get("moved"), "overshoot": r.get("overshoot"), "readback": r.get("readback"),
                         "why": r.get("unmeasured")})
        else:
            rows.append({"id": "A1_" + arm, "verdict": "PASS" if r.get("moved") == 60 else ("UNMEASURED" if r.get("t0") is None else "FAIL"),
                         "moved": r.get("moved"), "frames": r.get("sa_frames"), "stepMs": r.get("sa_stepMs")})
    return rows


def _throughput_arm(call, arm, mock, ticks):
    """-> one measured row for `arm` (A, B40, B100, C, U, U+)."""
    t_read = lambda: TS._ticks(call)  # noqa: E731
    clock = (lambda: call.wall) if mock else time.time
    n0 = getattr(call, "calls", None) if mock else call.counter["n"]
    row = {"arm": arm}
    if arm in ("U", "U+"):
        boost = arm == "U+"
        call("rimworld/set_time_speed", speed="Ultrafast", ultraSpeedBoost=boost)
        perf = call("jawa/time_perf") or {}
        row["ultraSpeedBoost"] = perf.get("ultraSpeedBoost")
        row["ultraSpeedBoostAsked"] = boost
        t0, w0 = t_read(), clock()
        call("rimworld/pause_game", pause=False)
        if mock:
            call.unpaused_window(UNPAUSED_S)
        else:
            time.sleep(UNPAUSED_S)
        perf2 = call("jawa/time_perf") or {}
        t1, w1 = t_read(), clock()
        call("rimworld/pause_game", pause=True)
        call("rimworld/set_time_speed", speed="Normal", ultraSpeedBoost=False)
        row.update(t0=t0, t1=t1, wallS=w1 - w0, curTimeSpeed=perf2.get("curTimeSpeed"), paused=perf2.get("paused"))
        row["tps"] = rate(t0, t1, w1 - w0)
        if row["tps"] is None:
            row["unmeasured"] = "unpaused clock did not move"
    else:
        if arm == "A":
            mode, budget = "step", 40.0
        else:
            mode, budget = "safe", {"B40": 40.0, "B100": 100.0, "C": 200.0}[arm]
        st = TS.Stepper(call, mode, budget, 0, log_path="", label="throughput")
        st.advance(WARMUP, why="warmup")
        perf = call("jawa/time_perf") or {}
        row["ultraSpeedBoost"] = perf.get("ultraSpeedBoost")
        w0 = clock()
        r = st.advance(ticks, timeout_ms=max(600000, ticks * 40), why="measure")
        w1 = clock()
        row.update(t0=r.get("t0"), t1=r.get("t1"), wallS=w1 - w0, moved=r.get("moved"), frames=r.get("sa_frames"),
                   stepMs=r.get("sa_stepMs"))
        if mode == "safe":
            fs = r.get("sa_frameStats") or {}
            row.update(ticksPerFrame=fs.get("ticksPerFrame"), p99Ms=fs.get("p99Ms"), maxFrameMs=fs.get("maxFrameMs"))
        else:
            row.update(ticksPerFrame={"1": ticks}, p99Ms=None, maxFrameMs=None,
                       frameNote="step_game_ticks steps one tick per frame by construction; no in-frame timer")
        row["tps"] = rate(r.get("t0"), r.get("t1"), w1 - w0) if r.get("moved") == ticks else None
        if row["tps"] is None:
            row["unmeasured"] = "clock moved %s of %s" % (r.get("moved"), ticks)
    row["roundTrips"] = (call.calls if mock else call.counter["n"]) - n0
    return row


def cmd_throughput(call, list_name, out_dir, mock=False, ticks=MEASURE, repeats=REPEATS, seed=None, fixture=None,
                   reload=None):
    seed = int(time.time()) if seed is None else seed
    order = balanced_order(THROUGHPUT_ARMS, repeats, seed)
    trials = []
    for i, arm in enumerate(order):
        if reload:
            reload()
        row = _throughput_arm(call, arm, mock, ticks)
        row["trial"] = i
        row["provenance"] = provenance(call, arm, None if arm in ("A", "U", "U+") else "budget", fixture, mock)
        trials.append(row)
    summary = {}
    for arm in THROUGHPUT_ARMS:
        tps = [t["tps"] for t in trials if t["arm"] == arm and t["tps"] is not None]
        summary[arm] = {"n": len(tps), "tps": tps, "meanTps": sum(tps) / len(tps) if tps else None}
    res = {"item": "TICKBURST_PROVE_MANY_TICKS_ONE_FRAME", "list": list_name, "seed": seed, "order": order, "warmup": WARMUP,
           "measureTicks": ticks, "repeats": repeats, "trials": trials, "summary": summary}
    os.makedirs(os.path.join(out_dir, list_name), exist_ok=True)
    path = os.path.join(out_dir, list_name, "throughput_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    rows = []
    for arm in THROUGHPUT_ARMS:
        s = summary[arm]
        rows.append({"id": "A2_" + arm, "verdict": "PASS" if s["n"] == repeats else "UNMEASURED", "meanTps": s["meanTps"],
                     "n": s["n"]})
    usb = [t for t in trials if t.get("ultraSpeedBoost") is None]
    rows.append({"id": "A2_ultraSpeedBoost_read", "verdict": "PASS" if not usb else "UNMEASURED", "unread": len(usb)})
    rows.append({"id": "A2_json", "verdict": "PASS", "path": path})
    return rows, path


# --- equivalence
CONFIGS = {
    "v2": {"argv": [sys.executable, "src/RimMandrake/FlowWorks/northstar/validation_v2.py", "--live"], "out": "--out"},
    "lines": {"argv": [sys.executable, "src/RimMandrake/FlowWorks/northstar/lines_proof.py"], "out": "positional", "site": "calm"},
    "glow_mid": {"argv": [sys.executable, "src/RimMandrake/LuminousPigment/live_probes/lp_glowtank_seed_sow.py"], "out": "--out",
                 "site": "calm", "hour": 12.0},
    "glow_dusk": {"argv": [sys.executable, "src/RimMandrake/LuminousPigment/live_probes/lp_glowtank_seed_sow.py"], "out": "--out",
                  "site": "calm", "hour": 17.5},
}


def checkpoint_of(config, result):
    """The comparable part of a proof's result JSON: per-row verdicts and measured values, or the glowtank state rows."""
    if result is None:
        return None
    if config.startswith("glow"):
        return {"verdict": result.get("verdict"), "route": result.get("route"), "rows": result.get("rows")}
    rows = result.get("rows")
    if isinstance(rows, list):
        return {"rows": {str(r.get("id") or r.get("row") or i): {k: v for k, v in r.items() if k not in ("id", "row")}
                         for i, r in enumerate(rows)}}
    if isinstance(rows, dict):
        return {"rows": rows}
    return {"raw": result}


def _hour_set(call, hour):
    """Put the fixture at `hour` before the proof spawns its pawns: a DECLARED clock jump (jawa/time_set_ticks)."""
    c = call("jawa/time_clock") or {}
    t = c.get("ticksGame")
    if t is None:
        return {"success": False, "why": "ticksGame unreadable"}
    day = 60000
    want = (t // day + 1) * day + int(hour / 24.0 * day)
    return call("jawa/time_set_ticks", ticks=want, timeException=True)


def run_trial(call, config, arm, trial, out_dir, reload=None, mock_runner=None, cap=None):
    cfg = CONFIGS[config]
    mode, budget, cap0 = ARM_OPTS[arm[0]] if arm[0] in ARM_OPTS else ("safe", 200.0, 0)
    cap = cap0 if cap is None else cap
    d = os.path.join(out_dir, "equiv", config)
    os.makedirs(d, exist_ok=True)
    stem = "%s_%s_t%d" % (config, arm, trial)
    out, clog = os.path.join(d, stem + ".json"), os.path.join(d, stem + ".clock.jsonl")
    rec = {"config": config, "arm": arm, "trial": trial, "out": out, "clockLog": clog}
    if reload and cfg.get("site"):
        rec["reload"] = reload(cfg["site"])
    if cfg.get("hour") is not None:
        rec["hourSet"] = _hour_set(call, cfg["hour"])
    if mock_runner:
        result, code = mock_runner(config, mode, budget, cap)
    else:
        argv = list(cfg["argv"]) + (["--out", out] if cfg["out"] == "--out" else [out])
        argv += ["--step", mode, "--step-budget-ms", str(budget), "--step-cap", str(cap)]
        env = dict(os.environ, TICKBURST_STEP_LOG=clog)
        try:
            p = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=3000, stdin=subprocess.DEVNULL)
            code = p.returncode
            with open(os.path.join(d, stem + ".log"), "w", encoding="utf-8") as f:
                f.write(p.stdout[-200000:] + "\n--- stderr\n" + p.stderr[-50000:])
        except subprocess.TimeoutExpired:
            code = None
        try:
            with open(out, encoding="utf-8") as f:
                result = json.load(f)
        except (OSError, ValueError):
            result = None
    rec["exit"] = code
    rec["checkpoint"] = checkpoint_of(config, result)
    rec["digest"] = digest(rec["checkpoint"]) if rec["checkpoint"] is not None else None
    rec["exceptions"] = (result or {}).get("ticking_exceptions") if isinstance(result, dict) else None
    if rec["checkpoint"] is None:
        rec["unmeasured"] = "proof wrote no result (exit %s)" % code
    rec["provenance"] = provenance(call, arm, cap or ("budget %g ms" % budget if mode == "safe" else (1 if mode == "step" else None)),
                                   CONFIGS[config].get("site"), mock_runner is not None)
    rec["complete"] = True
    return rec


def cmd_equiv(call, out_dir, configs, trials, max_s, mock_runner=None, reload=None, bounds=None, lesson_dir=None,
              selftest_runner=None):
    bounds = bounds or load_bounds()
    sp = os.path.join(out_dir, "equiv", "state.json")
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    try:
        with open(sp, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        state = {"runs": []}
    state["boundsHash"] = _sha_file(BOUNDS)
    t0 = time.time()
    for c, a, t in owed_trials(state, configs, EQUIV_ARMS, trials):
        if time.time() - t0 > max_s:
            break
        state["runs"].append(run_trial(call, c, a, t, out_dir, reload, mock_runner))
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=1, default=str)
    by = {(r["config"], r["arm"], r["trial"]): r for r in state["runs"]}
    for r in state["runs"]:
        ref = by.get((r["config"], "R", r["trial"]))
        if r["arm"] != "R" and ref and ref.get("checkpoint") is not None and r.get("checkpoint") is not None:
            r["compare"] = compare(ref["checkpoint"], r["checkpoint"], bounds)
            r["refDigest"] = ref.get("digest")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, default=str)
    code, vrows = equiv_verdict(state["runs"], configs, EQUIV_ARMS, trials)
    rows = [{"id": "A6_%s_%s" % (v["config"], v["arm"]), "verdict": v["verdict"], "trials": v["trials"]} for v in vrows]
    first = []
    for r in state["runs"]:
        if r.get("compare") and not r["compare"]["same"]:
            a_run = by.get((r["config"], "A", r["trial"])) or {}
            a_div = r["arm"] != "A" and bool(a_run.get("compare")) and not a_run["compare"]["same"]
            g, basis = guard_for(r["config"], (r["compare"]["first"] or {}).get("key"), a_div)
            first.append({"run": "%s/%s/t%d" % (r["config"], r["arm"], r["trial"]), "first": r["compare"]["first"],
                          "digest": r.get("digest"), "refDigest": r.get("refDigest"), "guard": g, "guardBasis": basis})
    rows.append({"id": "A6_first_divergences", "verdict": "PASS" if not first else "DIFF", "first": first[:6]})
    rows.append({"id": "A6_fresh_process", "verdict": "OWED", "why": "a fresh-process trial per arm needs a game restart, "
                 "which a live proof may not do (lightspeed-authoring §2); the supervisor's own restart makes trial 0 of a round "
                 "the only fresh-process one"})
    rows.append({"id": "A6_state", "verdict": "PASS", "path": sp, "boundsHash": state["boundsHash"]})
    if code == 2:
        rows.append({"id": "A6_adopt", "verdict": "UNMEASURED", "why": "trials still owed: adoption waits for every trial"})
        return rows, 2
    # acceptance 9: a divergence is the experiment's FINDING, not a failed clause; A6 fails only when the adoption did
    # not take (a matched proof not defaulting to gate, a selftest red, a divergent proof with no filed record)
    arows = cmd_adopt(state, vrows, configs, out_dir, lesson_dir, selftest_runner)
    rows.extend(arows)
    return rows, (1 if any(r["verdict"] == "FAIL" for r in arows) else 0)


# --- adoption (acceptance 9): matched proofs default to the governed path, the rest keep step and get a filed record
PROOF_CONFIGS = {"v2": ("v2",), "lines": ("lines",), "glow": ("glow_mid", "glow_dusk")}
PROOF_SELFTEST = {"v2": ["src/RimMandrake/FlowWorks/northstar/validation_v2.py", "--mock"],
                  "lines": ["src/RimMandrake/FlowWorks/northstar/lines_proof.py", "--mock"],
                  "glow": ["src/RimMandrake/Utils/selftest_tickburst_stepswitch.py"]}   # the probe has no mock of its own
GUARDS = {"G1": "power-net registration per frame", "G2": "region/room rebuild per frame", "G3": "glow grid recompute per frame",
          "G4": "sky glow set per frame", "G5": "world/map component Update", "G6": "path jobs", "G7": "job-loop guard",
          "G8": "Paused true while ticking", "G9": "camera-pinned tick interval rates", "G10": "autosave/long events",
          "G11": "tweener/draw/sound"}
GUARD_KEYS = (("G1", r"power|net|conn|link|cord|hose"), ("G2", r"room|region|roof|pit"), ("G3", r"glow|light|lamp|grow"),
              ("G4", r"sky|sun|dusk|solar|dark"), ("G5", r"goodwill|pollution|dissolution"), ("G7", r"job"),
              ("G10", r"autosave|save|longevent"), ("G11", r"pos|draw|tween|sound"))
CONFIG_GUARD = {"v2": "G2", "lines": "G1", "glow_mid": "G3", "glow_dusk": "G4"}
GUARD_AUDIT = "design/RimMandrake/tickburst_2026-11-06/guard_audit.md"


def guard_for(config, first_key, a_also_diverged):
    """-> (G#, basis). A divergence A shares is paused stepping itself (G8, final.md: filed against the harness); else the
    first divergent key names the guard; else the guard the config was chosen to exercise (final.md §2.4 checks)."""
    if a_also_diverged:
        return "G8", "arm A diverged from R in the same trial: paused stepping, not the burst"
    k = (first_key or "").lower()
    for g, rx in GUARD_KEYS:
        if re.search(rx, k):
            return g, "first divergent key %r matches %s" % (first_key, rx)
    return CONFIG_GUARD.get(config, "G8"), "config %s exercises it (guard_audit.md check column)" % config


def _lesson_marker(proof, rec):
    return "TICKBURST_ADOPT %s %s/%s" % (proof, rec["digest"], rec["refDigest"])


def _find_lesson(lesson_dir, marker):
    try:
        names = sorted(os.listdir(lesson_dir))
    except OSError:
        return None
    for n in names:
        fp = os.path.join(lesson_dir, n)
        try:
            with open(fp, encoding="utf-8") as f:
                if marker in f.read():
                    return fp
        except OSError:
            continue
    return None


def _file_lesson(proof, rec, lesson_dir):
    """One lesson per divergent proof (idempotent on its marker): first divergent checkpoint, both digests, G#."""
    marker = _lesson_marker(proof, rec)
    hit = _find_lesson(lesson_dir, marker)
    if hit:
        return hit
    sys.path.insert(0, HERE)
    import lessons as L  # noqa: E402
    f = rec["first"] or {}
    text = ("TICKBURST_PROVE_MANY_TICKS_ONE_FRAME: proof %s did NOT match unpaused play under safe_advance, so it keeps "
            "rimworld/step_game_ticks (final.md §2.3 adoption rule). First divergent checkpoint: %s in run %s (R=%r, %s=%r). "
            "Digests: R %s, %s %s. Implicates %s (%s): %s. Evidence: %s. [%s]"
            % (proof, f.get("key"), rec["run"], f.get("ref"), rec["arm"], f.get("got"), rec["refDigest"], rec["arm"],
               rec["digest"], rec["guard"], GUARDS.get(rec["guard"], "?"), rec["guardBasis"], rec.get("state"), marker))
    old = L.DIR
    try:
        L.DIR = lesson_dir
        return L.add(text, seat="RELENTLESS", slug="tickburst adopt %s diverges %s" % (proof, rec["guard"]), home=GUARD_AUDIT)
    finally:
        L.DIR = old


def _run_selftest(proof, adoption_file):
    argv = [sys.executable] + list(PROOF_SELFTEST[proof])
    env = dict(os.environ, TICKBURST_ADOPTION=adoption_file, TICKBURST_STEP="")
    try:
        p = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=450, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout[-400:] + p.stderr[-400:]).replace("\n", " | ")
    except subprocess.TimeoutExpired:
        return None, "timeout"


def cmd_adopt(state, vrows, configs, out_dir, lesson_dir=None, selftest_runner=None):
    """A6 tail, run only when every trial is in. Per proof: adopt iff all its configs' B and C rows PASS. Writes
    <out>/equiv/adoption.json, files the divergence lesson, then checks the record took: the proof's default resolves to
    gate (adopted) or step (not), and its own selftest passes under that default. -> rows."""
    lesson_dir = lesson_dir or os.path.join(REPO, "infrastructure", "state", "lessons")
    selftest_runner = selftest_runner or _run_selftest
    path = os.path.join(out_dir, "equiv", "adoption.json")
    sp = os.path.join(out_dir, "equiv", "state.json")
    verdict = {(v["config"], v["arm"]): v["verdict"] for v in vrows}
    by = {(r["config"], r["arm"], r["trial"]): r for r in state["runs"]}
    rec = {"item": "TICKBURST_PROVE_MANY_TICKS_ONE_FRAME", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "state": sp, "boundsHash": state.get("boundsHash"), "proofs": {}}
    for proof, cfgs in PROOF_CONFIGS.items():
        if not all(c in configs for c in cfgs):
            continue
        vs = [verdict.get((c, a)) for c in cfgs for a in ("B", "C")]
        p = {"configs": list(cfgs), "rows": dict(("%s_%s" % (c, a), verdict.get((c, a))) for c in cfgs for a in ("B", "C"))}
        p["adopt"] = all(v == "PASS" for v in vs)
        if not p["adopt"]:
            div = sorted((r for r in state["runs"] if r["config"] in cfgs and r["arm"] in ("B", "C") and r.get("compare")
                          and not r["compare"]["same"]), key=lambda r: (r["trial"], cfgs.index(r["config"]), r["arm"]))
            if div:
                r = div[0]
                a_run = by.get((r["config"], "A", r["trial"])) or {}
                a_div = bool(a_run.get("compare")) and not a_run["compare"]["same"]
                g, basis = guard_for(r["config"], (r["compare"]["first"] or {}).get("key"), a_div)
                d = {"run": "%s/%s/t%d" % (r["config"], r["arm"], r["trial"]), "arm": r["arm"], "first": r["compare"]["first"],
                     "digest": r.get("digest"), "refDigest": r.get("refDigest"), "guard": g, "guardBasis": basis,
                     "aAlsoDiverged": a_div, "state": sp}
                d["lesson"] = _file_lesson(proof, d, lesson_dir)
                p["divergence"] = d
            else:
                p["divergence"] = None          # a non-PASS with no compared divergence: nothing to file, checked below
        rec["proofs"][proof] = p
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, default=str)
    rows = []
    for proof, p in rec["proofs"].items():
        mode, src = TS.adopted_mode(proof, path)
        want = "gate" if p["adopt"] else "step"
        code, tail = selftest_runner(proof, path)
        row = {"id": "A6_adopt_%s" % proof, "adopt": p["adopt"], "defaultMode": mode, "modeSource": src,
               "selftestExit": code, "selftest": " ".join(PROOF_SELFTEST[proof])}
        ok = mode == want and code == 0
        if not p["adopt"]:
            d = p.get("divergence") or {}
            row.update(first=d.get("first"), digest=d.get("digest"), refDigest=d.get("refDigest"), guard=d.get("guard"),
                       lesson=d.get("lesson"))
            ok = ok and bool(d.get("lesson")) and os.path.exists(d["lesson"]) and d.get("guard") in GUARDS \
                and d.get("digest") and d.get("refDigest") and d.get("first")
        if not ok and code != 0:
            row["selftestTail"] = tail
        row["verdict"] = "PASS" if ok else "FAIL"
        rows.append(row)
    rows.append({"id": "A6_adoption_record", "verdict": "PASS", "path": path})
    return rows


def cmd_sweep(call, out_dir, trials, max_s, mock_runner=None, reload=None, bounds=None):
    """A7: LINES and glowtank-at-dusk at perFrameTickCap {1, 30, 60, 61, max}, each compared to cap 1 (the closest to A)."""
    bounds = bounds or load_bounds()
    sp = os.path.join(out_dir, "sweep", "state.json")
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    try:
        with open(sp, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        state = {"runs": []}
    done = {(r["config"], r["cap"]) for r in state["runs"]}
    t0 = time.time()
    for c in ("lines", "glow_dusk"):
        for cap in SWEEP_CAPS:
            if (c, cap) in done or time.time() - t0 > max_s:
                continue
            r = run_trial(call, c, "C" if cap == 0 else "B", 0, os.path.join(out_dir, "sweep"), reload, mock_runner, cap=cap)
            r["cap"] = cap
            state["runs"].append(r)
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=1, default=str)
    rows, owed, diff = [], 0, 0
    for c in ("lines", "glow_dusk"):
        runs = {r["cap"]: r for r in state["runs"] if r["config"] == c}
        ref = runs.get(1)
        for cap in SWEEP_CAPS:
            r = runs.get(cap)
            if r is None or ref is None or r.get("checkpoint") is None or ref.get("checkpoint") is None:
                owed += 1
                rows.append({"id": "A7_%s_cap%s" % (c, cap or "max"), "verdict": "UNMEASURED"})
                continue
            cmpr = compare(ref["checkpoint"], r["checkpoint"], bounds)
            diff += 0 if cmpr["same"] else 1
            rows.append({"id": "A7_%s_cap%s" % (c, cap or "max"), "verdict": "PASS" if cmpr["same"] else "DIFF",
                         "first": cmpr["first"], "digest": r.get("digest")})
    rows.append({"id": "A7_state", "verdict": "PASS", "path": sp})
    # a result that changes with N is a FINDING to file, not a failed sweep: the sweep's own verdict is "recorded"
    return rows, (2 if owed else 0)


def cmd_readback(call, mock=False):
    """A8: the live companion reports perFrameTickCap and stepMs; with cap 7 no frame steps more than 7 ticks."""
    t0 = TS._ticks(call)
    r = call("jawa/safe_advance", ticks=70, chunk=60, frameBudgetMs=200, perFrameTickCap=7, frameSamples=True, raw=True,
             timeoutMs=120000) or {}
    t1 = TS._ticks(call)
    fs = r.get("frameStats") or {}
    ft = fs.get("frameTicks") or []
    rows = [
        {"id": "A8_cap_reported", "verdict": "PASS" if r.get("perFrameTickCap") == 7 else ("UNMEASURED" if not r else "FAIL"),
         "perFrameTickCap": r.get("perFrameTickCap")},
        {"id": "A8_stepMs_reported", "verdict": "PASS" if isinstance(r.get("stepMs"), (int, float)) and r["stepMs"] > 0 else "FAIL",
         "stepMs": r.get("stepMs")},
        {"id": "A8_cap_held", "verdict": "PASS" if ft and max(ft) <= 7 and sum(ft) == 70 else "FAIL",
         "maxTicksInAFrame": max(ft) if ft else None, "sum": sum(ft), "frames": len(ft)},
        {"id": "A8_clock_moved_70", "verdict": "PASS" if t0 is not None and t1 is not None and t1 - t0 == 70 else "FAIL",
         "moved": None if t0 is None or t1 is None else t1 - t0},
    ]
    return rows


def _exit(rows, prefer=None):
    vs = [r["verdict"] for r in rows]
    if prefer is not None:
        code = prefer
    elif "FAIL" in vs:
        code = 1
    elif "UNMEASURED" in vs:
        code = 2
    else:
        code = 0
    _rows_print(rows)
    reason = next((r.get("why") or r["id"] for r in rows if r["verdict"] in ("UNMEASURED",)), "")
    print({0: "PASS", 1: "FAIL", 2: "UNMEASURED: %s" % (reason or "trials still owed")}.get(code, "UNMEASURED: unknown"))
    return code


def out_root(arg):
    if arg:
        return arg
    env = os.environ.get("TICKBURST_OUT")
    if env:
        return env
    helper = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
    p = subprocess.run([sys.executable, helper], capture_output=True, text=True, timeout=30)
    root = p.stdout.strip()
    if p.returncode or not root:
        raise SystemExit("agent storage root unset (agent_storage.py exit %s): pass --out-dir or TICKBURST_OUT" % p.returncode)
    return os.path.join(root, "rimmandrake", "tickburst")


def _site_reloader(call):
    sys.path.insert(0, os.path.join(HERE, "modcheck"))
    import test_site_saves as TSS  # noqa: E402

    def reload(site):
        r = TSS.load_site(call, site)
        return {k: r.get(k) for k in ("verified", "save", "problems", "load_s")}
    return reload


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []

    def check(ok, name, why=""):
        print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
        if not ok:
            fails.append(name)

    # pure: rate, order, compare
    check(rate(0, 600, 2.0) == 300 and rate(5, 5, 1.0) is None and rate(None, 5, 1) is None, "rate_refuses_still_clock")
    o = balanced_order(THROUGHPUT_ARMS, 3, 7)
    check(len(o) == 18 and all(sorted(o[i:i + 6]) == sorted(THROUGHPUT_ARMS) for i in (0, 6, 12)), "order_balanced_blocks")
    b = load_bounds()
    check(classify("rows.P_pits.fluidTotal", b)[0] == "continuous", "bounds_fluid_is_continuous")
    check(classify("rows.P_pits.descentCount", b)[0] == "discrete", "bounds_descent_is_discrete")
    same = compare({"rows": {"x": {"verdict": "PASS", "n": 3, "fluidTotal": 100.0}}},
                   {"rows": {"x": {"verdict": "PASS", "n": 3, "fluidTotal": 100.4}}}, b)
    check(same["same"], "compare_within_bounds_same", str(same))
    d1 = compare({"rows": {"x": {"verdict": "PASS"}}}, {"rows": {"x": {"verdict": "FAIL"}}}, b)
    check(not d1["same"] and d1["verdictDiffs"] and d1["first"]["key"] == "rows.x.verdict", "compare_verdict_diff_first")
    d2 = compare({"rows": {"x": {"n": 3}}}, {"rows": {"x": {"n": 4}}}, b)
    check(not d2["same"] and d2["discreteDiffs"], "compare_discrete_exact")
    d3 = compare({"rows": {"x": {"fluidTotal": 100.0}}}, {"rows": {"x": {"fluidTotal": 140.0}}}, b)
    check(not d3["same"] and d3["continuousOut"], "compare_continuous_out_of_bounds")
    d4 = compare({"rows": {"x": {"fluidTotal": float("nan")}}}, {"rows": {"x": {"fluidTotal": float("nan")}}}, b)
    check(not d4["same"] and d4["nan"] == 2, "compare_nan_never_same")
    d5 = compare({"rows": {"x": {"n": 1}}}, {"rows": {}}, b)
    check(not d5["same"] and d5["missing"], "compare_missing_row_diff")
    # NextChunk mirror: the same sweep as the C# unit (UnitsVitals.cs nextchunk_sweep_exact_total_never_over_cap)
    okc = True
    for ch in (1, 7, 30, 60):
        for cap in (0, 1, 30, 59, 60, 61, 125):
            for rem0 in (1, 59, 60, 61, 600, 1001):
                rem = rem0
                while rem > 0:
                    done, k = 0, 0
                    while k < 3:
                        n = MockGame.next_chunk(ch, rem, cap, done)
                        if n <= 0:
                            break
                        done, rem, k = done + n, rem - n, k + 1
                    if (cap and done > cap) or done == 0:
                        okc = False
                        break
    check(okc, "nextchunk_mirror_sweep")
    # step switch argv
    rest, op = TS.take_args(["x", "--step", "safe", "--step-budget-ms=200", "--step-cap", "61", "--origin", "1,2"])
    check(rest == ["x", "--origin", "1,2"] and op == {"mode": "safe", "modeSource": "--step", "budget_ms": 200.0, "cap": 61}, "take_args_strips", str(op))
    for bad in (["--step", "fast"], ["--step-budget-ms", "500"], ["--step-cap", "-1"], ["--step"]):
        try:
            TS.take_args(bad)
            check(False, "take_args_refuses_" + "_".join(bad))
        except ValueError:
            check(True, "take_args_refuses_" + "_".join(x.strip("-") for x in bad))
    # sanity on the mock game; then faults are seen
    g = MockGame()
    rows = cmd_sanity(g, mock=True)
    check(all(r["verdict"] == "PASS" for r in rows), "sanity_mock_all_pass", str([(r["id"], r["verdict"]) for r in rows]))
    rows = cmd_sanity(MockGame(faults=["short_safe"]), mock=True)
    check([r["verdict"] for r in rows if r["id"] in ("A1_B", "A1_C")] == ["FAIL", "FAIL"], "sanity_short_safe_fails")
    TS.PLAY_STALL_S = 0.05
    rows = cmd_sanity(MockGame(faults=["stall_play"]), mock=True)
    check([r["verdict"] for r in rows if r["id"] == "A1_R"] == ["UNMEASURED"], "sanity_stalled_play_unmeasured")
    TS.PLAY_STALL_S = 5.0
    # readback, and the cap fault caught
    check(all(r["verdict"] == "PASS" for r in cmd_readback(MockGame(), mock=True)), "readback_mock_pass")
    rb = {r["id"]: r["verdict"] for r in cmd_readback(MockGame(faults=["cap_overshoot"]), mock=True)}
    check(rb["A8_cap_held"] == "FAIL", "readback_cap_overshoot_caught")
    # throughput writes a JSON with the required fields
    import tempfile
    tmp = tempfile.mkdtemp(prefix="tickburst_selftest_")
    g = MockGame()
    rows, path = cmd_throughput(g, "minimal", tmp, mock=True, ticks=2000, repeats=3, seed=1)
    res = json.load(open(path))
    s = res["summary"]
    check(all(s[a]["n"] == 3 for a in THROUGHPUT_ARMS), "throughput_three_repeats_each", str({a: s[a]["n"] for a in s}))
    check(s["B40"]["meanTps"] > s["A"]["meanTps"] * 5, "throughput_mock_burst_faster_than_one_per_frame",
          "%s vs %s" % (s["B40"]["meanTps"], s["A"]["meanTps"]))
    t = res["trials"][0]
    need = ("tps", "ticksPerFrame", "p99Ms", "maxFrameMs", "roundTrips", "ultraSpeedBoost", "provenance")
    check(all(all(k in tr for k in need) for tr in res["trials"] if tr["arm"] not in ("U", "U+")) and
          all("ultraSpeedBoost" in tr for tr in res["trials"]), "throughput_rows_have_fields")
    pv = ("modListHash", "fixtureHash", "dllHashes", "arm", "nPerFrame", "camera", "autosave")
    check(all(all(k in tr["provenance"] for k in pv) for tr in res["trials"]), "throughput_rows_carry_provenance")
    uplus = [tr for tr in res["trials"] if tr["arm"] == "U+"]
    check(all(tr["ultraSpeedBoost"] is True for tr in uplus), "throughput_uplus_reads_boost_back")
    # equivalence: identical proofs PASS; a B-only divergence is DIFF with its first checkpoint; resumable
    def runner_same(config, mode, budget, cap):
        return {"verdict": "PASS", "route": "colonist", "rows": {"after": {"fuel": 0, "established": "True"}}}, 0

    def runner_bdiff(config, mode, budget, cap):
        est = "False" if (mode == "safe" and budget < 200) else "True"
        return {"verdict": "PASS" if est == "True" else "FAIL", "rows": {"after": {"established": est}}}, 0
    ran = []

    def st_ok(proof, adoption_file):
        ran.append((proof, TS.adopted_mode(proof, adoption_file)[0]))
        return 0, "mock selftest ok"
    les = os.path.join(tmp, "lessons")
    os.makedirs(les)
    e1 = os.path.join(tmp, "e1")
    rows, code = cmd_equiv(MockGame(), e1, ["lines", "glow_mid", "glow_dusk"], 2, 1e9, mock_runner=runner_same, bounds=b,
                           lesson_dir=les, selftest_runner=st_ok)
    v = {r["id"]: r for r in rows}
    check(code == 0 and all(r["verdict"] in ("PASS", "OWED") for r in rows), "equiv_same_passes", str(code))
    check(v["A6_adopt_lines"]["adopt"] and v["A6_adopt_lines"]["defaultMode"] == "gate" and v["A6_adopt_glow"]["defaultMode"] == "gate"
          and ("lines", "gate") in ran and not os.listdir(les), "adopt_matched_proofs_default_to_gate", str(ran))
    os.environ[TS.ENV_ADOPTION] = os.path.join(e1, "equiv", "adoption.json")
    try:
        check(TS.take_args([], proof="lines")[1]["mode"] == "gate" and TS.take_args([], proof="v2")[1]["mode"] == "step"
              and TS.take_args(["--step", "step"], proof="lines")[1]["mode"] == "step", "take_args_resolves_adoption")
    finally:
        os.environ.pop(TS.ENV_ADOPTION, None)
    e2 = os.path.join(tmp, "e2")
    ran[:] = []
    rows, code = cmd_equiv(MockGame(), e2, ["glow_mid", "glow_dusk"], 2, 1e9, mock_runner=runner_bdiff, bounds=b,
                           lesson_dir=les, selftest_runner=st_ok)
    v = {r["id"]: r for r in rows}
    check(code == 0 and v["A6_glow_mid_B"]["verdict"] == "DIFF" and v["A6_glow_mid_C"]["verdict"] == "PASS"
          and v["A6_first_divergences"]["first"][0]["first"]["key"] in ("rows.after.established", "verdict")
          and v["A6_first_divergences"]["first"][0]["guard"] in GUARDS, "equiv_b_divergence_found", str(v.get("A6_first_divergences")))
    ag = v["A6_adopt_glow"]
    lf = os.listdir(les)
    body = open(os.path.join(les, lf[0])).read() if len(lf) == 1 else ""
    check(ag["verdict"] == "PASS" and not ag["adopt"] and ag["defaultMode"] == "step" and ag["guard"] in GUARDS
          and ag["digest"] and ag["refDigest"] and ag["first"] and len(lf) == 1
          and ag["digest"] in body and ag["refDigest"] in body and ag["guard"] in body and str(ag["first"]["key"]) in body,
          "adopt_divergent_proof_keeps_step_and_files_record", str(ag))
    rows, code = cmd_equiv(MockGame(), e2, ["glow_mid", "glow_dusk"], 2, 1e9, mock_runner=runner_bdiff, bounds=b,
                           lesson_dir=les, selftest_runner=st_ok)
    check(len(os.listdir(les)) == 1, "adopt_lesson_filed_once", str(os.listdir(les)))
    rows, code = cmd_equiv(MockGame(), e2, ["glow_mid", "glow_dusk"], 2, 1e9, mock_runner=runner_bdiff, bounds=b,
                           lesson_dir=les, selftest_runner=lambda p, f: (1, "red"))
    check(code == 1 and {r["id"]: r for r in rows}["A6_adopt_glow"]["verdict"] == "FAIL", "adopt_red_selftest_fails_a6")
    check(guard_for("lines", "rows.L3.powerNet", False)[0] == "G1" and guard_for("glow_dusk", "verdict", False)[0] == "G4"
          and guard_for("v2", "rows.P1.sky", True)[0] == "G8", "guard_for_maps_keys_config_and_paused")
    r = TS.Stepper(MockGame(), "gate", log_path="").advance(3000)
    check(r["ok"] and r["moved"] == 3000 and r["reply"]["path"] == "safe_advance" and r["arm"] == "G", "stepper_gate_via_clockgate",
          str(r.get("reply")))
    e3 = os.path.join(tmp, "e3")
    rows, code = cmd_equiv(MockGame(), e3, ["glow_mid"], 2, -1, mock_runner=runner_same, bounds=b)
    check(code == 2, "equiv_out_of_time_is_unmeasured")
    rows, code = cmd_equiv(MockGame(), e3, ["glow_mid"], 2, 1e9, mock_runner=runner_same, bounds=b, lesson_dir=les,
                           selftest_runner=st_ok)
    st = json.load(open(os.path.join(e3, "equiv", "state.json")))
    check(code == 0 and len(st["runs"]) == 8, "equiv_resumes_without_rerunning", str(len(st["runs"])))
    check(all(all(k in r["provenance"] for k in pv) for r in st["runs"]), "equiv_runs_carry_provenance")
    # sweep: records every cap and flags an N-dependent result
    def runner_n(config, mode, budget, cap):
        return {"verdict": "PASS", "rows": {"after": {"glow": "True" if cap in (1, 30, 60, 61) else "False"}}}, 0
    rows, code = cmd_sweep(MockGame(), os.path.join(tmp, "sw"), 1, 1e9, mock_runner=runner_n, bounds=b)
    v = {r["id"]: r["verdict"] for r in rows}
    check(code == 0 and v["A7_lines_cap61"] == "PASS" and v["A7_lines_capmax"] == "DIFF", "sweep_flags_n_dependence", str(v))
    print("tickburst_bench selftest: %d failed" % len(fails))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", choices=("sanity", "throughput", "equiv", "sweep", "readback"))
    ap.add_argument("--mock", action="store_true", help="run the selftest (no bridge)")
    ap.add_argument("--list", default="minimal", help="minimal | full: names the throughput JSON's folder")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--ticks", type=int, default=MEASURE)
    ap.add_argument("--repeats", type=int, default=REPEATS)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--configs", default="v2,lines,glow_mid,glow_dusk")
    ap.add_argument("--site", default="calm", help="the fixture every throughput trial reloads (test_site_saves.py)")
    ap.add_argument("--no-reload", action="store_true", help="throughput/equiv on the current map, no fixture reloads")
    ap.add_argument("--max-seconds", type=int, default=480, help="wall budget of this round; resumable commands stop here")
    a = ap.parse_args(argv)
    if a.mock or not a.cmd:
        return selftest()
    try:
        call = real_call()
    except Exception as e:  # noqa: BLE001
        print("UNMEASURED: bridge unreachable (%s)" % type(e).__name__)
        return 2
    perf = call("jawa/time_perf") or {}
    if "ultraSpeedBoost" not in perf:
        print("UNMEASURED: companion predates TICKBURST (no ultraSpeedBoost in jawa/time_perf; build.py --gm --apply from this sha)")
        return 2
    out = out_root(a.out_dir)
    rel = None if a.no_reload else _site_reloader(call)
    if a.cmd == "sanity":
        return _exit(cmd_sanity(call))
    if a.cmd == "readback":
        return _exit(cmd_readback(call))
    if a.cmd == "throughput":
        rows, _ = cmd_throughput(call, a.list, out, ticks=a.ticks, repeats=a.repeats, fixture=None if a.no_reload else a.site,
                                 reload=(lambda: rel(a.site)) if rel else None)
        return _exit(rows)
    if a.cmd == "equiv":
        rows, code = cmd_equiv(call, out, [c for c in a.configs.split(",") if c], a.trials, a.max_seconds, reload=rel)
        return _exit(rows, prefer=code)
    rows, code = cmd_sweep(call, out, 1, a.max_seconds, reload=rel)
    return _exit(rows, prefer=code)


if __name__ == "__main__":
    sys.exit(main())
