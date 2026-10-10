#!/usr/bin/env python3
r"""tps_record.py - read the JawaBench TPS record (BRIDGE_TPS_REGULAR_REPORT_1, BRIDGE_TPS_CAPTURE_FIXES_1).

    python3 src/RimMandrake/Utils/tps_record.py                                   verdict over the last 5 minutes
    python3 src/RimMandrake/Utils/tps_record.py --at "yesterday 15:00"            timeline 10 min either side
    python3 src/RimMandrake/Utils/tps_record.py --at "2026-10-09 21:30" --span 30m --tz America/Los_Angeles
    python3 src/RimMandrake/Utils/tps_record.py --since "today 09:00" --until "today 12:00"
    python3 src/RimMandrake/Utils/tps_record.py --sessions                         list game sessions on disk
    python3 src/RimMandrake/Utils/tps_record.py --session 3f2a --since ...         one session only
    python3 src/RimMandrake/Utils/tps_record.py --json

The JawaBench companion starts the sampler when RimBridgeServer registers it (game load, no
bridge call needed) and writes ordered JSON lines - windows, incidents, lifecycle events,
attribution - through one bounded writer thread into session-named segments

    C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\tps_<start>_<session>_<pid>_<seg>.jsonl

(>= 7 days kept, byte-capped; outside git). Times given without a zone are read in --tz (default
America/Los_Angeles, the owner's zone); the record itself is UTC. The window maths is a PORT of
src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsMath.cs; selftest_tps_record.py holds
the two to the same answers. Doc: design/RimMandrake/tps_record.md.

🔑 Judge `ratio` (ticks / expected ticks, expected integrated frame by frame at the effective
multiplier over UNPAUSED time), never tps against 60. Only `state: run` windows are judged;
`paused`, `mixed`, `stall` and `longevent` windows are recorded, and stalls are incidents.
🔑 A hole in the record is COVERAGE (no sampler, game down, writer failing), never "TPS was fine";
the verdict says STALE/MISSING/ERROR separately from any performance WARN.
"""
import argparse
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# ---- constants: MUST equal JawaBenchTpsMath.cs (selftest_tps_record.py parses and compares) ----
CADENCE_SECONDS = 5.0
GAP_SECONDS = 2.0
EXPLAINED_SHARE = 0.8
TICKS_PER_SECOND_AT_SPEED1 = 60.0
PAUSED_SHARE = 0.5
STALL_SHARE = 0.5
LONG_EVENT_SHARE = 0.5
MIXED_SHARE = 0.25
FRAME_BUDGET_SECONDS = 0.045454544
MAX_GAPS_PER_WINDOW = 8
SEGMENT_BYTES = 2 * 1024 * 1024
RETENTION_DAYS = 7.0
RETENTION_BYTES = 256 * 1024 * 1024
LOG_RETENTION_BYTES = 1024 * 1024 * 1024
QUEUE_CAPACITY = 4096
SILENCE_SECONDS = 10.0
SILENCE_REPEAT_SECONDS = 30.0
RING_CAPACITY = 720
SUSTAINED_SAMPLES = 6
LOW_RATIO = 0.6
HIGH_RATIO = 1.15

STATE_RUN, STATE_PAUSED, STATE_MIXED, STATE_STALL, STATE_LONGEVENT = "run", "paused", "mixed", "stall", "longevent"

STALE_SECONDS = 60      # newest sample older than this = coverage is STALE (not a performance verdict)


def round_away(v, places):
    """Mirror of .NET Math.Round(double, places, MidpointRounding.AwayFromZero)."""
    p = 10.0 ** places
    x = v * p
    x = math.trunc(x + math.copysign(0.49999999999999994, x))
    return x / p


