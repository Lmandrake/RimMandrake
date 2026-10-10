#!/usr/bin/env python3
r"""tps_record.py - read the JawaBench TPS record (BRIDGE_TPS_REGULAR_REPORT_1).

    python3 src/RimMandrake/Utils/tps_record.py              summary of the last 5 minutes
    python3 src/RimMandrake/Utils/tps_record.py --last 60    last 60 samples + summary
    python3 src/RimMandrake/Utils/tps_record.py --json

The JawaBench companion samples ticks-per-second every 5 real seconds while a game is being
played and appends one JSON line per sample to

    C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\tps.jsonl

(rotating to tps.1.jsonl at 1 MB; outside git). The maths here is a PORT of
src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsMath.cs - selftest_tps_record.py
holds the two to the same answers. Doc: design/RimMandrake/tps_record.md.

🔑 Judge TPS against `target` (60 x the effective speed multiplier), never against 60: speed 3
targets 180 and speed 4 (Ultrafast) 900, so "tps 170" is fine at speed 3 and dire at speed 4.
Paused windows (`state: paused`) and windows where the speed setting changed (`state: mixed`)
are recorded but never judged.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# ---- constants: MUST equal JawaBenchTpsMath.cs (selftest_tps_record.py parses and compares) ----
CADENCE_SECONDS = 5.0
MAX_WINDOW_SECONDS = 60.0
TICKS_PER_SECOND_AT_SPEED1 = 60.0
PAUSED_SHARE = 0.5
ROTATE_BYTES = 1024 * 1024
RING_CAPACITY = 720
SUSTAINED_SAMPLES = 6
LOW_RATIO = 0.6
HIGH_RATIO = 1.15

STATE_RUN, STATE_PAUSED, STATE_MIXED = "run", "paused", "mixed"

STALE_SECONDS = 60      # newest sample older than this = sampler not running (or game not in play)


def compute(d_ticks, d_real, frames, paused_frames, multiplier, speed_changed):
    """Port of JawaBenchTpsMath.Compute. Returns dict(tps, target, ratio, pausedFrac, state)."""
    tps = d_ticks / d_real if d_real > 0 else 0.0
    target = TICKS_PER_SECOND_AT_SPEED1 * multiplier
    ratio = tps / target if target > 0 else None
    paused_frac = paused_frames / frames if frames > 0 else 0.0
    if multiplier <= 0 or paused_frac >= PAUSED_SHARE:
        state = STATE_PAUSED
    elif speed_changed:
        state = STATE_MIXED
    else:
        state = STATE_RUN
    return {"tps": tps, "target": target, "ratio": ratio, "pausedFrac": paused_frac, "state": state}


def window_usable(d_real, d_ticks):
    return 0 < d_real <= MAX_WINDOW_SECONDS and d_ticks >= 0


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


def should_rotate(current_bytes, line_bytes):
    return current_bytes > 0 and current_bytes + line_bytes > ROTATE_BYTES


# ---------------------------------------------------------------- the record on disk

def record_dir():
    try:
        from game_paths import PLAYER_LOG
        base = os.path.dirname(PLAYER_LOG)
    except Exception:
        base = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
    return os.path.join(base, "JawaBench", "tps")


def read_samples(directory=None):
    """All samples, oldest first (tps.1.jsonl then tps.jsonl). Malformed lines are counted, not hidden."""
    d = directory or record_dir()
    rows, bad = [], 0
    for name in ("tps.1.jsonl", "tps.jsonl"):
        p = os.path.join(d, name)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    bad += 1
    return rows, bad


def _epoch(utc):
    try:
        return datetime.strptime(utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def summarise(samples, now=None, window_s=300):
    """Summary over samples newer than now-window_s. Pure: selftested on fixtures."""
    now = time.time() if now is None else now
    recent = [s for s in samples if (_epoch(s.get("utc")) or 0) >= now - window_s]
    newest = max((_epoch(s.get("utc")) or 0 for s in samples), default=None)
    run = [s for s in recent if s.get("state") == STATE_RUN and s.get("ratio") is not None]
    tps = [float(s["tps"]) for s in run]
    ratios = [float(s["ratio"]) for s in run]
    return {
        "samples": len(recent),
        "run": len(run),
        "paused": sum(1 for s in recent if s.get("state") == STATE_PAUSED),
        "mixed": sum(1 for s in recent if s.get("state") == STATE_MIXED),
        "newestAgeS": (now - newest) if newest else None,
        "tpsMin": min(tps) if tps else None,
        "tpsMedian": median(tps),
        "tpsMax": max(tps) if tps else None,
        "ratioMedian": median(ratios),
        "target": run[-1].get("target") if run else None,
        "speed": recent[-1].get("speed") if recent else None,
        "frameMaxMs": max((float(s.get("frameMaxMs") or 0) for s in recent), default=None),
        "gc0": sum(int(s.get("gc0") or 0) for s in recent),
        "sustained": sustained(ratios),
    }


def verdict(summary):
    """(level, detail) for belt_watchdog. Levels: OK / INFO / WARN / UNKNOWN. Never escalates a verdict."""
    s = summary
    if not s["samples"]:
        age = s["newestAgeS"]
        if age is None:
            return "UNKNOWN", "no TPS record yet (sampler starts on the first jawa/ call of a session)"
        return "INFO", "no TPS sample in the last 5m (newest %ds ago: game not in play, or sampler not started)" % age
    if not s["run"]:
        return "INFO", "%d samples in 5m, all paused/speed-changing (speed %s)" % (s["samples"], s["speed"])
    body = "tps median %.0f (min %.0f max %.0f) vs target %.0f at %s, ratio %.2f, %d run/%d paused, frameMax %.0fms, gc0 %d" % (
        s["tpsMedian"], s["tpsMin"], s["tpsMax"], s["target"] or 0, s["speed"], s["ratioMedian"],
        s["run"], s["paused"], s["frameMaxMs"] or 0, s["gc0"])
    if s["newestAgeS"] is not None and s["newestAgeS"] > STALE_SECONDS:
        body += "; newest sample %ds old" % s["newestAgeS"]
    if s["sustained"] == "low":
        return "WARN", "SUSTAINED LOW TPS (<%.0f%% of target for %ds): %s" % (
            LOW_RATIO * 100, SUSTAINED_SAMPLES * CADENCE_SECONDS, body)
    if s["sustained"] == "high":
        return "WARN", "SUSTAINED HIGH TPS (>%.0f%% of target for %ds): %s" % (
            HIGH_RATIO * 100, SUSTAINED_SAMPLES * CADENCE_SECONDS, body)
    return "OK", body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--last", type=int, default=0, help="also print the last N samples")
    ap.add_argument("--window", type=int, default=300, help="summary window in seconds (default 300)")
    ap.add_argument("--dir", default=None, help="record directory (default: the game's SaveData JawaBench/tps)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows, bad = read_samples(a.dir)
    s = summarise(rows, window_s=a.window)
    level, detail = verdict(s)
    if a.json:
        print(json.dumps({"dir": a.dir or record_dir(), "total": len(rows), "malformed": bad, "summary": s,
                          "level": level, "detail": detail, "last": rows[-a.last:] if a.last else []}, indent=1))
        return 0
    for r in (rows[-a.last:] if a.last else []):
        print("%s %-6s %-9s tps %7s / %4s  frameMax %sms gc0 %s" % (
            r.get("utc"), r.get("state"), r.get("speed"), r.get("tps"), r.get("target"),
            r.get("frameMaxMs"), r.get("gc0")))
    print("%s tps: %s   [%d samples on disk, %d malformed, %s]" % (level, detail, len(rows), bad, a.dir or record_dir()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
