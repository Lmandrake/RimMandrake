#!/usr/bin/env python3
"""Results nobody acted on, in a window of days (the must-not-get-worse measure of
RIMMANDRAKE_CARRY_RESULT_IN_CONDUCTOR_WAKE_408_FILES_OPENED).

    python3 design/specs/2026-11-23-wake-carries-result/unacted.py --end 2026-11-23T19:56:00-08:00 --days 7

A run counts when it ended in the window and its record holds `owed_close`, or a note on its item that starts LEFT OPEN:
was written between its start and its end (plus 10 minutes), or its result text holds one. It was acted on when, in the 24 h
after its end, an event on its item other than the run's own end note was written, or a run on the item (or one with
`continued_from` naming it) started. Reads the run records and this clone's ledger; writes nothing."""
import argparse
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "src", "RimMandrake", "rimflow"))
import detached_helper as DH  # noqa: E402
import model  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--end", required=True)
    ap.add_argument("--days", type=float, default=7)
    a = ap.parse_args()
    end = datetime.datetime.fromisoformat(a.end).timestamp()
    start = end - a.days * 86400
    by = {}
    for e in model.read():
        t = DH._epoch(e.get("ts"))
        if t is not None:
            by.setdefault(e.get("id"), []).append((t, e))
    recs = []
    for p in glob.glob(os.path.join(DH.runs_dir(), "*.json")):
        if p.endswith(".out.json"):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(r, dict) and r.get("unit"):
            recs.append(r)
    ended = [r for r in recs if isinstance(r.get("ended"), (int, float)) and start <= r["ended"] < end]
    cut = [r for r in ended if r["ended"] + 86400 > datetime.datetime.now().timestamp()]
    need, idle = [], []
    for r in ended:
        evs = by.get(r.get("item"), [])
        mine = [e for t, e in evs if (r.get("at") or 0) <= t <= r["ended"] + 600]
        owed = bool(r.get("owed_close"))
        if not (owed or DH.left_open_noted(mine, r.get("item"), r.get("at") or 0) or DH.result_left_open(r)):
            continue
        need.append(r)
        acted = any(r["ended"] - 60 < t <= r["ended"] + 86400 and ("DETACHED run " + r["unit"]) not in str(e.get("text"))
                    for t, e in evs)
        acted = acted or any(x is not r and (x.get("item") == r.get("item") or x.get("continued_from") == r["unit"])
                             and r["ended"] - 60 < (x.get("at") or 0) <= r["ended"] + 86400 for x in recs)
        if not acted:
            idle.append(r)
    print("runs ended in the window: %d; owed or left open: %d; nobody acted on within 24 h: %d%s" % (
        len(ended), len(need), len(idle),
        "; %d ended under 24 h ago, so their 24 h is not over" % len(cut) if cut else ""))
    for r in idle:
        print("  %s  item %s  ended %s" % (r["unit"], r.get("item"), DH.iso(r["ended"])))


if __name__ == "__main__":
    main()