def F(v, places):
    """Mirror of JawaBenchTpsMath.F: round away from zero, then up to 4 decimals, trailing zeros trimmed."""
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "null"
    s = "%.4f" % round_away(float(v), places)
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Window:
    """Port of JawaBenchTpsMath.Window."""
    def __init__(self):
        self.dReal = self.runS = self.pausedS = self.explainedS = self.stallS = self.ambigS = 0.0
        self.expected = self.gapMaxS = self.simS = self.simMaxS = 0.0
        self.dTicks = self.frames = self.pausedFrames = self.transitions = 0
        self.capFrames = self.budgetFrames = self.gapsDropped = 0
        self.multMin, self.multMax, self.multEnd = float("inf"), float("-inf"), 0.0
        self.pausedEnd = False
        self.gaps = []

    tps = property(lambda s: s.dTicks / s.runS if s.runS > 0 else 0.0)
    tpsWall = property(lambda s: s.dTicks / s.dReal if s.dReal > 0 else 0.0)
    target = property(lambda s: s.expected / s.runS if s.runS > 0 else 0.0)
    ratio = property(lambda s: s.dTicks / s.expected if s.expected > 0 else None)
    pausedFrac = property(lambda s: s.pausedS / s.dReal if s.dReal > 0 else 0.0)
    simShare = property(lambda s: s.simS / s.dReal if s.dReal > 0 else 0.0)

    @property
    def state(self):
        if self.dReal <= 0:
            return STATE_PAUSED
        if self.explainedS >= LONG_EVENT_SHARE * self.dReal:
            return STATE_LONGEVENT
        if self.stallS >= STALL_SHARE * self.dReal:
            return STATE_STALL
        if self.pausedS >= PAUSED_SHARE * self.dReal or self.expected <= 0:
            return STATE_PAUSED
        if self.ambigS >= MIXED_SHARE * self.runS:
            return STATE_MIXED
        return STATE_RUN


def gap_kind(g):
    return STATE_LONGEVENT if g["explained"] >= EXPLAINED_SHARE * g["seconds"] else STATE_STALL


class FrameAccumulator:
    """Port of JawaBenchTpsMath.FrameAccumulator (see the C# for the semantics)."""
    def __init__(self):
        self.open = False
        self._w = Window()

    def pre(self, now, paused, mult, ticks_before, explained):
        self._ticks_pre, self._paused_pre, self._mult_pre, self._last_run_dt = ticks_before, paused, mult, 0.0
        if not self.open:
            self.open, self._need_tick0 = True, True
            self._t_prev = self._t0 = now
            self._paused_prev, self._mult_prev = paused, mult
            self._w = Window()
            return None
        dt = max(0.0, now - self._t_prev)
        ex = 0.0 if explained < 0 else min(explained, dt)
        r = dt - ex
        transition = paused != self._paused_prev or (not paused and not self._paused_prev and mult != self._mult_prev)
        gap = dt > GAP_SECONDS
        w = self._w
        w.frames += 1
        w.dReal += dt
        w.explainedS += ex
        w.gapMaxS = max(w.gapMaxS, dt)
        if transition:
            w.transitions += 1
        if gap:
            w.stallS += r
        if gap and transition:
            w.ambigS += r
        elif paused:
            w.pausedS += r
            w.pausedFrames += 1
        else:
            w.runS += r
            w.expected += TICKS_PER_SECOND_AT_SPEED1 * mult * r
            self._last_run_dt = r
            w.multMin, w.multMax = min(w.multMin, mult), max(w.multMax, mult)
        g = None
        if gap:
            g = {"start": self._t_prev, "seconds": dt, "explained": ex, "paused": paused, "mult": mult,
                 "ambiguous": transition}
            if len(w.gaps) < MAX_GAPS_PER_WINDOW:
                w.gaps.append(g)
            else:
                w.gapsDropped += 1
        self._t_prev, self._paused_prev, self._mult_prev = now, paused, mult
        return g

    def post(self, mult_after, ticks_after, sim_seconds):
        if not self.open:
            return None
        if self._need_tick0:
            self._need_tick0, self._tick0 = False, ticks_after
            return None
        w = self._w
        w.simS += sim_seconds
        w.simMaxS = max(w.simMaxS, sim_seconds)
        if not self._paused_pre:
            done = ticks_after - self._ticks_pre
            if self._mult_pre > 0 and done >= 2 * self._mult_pre:
                w.capFrames += 1
            if sim_seconds > FRAME_BUDGET_SECONDS:
                w.budgetFrames += 1
            if mult_after != self._mult_pre:
                w.ambigS += self._last_run_dt
                w.transitions += 1
        self._mult_prev = mult_after
        if self._t_prev - self._t0 < CADENCE_SECONDS:
            return None
        w.dTicks = max(0, ticks_after - self._tick0)
        w.multEnd, w.pausedEnd = mult_after, self._paused_pre
        if w.multMin == float("inf"):
            w.multMin = w.multMax = 0.0
        self._t0, self._tick0 = self._t_prev, ticks_after
        self._w = Window()
        return w


