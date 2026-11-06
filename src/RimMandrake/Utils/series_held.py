#!/usr/bin/env python3
"""series_held.py — did one ops_watch series stay below a line for a whole window, measured the whole time?

    python3 src/RimMandrake/Utils/series_held.py --key disk.tmp_used_pct --below 80 --hours 48 [--max-gap-min 90]
           [--series <family.jsonl>] [--now <epoch>]

Reads an ops_watch series file (default: the family named by the key's first part, under $RM_OPS_WATCH_DIR/series,
else D:\\ClaudeWork\\rimmandrake\\ops_watch\\series). The window is the last --hours ending at --now. Exit codes:
  0  HELD      every MEASURED point in the window is below the line, and no stretch of the window (its start, its end,
               or between two points) went longer than --max-gap-min without a MEASURED point;
  1  BROKEN    a MEASURED point in the window is at or above the line (the newest such point is printed);
  2  UNMEASURED the file is unreadable, or the window has a hole longer than --max-gap-min (an instrument that did not
               run is not evidence the line held: TMP_SCRATCH_PRUNE_SIXTEEN_GIGS_NOBODY_CLAIMS saw a 4 h hole).
One line of output, always.
"""
import argparse
import calendar
import json
import os
import sys
import time
from pathlib import Path

LIVE_SERIES = Path("/mnt/d/ClaudeWork/rimmandrake/ops_watch/series")


def epoch(at: str) -> float:
    return float(calendar.timegm(time.strptime(at[:19], "%Y-%m-%dT%H:%M:%S")))


def points(path: Path, key: str) -> list[tuple[float, float]]:
    """(epoch, value) of every MEASURED point of `key`, in time order; a torn or foreign line is skipped."""
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            try:
                row = json.loads(ln)
                p = row["points"][key]
                if p.get("m") == "MEASURED" and isinstance(p.get("v"), (int, float)):
                    out.append((epoch(row["at"]), float(p["v"])))
            except (ValueError, KeyError, TypeError, AttributeError):
                continue
    return sorted(out)


def judge(pts, below: float, hours: float, max_gap_s: float, now: float) -> tuple[int, str]:
    start = now - hours * 3600
    win = [(t, v) for t, v in pts if start <= t <= now]
    bad = [(t, v) for t, v in win if v >= below]
    if bad:
        t, v = bad[-1]
        return 1, "BROKEN: %s at %s >= %g (%d of %d points in the window)" % (
            v, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)), below, len(bad), len(win))
    edges = [start] + [t for t, _ in win] + [now]
    gap, at = max(((b - a, a) for a, b in zip(edges, edges[1:])), default=(hours * 3600, start))
    if gap > max_gap_s:
        return 2, "UNMEASURED: a %.0f min hole from %s (limit %.0f min); %d points in the %g h window" % (
            gap / 60, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(at)), max_gap_s / 60, len(win), hours)
    return 0, "HELD: %d points over %g h, max %s < %g, longest hole %.0f min" % (
        len(win), hours, max(v for _, v in win), below, gap / 60)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--key", required=True)
    ap.add_argument("--below", type=float, required=True)
    ap.add_argument("--hours", type=float, required=True)
    ap.add_argument("--max-gap-min", type=float, default=90.0)
    ap.add_argument("--series", type=Path)
    ap.add_argument("--now", type=float)
    a = ap.parse_args(argv)
    base = Path(os.environ["RM_OPS_WATCH_DIR"]) / "series" if os.environ.get("RM_OPS_WATCH_DIR") else LIVE_SERIES
    path = a.series or base / (a.key.split(".")[0] + ".jsonl")
    try:
        pts = points(path, a.key)
    except OSError as e:
        print("UNMEASURED: %s: %s" % (path, e.strerror))
        return 2
    code, line = judge(pts, a.below, a.hours, a.max_gap_min * 60, time.time() if a.now is None else a.now)
    print("%s [%s %s]" % (line, a.key, path))
    return code


if __name__ == "__main__":
    sys.exit(main())
