#!/usr/bin/env python3
"""Live bridge utilization: active driving time over time the bridge was held.

    python3 src/RimMandrake/Utils/northstar_driver/bridge_utilization.py [--day 2026-10-01] [--gap-min 5]

HELD   = intervals from the ledger's `bridge` events (state taken -> released, per holder; a take
         while held closes the previous hold).
ACTIVE = union of driver run intervals:
         - modcheck live-queue rows (`Transient/modcheck/*.jsonl`, `started`/`finished`; these are
           naive Windows-local stamps written by python.exe, read as --local-tz)
         - north-star driver results (`Transient/northstar/*.json`, `started_utc` + timing.total_ms;
           mock runs skipped). Tick advance is a bridge call (`step_game_ticks`), so the call log's
           total already includes it — a lower bound, since gaps between calls are not counted.
Utilization = |ACTIVE ∩ HELD| / |HELD|. Idle gaps over --gap-min inside a hold are listed with the
holder, the hold's stated purpose, and any `game` state event inside the gap (LOADING/DOWN = a cold
load or the game being down, the usual cause).

Owner, 2026-10-01: "Live bridge usage. In fact that's a great metric to track."
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTC = dt.timezone.utc


def _utc(s):
    return dt.datetime.strptime(s.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC)


def _local(s, tz):
    return dt.datetime.fromisoformat(s[:19]).replace(tzinfo=tz).astimezone(UTC)


def read_events(ledger_dir):
    evs = []
    for f in sorted(glob.glob(os.path.join(ledger_dir, "*.jsonl"))):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("event") in ("bridge", "game") and e.get("ts"):
                    evs.append(e)
    evs.sort(key=lambda e: e["ts"])
    return evs


def held_intervals(evs, now):
    """[(start, end, holder, purpose)] from bridge taken/released events."""
    out, cur = [], None
    for e in evs:
        if e["event"] != "bridge":
            continue
        t = _utc(e["ts"])
        st = e.get("state")
        if st == "taken":
            if cur:
                out.append((cur[0], t, cur[1], cur[2]))
            holder = e.get("for") or e.get("holder") or e.get("seat")
            cur = (t, holder, e.get("purpose", ""))
        elif st == "released" and cur:
            out.append((cur[0], t, cur[1], cur[2]))
            cur = None
    if cur:
        out.append((cur[0], now, cur[1], cur[2] + " (still held)"))
    return out


def active_intervals(modcheck_globs, northstar_glob, tz):
    out = []
    for pat in modcheck_globs:
        for f in sorted(glob.glob(pat)):
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if r.get("dry_run") or not r.get("started") or not r.get("finished"):
                        continue
                    a, b = _local(r["started"], tz), _local(r["finished"], tz)
                    if b > a:
                        out.append((a, b, "modcheck:%s" % r.get("job", "?")))
    for f in sorted(glob.glob(northstar_glob)):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if d.get("mode") == "mock" or not d.get("started_utc"):
            continue
        a = _utc(d["started_utc"])
        ms = (d.get("timing") or {}).get("total_ms") or 0
        out.append((a, a + dt.timedelta(milliseconds=ms), "northstar:%s" % d.get("mod", "?")))
    return out


def union(iv):
    iv = sorted((a, b) for a, b, *_ in iv if b > a)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def clip(iv, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in iv if b > lo and a < hi]


def report(held, active, game_evs, day=None, gap_min=5.0):
    """Return dict: held_min, active_min, utilization, gaps[...]; restricted to a UTC day if given."""
    if day:
        lo = dt.datetime.combine(day, dt.time(), UTC)
        hi = lo + dt.timedelta(days=1)
    else:
        lo, hi = dt.datetime.min.replace(tzinfo=UTC), dt.datetime.max.replace(tzinfo=UTC)
    act = clip(union(active), lo, hi)
    held_min = act_min = 0.0
    gaps = []
    for a0, b0, who, why in held:
        a, b = max(a0, lo), min(b0, hi)
        if b <= a:
            continue
        held_min += (b - a).total_seconds() / 60
        inside = clip(act, a, b)
        act_min += sum((y - x).total_seconds() for x, y in inside) / 60
        cursor = a
        for x, y in inside + [(b, b)]:
            if (x - cursor).total_seconds() / 60 > gap_min:
                cause = [e["state"] for e in game_evs if cursor <= _utc(e["ts"]) <= x]
                gaps.append({"start": cursor.isoformat(), "end": x.isoformat(),
                             "minutes": round((x - cursor).total_seconds() / 60, 1),
                             "holder": who, "purpose": why,
                             "game_events": cause,
                             "cause": ("cold load / game down" if any(s in ("LOADING", "DOWN") for s in cause)
                                       else "unattributed (see purpose)")})
            cursor = max(cursor, y)
    return {"held_min": round(held_min, 1), "active_min": round(act_min, 1),
            "utilization": round(act_min / held_min, 4) if held_min else None, "gaps": gaps}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--day", help="UTC day YYYY-MM-DD (default: all time)")
    ap.add_argument("--gap-min", type=float, default=5.0)
    ap.add_argument("--ledger", default=os.path.join(REPO, "infrastructure", "state", "ledger", "events"))
    ap.add_argument("--modcheck", action="append",
                    default=None, help="glob of modcheck live-queue jsonl (repeatable)")
    ap.add_argument("--northstar", default=os.path.join(REPO, "Transient", "northstar", "*.json"))
    ap.add_argument("--local-tz", default="America/Los_Angeles",
                    help="zone of the naive modcheck stamps (python.exe on the Windows host)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(a.local_tz)
    mc = a.modcheck or [os.path.join(REPO, "Transient", "modcheck", "*.jsonl")]
    evs = read_events(a.ledger)
    now = dt.datetime.now(UTC)
    held = held_intervals(evs, now)
    active = active_intervals(mc, a.northstar, tz)
    day = dt.date.fromisoformat(a.day) if a.day else None
    r = report(held, active, [e for e in evs if e["event"] == "game"], day, a.gap_min)
    if a.json:
        print(json.dumps(r, indent=1))
        return 0
    u = "n/a" if r["utilization"] is None else "%.1f%%" % (100 * r["utilization"])
    print("bridge utilization %s: held %.1f min, active %.1f min, utilization %s, %d idle gaps > %g min"
          % (a.day or "all-time", r["held_min"], r["active_min"], u, len(r["gaps"]), a.gap_min))
    for g in r["gaps"]:
        print("  %s  %6.1f min  %-8s %s | %s" % (g["start"][:16], g["minutes"], g["holder"], g["cause"],
                                                (g["purpose"] or "")[:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