def window_fields(w):
    """Port of JawaBenchTpsMath.WindowFields (the JSON fields, no braces)."""
    fps = w.frames / w.dReal if w.dReal > 0 else 0.0
    parts = [('"state":"%s"' % w.state), '"dReal":' + F(w.dReal, 3), '"dTicks":%d' % w.dTicks,
             '"ratio":' + F(w.ratio, 3), '"tps":' + F(w.tps, 2), '"tpsWall":' + F(w.tpsWall, 2),
             '"target":' + F(w.target, 2), '"expected":' + F(w.expected, 1), '"runS":' + F(w.runS, 3),
             '"pausedS":' + F(w.pausedS, 3), '"explainedS":' + F(w.explainedS, 3), '"stallS":' + F(w.stallS, 3),
             '"ambigS":' + F(w.ambigS, 3), '"pausedFrac":' + F(w.pausedFrac, 3), '"multMin":' + F(w.multMin, 2),
             '"multMax":' + F(w.multMax, 2), '"mult":' + F(w.multEnd, 2), '"transitions":%d' % w.transitions,
             '"frames":%d' % w.frames, '"fps":' + F(fps, 1), '"gapMaxMs":' + F(w.gapMaxS * 1000.0, 1),
             '"gaps":%d' % (len(w.gaps) + w.gapsDropped), '"simMs":' + F(w.simS * 1000.0, 1),
             '"simMaxMs":' + F(w.simMaxS * 1000.0, 1), '"simShare":' + F(w.simShare, 3),
             '"capFrames":%d' % w.capFrames, '"budgetFrames":%d' % w.budgetFrames]
    return ",".join(parts)


def gap_fields(g):
    """Port of JawaBenchTpsMath.GapFields."""
    return ('"gapS":%s,"explainedS":%s,"unexplainedS":%s,"pausedAfter":%s,"mult":%s,"ambiguous":%s' % (
        F(g["seconds"], 3), F(g["explained"], 3), F(g["seconds"] - g["explained"], 3),
        "true" if g["paused"] else "false", F(g["mult"], 2), "true" if g["ambiguous"] else "false"))


def should_rotate(current_bytes, line_bytes):
    return current_bytes > 0 and current_bytes + line_bytes > SEGMENT_BYTES


def segment_name(start_epoch, session, pid, segment):
    return "tps_%s_%s_%d_%03d.jsonl" % (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(start_epoch)), session, pid, segment)


def plan_retention(sizes, age_days, current, cap_bytes):
    """Port of JawaBenchTpsMath.PlanRetention: indices to delete, oldest first; never a current file."""
    order = sorted(range(len(sizes)), key=lambda i: (-age_days[i], i))
    total = sum(sizes)
    out = []
    for i in order:
        if current[i]:
            continue
        if age_days[i] > RETENTION_DAYS or total > cap_bytes:
            out.append(i)
            total -= sizes[i]
    return out


