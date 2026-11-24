#!/usr/bin/env python3
"""already.py: of a week's detached runs, how many result texts say that the work was already done (a wording rule, so a
rough reading: it also counts a run that says one part was already done). The must-not-get-worse reading of
RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT. Read-only.

    python3 design/specs/2026-11-23-agent-work-to-code/census/already.py --end 2026-11-23T19:56-08:00 [--days 7]
Baseline, read 2026-11-23 11:03 PM PST: 93 of 700 read (30 of 730 records could not be read).
Exit 0 read, 2 could not look."""
import argparse
import datetime
import json
import os
import re
import sys

RUNS = os.path.join(os.environ.get("RM_DISPATCHER_STATE") or "/mnt/d/ClaudeWork/rimmandrake/dispatcher", "detached")
RX = re.compile(r"\balready\b[^.\n]{0,60}\b(done|built|landed|published|closed|fixed|made|exists?|holds|on origin)\b"
                r"|\b(done|built|landed|fixed|closed) already\b", re.I)


def result_of(path):
    got = ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if '"result"' in ln and "{" in ln:
                try:
                    o, _ = json.JSONDecoder().raw_decode(ln[ln.find("{"):])
                    got = str(o.get("result") or "") or got
                except (ValueError, AttributeError):
                    continue
    return got


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--end", required=True, help="ISO time with its zone")
    ap.add_argument("--days", type=float, default=7)
    a = ap.parse_args()
    end = datetime.datetime.fromisoformat(a.end).timestamp()
    n = unread = hits = 0
    try:
        names = sorted(x for x in os.listdir(RUNS) if x.endswith(".json") and not x.endswith(".out.json"))
    except OSError as e:
        print("could not look: %s" % e)
        return 2
    for x in names:
        try:
            with open(os.path.join(RUNS, x), encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            unread += 1
            continue
        if not isinstance(r, dict) or not isinstance(r.get("at"), (int, float)) or not end - a.days * 86400 <= r["at"] < end:
            continue
        n += 1
        try:
            t = result_of(r.get("out") or "")
        except OSError:
            t = ""
        if not t:
            unread += 1
        elif RX.search(t):
            hits += 1
    if not n:
        print("could not look: no run record in the window")
        return 2
    print("%d of %d read say already done; %d record(s) could not be read" % (hits, n - unread, unread))
    return 0


if __name__ == "__main__":
    sys.exit(main())
