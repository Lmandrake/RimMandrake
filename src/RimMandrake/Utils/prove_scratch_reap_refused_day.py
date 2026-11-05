#!/usr/bin/env python3
"""Proof for REAPER_FIX_OWN_SELFTEST_LITTERS_FAKE_SAVES's Done-when: scratch_reap's `refused` stays under its end line
through a day of nightly and hand runs.

Reads the reaper's own records (never a copy): runs.jsonl and its rotation runs.jsonl.1 in the state dir, and
sanity.json. Green (exit 0) only when ALL hold:
  1. every run (apply and dry) stamped inside the last --hours (24) has at most `end.refused` REFUSE rows, the line
     read from scratch_reap_sanity.json, judged as scratch_reap.judge_sanity does (over the line = a problem);
  2. the runs span the window: the oldest in it is no more than --edge-h (2 h) after the window opens, the newest no
     more than --edge-h before now, and no gap between consecutive runs exceeds --gap-h (3 h);
  3. sanity.json's end reading is fresh (--edge-h) and its measures.refused is at or under the same line.
Any unreadable record, missing field or bad line is red: no reading is never a pass. Exit 1 red, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def parse_ts(s: str) -> float:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def fmt(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_runs(sd: Path, since: float, bad: list[str]) -> list[tuple[float, bool, int]]:
    """-> (ts, apply, REFUSE count) of every run stamped at or after `since`, oldest first."""
    out = []
    for name in ("runs.jsonl.1", "runs.jsonl"):
        p = sd / name
        if not p.exists():
            if name == "runs.jsonl":
                bad.append(f"{p}: missing")
            continue
        try:
            fh = open(p, encoding="utf-8")
        except OSError as e:
            bad.append(f"{p}: unreadable: {e}")
            continue
        with fh:
            for n, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                    ts = parse_ts(r["ts"])
                except (ValueError, KeyError, TypeError) as e:
                    bad.append(f"{p}:{n}: unparseable run: {type(e).__name__}")
                    continue
                if ts < since:
                    continue
                rows = r.get("rows")
                if not isinstance(rows, list):
                    bad.append(f"{p}:{n} ({r['ts']}): no rows")
                    continue
                out.append((ts, bool(r.get("apply")), sum(1 for x in rows if isinstance(x, dict)
                                                           and x.get("verdict") == "REFUSE")))
    out.sort()
    return out


def prove(sd: Path, limits: Path, now: float, hours: float, edge_h: float, gap_h: float) -> tuple[bool, list[str]]:
    bad: list[str] = []
    lines: list[str] = []
    try:
        line = json.loads(limits.read_text())["end"]["refused"]
        if not isinstance(line, (int, float)) or isinstance(line, bool):
            raise TypeError(f"end.refused is {line!r}")
    except (OSError, ValueError, KeyError, TypeError) as e:
        return False, [f"RED end line unreadable from {limits}: {e}"]
    start = now - hours * 3600
    runs = load_runs(sd, start, bad)
    runs = [r for r in runs if r[0] <= now + 60]
    lines.append(f"window {fmt(start)} .. {fmt(now)}; end line refused <= {line}; {len(runs)} run(s)")
    for ts, ap, n in runs:
        over = n > line
        lines.append(f"  {fmt(ts)} {'apply' if ap else 'dry  '} REFUSE {n}{'  OVER' if over else ''}")
        if over:
            bad.append(f"run {fmt(ts)} refused {n} over {line}")
    if not runs:
        bad.append("no run in the window")
    else:
        if runs[0][0] - start > edge_h * 3600:
            bad.append(f"window not covered: oldest run {fmt(runs[0][0])} is "
                       f"{(runs[0][0] - start) / 3600:.1f} h after the window opens (max {edge_h} h)")
        if now - runs[-1][0] > edge_h * 3600:
            bad.append(f"newest run {fmt(runs[-1][0])} is {(now - runs[-1][0]) / 3600:.1f} h old (max {edge_h} h)")
        for (a, *_), (b, *_) in zip(runs, runs[1:]):
            if b - a > gap_h * 3600:
                bad.append(f"gap {fmt(a)} .. {fmt(b)}: {(b - a) / 3600:.1f} h with no run (max {gap_h} h)")
    try:
        end = json.loads((sd / "sanity.json").read_text())["end"]
        at, ref = float(end["at"]), end["measures"]["refused"]
        lines.append(f"sanity.json end {fmt(at)}: refused {ref}")
        if now - at > edge_h * 3600:
            bad.append(f"sanity.json end is {(now - at) / 3600:.1f} h old (max {edge_h} h)")
        if not isinstance(ref, (int, float)) or isinstance(ref, bool):
            bad.append(f"sanity.json end refused has no reading: {ref!r}")
        elif ref > line:
            bad.append(f"sanity.json end refused {ref} over {line}")
    except (OSError, ValueError, KeyError, TypeError) as e:
        bad.append(f"sanity.json end unreadable: {type(e).__name__}: {e}")
    return not bad, lines + [f"RED {b}" for b in bad]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state-dir", default=os.environ.get("SCRATCH_REAP_STATE_DIR")
                    or str(Path.home() / ".local/state/rm-scratch-reap"))
    ap.add_argument("--limits", default=str(HERE / "scratch_reap_sanity.json"))
    ap.add_argument("--now", help="UTC stamp YYYY-MM-DDTHH:MM:SSZ (default: the clock)")
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--edge-h", type=float, default=2.0)
    ap.add_argument("--gap-h", type=float, default=3.0)
    a = ap.parse_args(argv)
    if a.hours < 24 and not os.environ.get("PROVE_REFUSED_DAY_SELFTEST"):
        print("--hours under 24 is not a day: refused", file=sys.stderr)
        return 2
    now = parse_ts(a.now) if a.now else time.time()
    ok, out = prove(Path(a.state_dir), Path(a.limits), now, a.hours, a.edge_h, a.gap_h)
    print("\n".join(out[-60:]))
    print("GREEN: refused under its end line through the day" if ok else "RED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
