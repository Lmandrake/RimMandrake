#!/usr/bin/env python3
"""shape_cost.py: the cost of one Shape run, read from the run records of this machine. A measuring script.

Item RIMMANDRAKE_CLOSE_TESTLESS_HOLES_HOMES_NOT_248_SHAPE_RUNS. A Shape run is a detached run whose brief is the Shape
brief (roles/list_shape.md, which starts "Shape list item"). Its cost is the record's `tokens` in `token_unit`
weighted_v2 (role_launch.MODEL_PRICES: one uncached Opus 5.5 input token = 1). A record with no such figure is counted
as UNMEASURED, never as 0. The figure goes beside `no_home_shape_per_day` in src/RimMandrake/rimflow/list_dispatch.json.

    python3 design/specs/2026-11-26-testless-tickets/shape_cost.py [--dir <dispatcher/detached>]

Exit 0 read; 2 could not look (no record folder, or no Shape run with a measured cost).
"""
import argparse
import glob
import json
import os
import statistics
import subprocess
import sys

HEAD = "Shape list item"


def default_dir():
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True, timeout=60)  # budget: danger=a hung helper holds this read; it prints one line
    if r.returncode:
        raise RuntimeError("agent_storage.py failed: %s" % (r.stderr.strip() or "no output"))
    return os.path.join(r.stdout.strip(), "rimmandrake", "dispatcher", "detached")


def read(d):
    """-> (measured [(item, tokens)], unmeasured [item])."""
    got, unm = [], []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        if p.endswith(".out.json"):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
            with open(r.get("brief_file") or r.get("brief_src") or "", encoding="utf-8", errors="replace") as f:
                head = f.read(200)
        except (OSError, ValueError, TypeError):
            continue
        if not head.startswith(HEAD):
            continue
        tok = r.get("tokens")
        if isinstance(tok, (int, float)) and not isinstance(tok, bool) and r.get("token_unit") == "weighted_v2":
            got.append((r.get("item"), float(tok)))
        else:
            unm.append(r.get("item"))
    return got, unm


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir")
    o = ap.parse_args(argv)
    try:
        d = o.dir or default_dir()
    except Exception as e:  # noqa: BLE001 - could not look is never a cost of 0
        print("UNMEASURED: the record folder could not be found (%s)" % e)
        return 2
    if not os.path.isdir(d):
        print("UNMEASURED: no record folder at %s" % d)
        return 2
    got, unm = read(d)
    if not got:
        print("UNMEASURED: no Shape run with a measured cost in %s (%d unmeasured)" % (d, len(unm)))
        return 2
    t = [v for _i, v in got]
    print("Shape runs in %s: %d, %d with a measured cost, %d UNMEASURED" % (d, len(got) + len(unm), len(got), len(unm)))
    print("weighted_v2 tokens per run: median %d, mean %d, min %d, max %d" % (
        statistics.median(t), sum(t) / len(t), min(t), max(t)))
    print("at 5 a day: %.1f M at the median, %.1f M at the mean" % (5 * statistics.median(t) / 1e6, 5 * sum(t) / len(t) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