def median(xs):
    a = sorted(xs)
    n = len(a)
    if n == 0:
        return None
    return a[n // 2] if n % 2 else (a[n // 2 - 1] + a[n // 2]) / 2.0


def sustained(run_ratios):
    """Port of JawaBenchTpsMath.Sustained: low/high/ok/unknown over the last SUSTAINED_SAMPLES."""
    if len(run_ratios) < SUSTAINED_SAMPLES:
        return "unknown"
    tail = run_ratios[-SUSTAINED_SAMPLES:]
    if all(r < LOW_RATIO for r in tail):
        return "low"
    if all(r > HIGH_RATIO for r in tail):
        return "high"
    return "ok"


# ---------------------------------------------------------------- the record on disk

DEFAULT_TZ = os.environ.get("TPS_TZ", "America/Los_Angeles")
FUTURE_SLACK_SECONDS = 120
SEGMENT_RE = re.compile(r"^tps_(\d{8}T\d{6}Z)_([0-9a-f]+)_(\d+)_(\d{3})\.jsonl$")
LEGACY = ("tps.1.jsonl", "tps.jsonl", "observer.jsonl")   # observer.jsonl: belt_watchdog's external findings
_open = open   # selftest swaps this to simulate a segment vanishing mid-read


def record_dir():
    try:
        from game_paths import PLAYER_LOG
        base = os.path.dirname(PLAYER_LOG)
    except Exception:                                           # noqa: BLE001
        base = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
    return os.path.join(base, "JawaBench", "tps")


def list_files(d):
    """Segment files sorted by name (= start time, session, segment), legacy files first."""
    try:
        names = os.listdir(d)
    except OSError:
        return []
    segs = sorted(n for n in names if SEGMENT_RE.match(n))
    return [os.path.join(d, n) for n in LEGACY if n in names] + [os.path.join(d, n) for n in segs]


def _epoch(utc):
    try:
        return datetime.strptime(utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except (TypeError, ValueError):
        try:
            return datetime.strptime(utc, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()
        except (TypeError, ValueError):
            return None


def _valid(r):
    """A row we can place on the timeline. Legacy rows (no `kind`) are samples."""
    if not isinstance(r, dict) or _epoch(r.get("utc")) is None:
        return False
    k = r.setdefault("kind", "sample")
    if k == "sample":
        if not isinstance(r.get("state"), str):
            return False
        for f in ("ratio", "tps", "dReal"):
            if r.get(f) is not None and not isinstance(r.get(f), (int, float)):
                return False
    return True


def read_record(directory=None, now=None):
    """Every valid row, ordered by session (in start order) then seq. Bad rows are COUNTED, never silently
    dropped: malformed (not JSON, incl. a torn last line), invalid (JSON but unplaceable), future (utc more
    than FUTURE_SLACK_SECONDS ahead of now), vanished (a segment deleted between listing and opening)."""
    d = directory or record_dir()
    now = time.time() if now is None else now
    out = {"dir": d, "rows": [], "malformed": 0, "invalid": 0, "future": 0, "vanished": 0, "files": 0}
    order = 0
    for p in list_files(d):
        try:
            fh = _open(p, encoding="utf-8", errors="replace")
        except FileNotFoundError:
            out["vanished"] += 1
            continue
        except OSError:
            out["vanished"] += 1
            continue
        out["files"] += 1
        with fh:
            for ln in fh:
                if not ln.endswith("\n"):          # a line the writer has not finished: never parse half a row
                    out["malformed"] += 1
                    continue
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except ValueError:
                    out["malformed"] += 1
                    continue
                if not _valid(r):
                    out["invalid"] += 1
                    continue
                ep = _epoch(r["utc"])
                if ep > now + FUTURE_SLACK_SECONDS:
                    out["future"] += 1
                    continue
                r["_t"] = ep
                r["_o"] = order
                order += 1
                out["rows"].append(r)
    first = {}
    for r in out["rows"]:
        s = r.get("session") or "?"
        first[s] = min(first.get(s, r["_t"]), r["_t"])
    # within a session: the writer's seq order; rows without seq (legacy, observer) by time, after them
    out["rows"].sort(key=lambda r: (first[r.get("session") or "?"], r.get("session") or "?",
                                    0 if isinstance(r.get("seq"), int) else 1,
                                    r["seq"] if isinstance(r.get("seq"), int) else r["_t"], r["_o"]))
    return out


def read_samples(directory=None):
    """Back-compat: (rows, bad) for callers that only want rows."""
    rec = read_record(directory)
    return rec["rows"], rec["malformed"] + rec["invalid"]


def read_heartbeats(directory=None):
    """The watchdog thread's hb_<session>.json files: [{...,'_path','_mtime'}], newest first."""
    d = directory or record_dir()
    out = []
    try:
        names = [n for n in os.listdir(d) if n.startswith("hb_") and n.endswith(".json")]
    except OSError:
        return out
    for n in names:
        p = os.path.join(d, n)
        try:
            with _open(p, encoding="utf-8") as fh:
                hb = json.load(fh)
            hb["_path"], hb["_mtime"] = p, os.path.getmtime(p)
            out.append(hb)
        except (OSError, ValueError):
            continue
    out.sort(key=lambda h: h["_mtime"], reverse=True)
    return out


# ---------------------------------------------------------------- the external observer (belt_watchdog)

HB_FRESH_SECONDS = 15   # the watchdog thread rewrites hb_<session>.json every 5 s


def observe(rows, hbs, game_pid, now=None):
    """What an observer OUTSIDE the game process can see that the process cannot say about itself.
    rows: read_record rows; hbs: read_heartbeats(); game_pid: the running RimWorldWin64 pid or None.
    Returns findings [{finding, session, pid, hbAgeS, silentS, phase, level, detail}], newest session first:
      silent                 heartbeat fresh, main thread silent > SILENCE_SECONDS (hung or very long frame)
      frozen                 the game pid is running but hb_ stopped changing: the watchdog thread is stopped
                             too (stop-the-world GC, native hang, debugger) - only visible from outside
      exited-without-shutdown hb_ is old, that pid is not running, and the session wrote no `shutdown` line
                             (crash, kill, power) - its record ends at the last heartbeat
    A cleanly shut down session yields nothing."""
    now = time.time() if now is None else now
    ended = {r.get("session") for r in rows if r.get("kind") == "shutdown"}
    reported = {(r.get("session"), r.get("finding")) for r in rows if r.get("kind") == "observer"}
    out = []
    for hb in hbs:
        sess, pid = hb.get("session"), hb.get("pid")
        age = now - hb["_mtime"]
        silent = float(hb.get("silentS") or 0)
        base = {"session": sess, "pid": pid, "hbAgeS": round(age, 1), "silentS": silent, "phase": hb.get("phase"),
                "lastHeartbeatUtc": hb.get("utc")}
        if age <= HB_FRESH_SECONDS:
            if silent > SILENCE_SECONDS:
                out.append(dict(base, finding="silent", level="WARN",
                                detail="main thread silent %.0fs in phase %s (pid %s)" % (silent, hb.get("phase"), pid)))
        elif game_pid is not None and pid == game_pid:
            out.append(dict(base, finding="frozen", level="WARN",
                            detail="pid %s is running but its heartbeat thread stopped %.0fs ago (phase %s): whole "
                                   "process frozen (GC / native hang)" % (pid, age, hb.get("phase"))))
        elif sess not in ended:
            f = dict(base, finding="exited-without-shutdown", level="INFO",
                     detail="session %s (pid %s) ended WITHOUT a shutdown line - crash or kill; its record ends at "
                            "the last heartbeat %s, phase %s" % ((sess or "?")[:8], pid, hb.get("utc"), hb.get("phase")))
            f["new"] = (sess, "exited-without-shutdown") not in reported
            out.append(f)
    return out


def record_observation(finding, directory=None):
    """Append one observer finding to observer.jsonl in the record dir (read back by read_record)."""
    d = directory or record_dir()
    row = {"kind": "observer", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           **{k: v for k, v in finding.items() if k not in ("level", "new")}}
    with open(os.path.join(d, "observer.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------- time arguments

def _tz(name):
    import zoneinfo
    return zoneinfo.ZoneInfo(name or DEFAULT_TZ)


def parse_when(s, tz=None, now=None):
    """Epoch seconds for "2026-10-09 15:00[:SS]" / "yesterday 15:00" / "today 9:30" / "15:00" (local in tz),
    an ISO time with Z or an offset, or a bare epoch number."""
    s = s.strip()
    z = _tz(tz)
    if re.fullmatch(r"\d{9,11}(\.\d+)?", s):
        return float(s)
    m = re.fullmatch(r"(?:(today|yesterday)\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?", s, re.I)
    if m:
        base = datetime.fromtimestamp(time.time() if now is None else now, z).date()
        if (m.group(1) or "").lower() == "yesterday":
            base -= timedelta(days=1)
        dt = datetime(base.year, base.month, base.day, int(m.group(2)), int(m.group(3)), int(m.group(4) or 0), tzinfo=z)
        return dt.timestamp()
    iso = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        raise ValueError("cannot read time %r (try '2026-10-09 15:00', 'yesterday 15:00' or an ISO time)" % s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=z)
    return dt.timestamp()


def parse_span(s):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([smhd]?)", s.strip())
    if not m:
        raise ValueError("cannot read span %r (e.g. 10m, 90s, 2h)" % s)
    return float(m.group(1)) * {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]


# ---------------------------------------------------------------- judgement

def _samples(rows):
    return [r for r in rows if r.get("kind") == "sample"]


def contiguous(prev, cur):
    """cur directly follows prev: same session and no hole longer than one cadence beyond cur's own window."""
    if prev is None or (prev.get("session") or "?") != (cur.get("session") or "?"):
        return False
    d_real = cur.get("dReal") if isinstance(cur.get("dReal"), (int, float)) else CADENCE_SECONDS
    return 0 <= cur["_t"] - prev["_t"] <= d_real + CADENCE_SECONDS


def sustained_from_rows(rows):
    """Sustained over the trailing UNBROKEN streak of run windows (a non-run window, a new session or a
    coverage hole starts the streak again)."""
    streak, prev = [], None
    for r in _samples(rows):
        r.setdefault("_t", _epoch(r.get("utc")) or 0)
        if not contiguous(prev, r):
            streak = []
        if r.get("state") == STATE_RUN and isinstance(r.get("ratio"), (int, float)):
            streak.append(float(r["ratio"]))
        else:
            streak = []
        prev = r
    return sustained(streak)


def by_target(samples):
    out = {}
    for s in samples:
        if s.get("state") != STATE_RUN or not isinstance(s.get("ratio"), (int, float)):
            continue
        k = "%.0f" % float(s.get("target") or 0)
        out.setdefault(k, {"n": 0, "tps": [], "ratio": []})
        out[k]["n"] += 1
        out[k]["tps"].append(float(s.get("tps") or 0))
        out[k]["ratio"].append(float(s["ratio"]))
    return {k: {"n": v["n"], "tpsMedian": median(v["tps"]), "ratioMedian": median(v["ratio"]),
                "ratioMin": min(v["ratio"])} for k, v in out.items()}


def summarise(rows, now=None, window_s=300, writer=None):
    """Coverage and performance over the last window_s. Pure: selftested on fixtures."""
    now = time.time() if now is None else now
    for r in rows:
        r.setdefault("_t", _epoch(r.get("utc")) or 0)
    samples = _samples(rows)
    recent = [s for s in samples if s["_t"] >= now - window_s]
    newest = max((s["_t"] for s in samples), default=None)
    run = [s for s in recent if s.get("state") == STATE_RUN and isinstance(s.get("ratio"), (int, float))]
    ratios = [float(s["ratio"]) for s in run]
    last = samples[-1] if samples else {}
    w = dict(writer or {})
    for k in ("werr", "wdrop"):
        if k not in w and isinstance(last.get(k), (int, float)):
            w[k] = last[k]
    if newest is None:
        coverage = "MISSING"
    elif now - newest > STALE_SECONDS:
        coverage = "STALE"
    else:
        coverage = "FRESH"
    states = {}
    for s in recent:
        states[s.get("state")] = states.get(s.get("state"), 0) + 1
    return {
        "coverage": coverage,
        "writer": w,
        "samples": len(recent),
        "run": len(run),
        "states": states,
        "incidents": sum(1 for r in rows if r.get("kind") == "incident" and r["_t"] >= now - window_s),
        "newestAgeS": (now - newest) if newest is not None else None,
        "ratioMedian": median(ratios),
        "ratioMin": min(ratios) if ratios else None,
        "byTarget": by_target(recent),
        "speed": recent[-1].get("speed") if recent else None,
        "gapMaxMs": max((float(s.get("gapMaxMs") or s.get("frameMaxMs") or 0) for s in recent), default=None),
        "sustained": sustained_from_rows([s for s in samples if s["_t"] >= now - window_s]),
    }


def verdict(summary):
    """(level, detail) for belt_watchdog. COVERAGE (MISSING/STALE/ERROR) is reported apart from
    PERFORMANCE (SUSTAINED LOW/HIGH); a stale record never yields a performance WARN, and the line never
    escalates the watchdog's overall verdict. Levels: OK / INFO / WARN / UNKNOWN."""
    s = summary
    werr = (s.get("writer") or {}).get("werr") or 0
    err = ""
    if werr:
        err = "; coverage ERROR: writer reported %d write errors%s" % (
            werr, (" (%s)" % s["writer"]["lastError"]) if s["writer"].get("lastError") else "")
    if s["coverage"] == "MISSING":
        return "UNKNOWN", "coverage MISSING: no TPS record on disk (sampler never started, or the companion " \
                          "is not deployed)" + err
    if s["coverage"] == "STALE":
        return "INFO", "coverage STALE: newest window %ds ago (game down, at the menu, or the sampler stopped) - " \
                       "not a performance verdict%s" % (s["newestAgeS"], err)
    if not s["run"]:
        return "INFO", "%d windows in 5m, none judged (%s)%s" % (
            s["samples"], ", ".join("%s %d" % kv for kv in sorted(s["states"].items(), key=str)), err)
    tg = ", ".join("target %s: tps %.0f ratio %.2f (n %d)" % (k, v["tpsMedian"], v["ratioMedian"], v["n"])
                   for k, v in sorted(s["byTarget"].items(), key=lambda kv: float(kv[0])))
    body = "ratio median %.2f (min %.2f) over %d run windows; %s; %d incidents; gapMax %.0fms%s" % (
        s["ratioMedian"], s["ratioMin"], s["run"], tg, s["incidents"], s["gapMaxMs"] or 0, err)
    if s["sustained"] == "low":
        return "WARN", "SUSTAINED LOW TPS (<%.0f%% of target for %d contiguous windows): %s" % (
            LOW_RATIO * 100, SUSTAINED_SAMPLES, body)
    if s["sustained"] == "high":
        return "WARN", "SUSTAINED HIGH TPS (>%.0f%% of target for %d contiguous windows): %s" % (
            HIGH_RATIO * 100, SUSTAINED_SAMPLES, body)
    return "OK", body


# ---------------------------------------------------------------- timelines

def sessions(rows):
    out = {}
    for r in rows:
        s = r.get("session") or "?"
        e = out.setdefault(s, {"session": s, "first": r["_t"], "last": r["_t"], "samples": 0, "incidents": 0,
                               "pid": None, "events": []})
        e["first"], e["last"] = min(e["first"], r["_t"]), max(e["last"], r["_t"])
        k = r.get("kind")
        if k == "sample":
            e["samples"] += 1
        elif k == "incident":
            e["incidents"] += 1
        elif k in ("session", "shutdown", "game", "menu", "error", "silence"):
            e["events"].append(k)
        if r.get("pid"):
            e["pid"] = r["pid"]
    return sorted(out.values(), key=lambda e: e["first"])


def select_session(rows, prefix):
    if not prefix:
        return rows
    return [r for r in rows if (r.get("session") or "").startswith(prefix)]


def timeline(rows, t0, t1):
    """Rows in [t0, t1] (a window counts if it overlaps), coverage holes, incidents, per-target ratios."""
    sel = []
    for r in rows:
        start = r["_t"] - (float(r.get("dReal") or 0) if r.get("kind") == "sample" else 0)
        if r["_t"] >= t0 and start <= t1:
            sel.append(r)
    holes, prev = [], None
    for r in _samples(sel):
        if prev is not None and not contiguous(prev, r):
            holes.append({"from": prev["_t"], "to": r["_t"] - float(r.get("dReal") or 0),
                          "sameSession": (prev.get("session") == r.get("session"))})
        prev = r
    ss = _samples(sel)
    if not ss:
        holes.append({"from": t0, "to": t1, "sameSession": False})
    else:
        if ss[0]["_t"] - float(ss[0].get("dReal") or 0) > t0 + CADENCE_SECONDS:
            holes.insert(0, {"from": t0, "to": ss[0]["_t"] - float(ss[0].get("dReal") or 0), "sameSession": False})
        if ss[-1]["_t"] < t1 - 2 * CADENCE_SECONDS:
            holes.append({"from": ss[-1]["_t"], "to": t1, "sameSession": False})
    return {"from": t0, "to": t1, "rows": sel, "holes": holes,
            "incidents": sum(1 for r in sel if r.get("kind") in ("incident", "silence")),
            "byTarget": by_target(ss), "sustained": sustained_from_rows(sel),
            "states": {k: sum(1 for s in ss if s.get("state") == k) for k in sorted({s.get("state") for s in ss})}}


def _local(ep, tz):
    return datetime.fromtimestamp(ep, _tz(tz)).strftime("%Y-%m-%d %H:%M:%S")


def render_row(r, tz):
    t = _local(r["_t"], tz)
    k = r.get("kind")
    if k == "sample":
        return "%s  %-9s %-9s ratio %-6s tps %-7s wall %-7s target %-5s fps %-5s sim %-5s gapMax %sms%s" % (
            t, r.get("state"), r.get("speed"), r.get("ratio"), r.get("tps"), r.get("tpsWall", r.get("tps")),
            r.get("target"), r.get("fps"), r.get("simShare", "-"), r.get("gapMaxMs", r.get("frameMaxMs")),
            ("  top " + r["top"]) if r.get("top") else "")
    if k == "incident":
        return "%s  INCIDENT %-9s %ss (unexplained %ss) phase %s speed %s mult %s heap %s" % (
            t, r.get("type") or r.get("kindDetail") or r.get("gapKind"), r.get("gapS"), r.get("unexplainedS"),
            r.get("phase"), r.get("speed"), r.get("mult"), r.get("heapMB"))
    if k == "silence":
        return "%s  SILENCE  main thread silent %ss, phase %s (watchdog thread)" % (t, r.get("silentS"), r.get("phase"))
    return "%s  %-8s %s" % (t, (k or "?").upper(), json.dumps({kk: v for kk, v in r.items()
                                                              if not kk.startswith("_") and kk not in ("utc", "kind")})[:160])


def render_timeline(tl, tz):
    out = ["timeline %s .. %s (%s)" % (_local(tl["from"], tz), _local(tl["to"], tz), tz or DEFAULT_TZ)]
    holes = list(tl["holes"])
    for r in tl["rows"]:
        while holes and holes[0]["from"] <= r["_t"] - float(r.get("dReal") or 0) and holes[0]["to"] <= r["_t"]:
            h = holes.pop(0)
            out.append("%s  -- NO COVERAGE for %ds%s --" % (_local(h["from"], tz), h["to"] - h["from"],
                                                            " (same session: sampler gap)" if h["sameSession"] else ""))
        out.append(render_row(r, tz))
    for h in holes:
        out.append("%s  -- NO COVERAGE for %ds --" % (_local(h["from"], tz), h["to"] - h["from"]))
    tg = ", ".join("target %s: ratio median %.2f min %.2f (n %d)" % (k, v["ratioMedian"], v["ratioMin"], v["n"])
                   for k, v in sorted(tl["byTarget"].items(), key=lambda kv: float(kv[0])))
    out.append("windows %s; incidents %d; sustained %s; %s" % (
        ", ".join("%s %d" % kv for kv in tl["states"].items()) or "none", tl["incidents"], tl["sustained"], tg or "no run windows"))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--at", help="centre time (local in --tz unless it carries a zone)")
    ap.add_argument("--span", default="10m", help="with --at: this much either side (default 10m)")
    ap.add_argument("--since", help="timeline start")
    ap.add_argument("--until", help="timeline end (default now)")
    ap.add_argument("--tz", default=DEFAULT_TZ, help="zone for times you type and times printed (default %(default)s)")
    ap.add_argument("--session", help="only this session (id prefix)")
    ap.add_argument("--sessions", action="store_true", help="list sessions on disk")
    ap.add_argument("--last", type=int, default=0, help="also print the last N rows")
    ap.add_argument("--window", type=int, default=300, help="verdict window in seconds (default 300)")
    ap.add_argument("--dir", default=None, help="record directory (default: the game's SaveData JawaBench/tps)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rec = read_record(a.dir)
    rows = select_session(rec["rows"], a.session)
    health = "%d rows on disk in %d files; %d malformed, %d invalid, %d future, %d vanished mid-read [%s]" % (
        len(rec["rows"]), rec["files"], rec["malformed"], rec["invalid"], rec["future"], rec["vanished"], rec["dir"])
    if a.sessions:
        ss = sessions(rows)
        if a.json:
            print(json.dumps(ss, indent=1))
        else:
            for e in ss:
                print("%s  %s .. %s  pid %s  %d windows  %d incidents  %s" % (
                    e["session"], _local(e["first"], a.tz), _local(e["last"], a.tz), e["pid"], e["samples"],
                    e["incidents"], ",".join(sorted(set(e["events"])))))
            print(health)
        return 0
    if a.at or a.since:
        if a.at:
            c, h = parse_when(a.at, a.tz), parse_span(a.span)
            t0, t1 = c - h, c + h
        else:
            t0 = parse_when(a.since, a.tz)
            t1 = parse_when(a.until, a.tz) if a.until else time.time()
        tl = timeline(rows, t0, t1)
        if a.json:
            print(json.dumps({k: v for k, v in tl.items() if k != "rows"} | {
                "rows": [{k: v for k, v in r.items() if not k.startswith("_")} for r in tl["rows"]]}, indent=1))
        else:
            print(render_timeline(tl, a.tz))
            print(health)
        return 0
    s = summarise(rows, window_s=a.window)
    level, detail = verdict(s)
    if a.json:
        print(json.dumps({"record": {k: v for k, v in rec.items() if k != "rows"}, "summary": s, "level": level,
                          "detail": detail,
                          "last": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows[-a.last:]]
                          if a.last else []}, indent=1))
        return 0
    for r in (rows[-a.last:] if a.last else []):
        print(render_row(r, a.tz))
    print("%s tps: %s" % (level, detail))
    print(health)
    return 0


if __name__ == "__main__":
    sys.exit(main())
