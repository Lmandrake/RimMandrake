#!/usr/bin/env python3
"""holes_check.py: the outcome check of RIMMANDRAKE_CLOSE_TESTLESS_HOLES_HOMES_NOT_248_SHAPE_RUNS.

It runs testless_census.py and counts two kinds of hole among the open tickets with no test:
  - a ticket with no home and no route (its `why` holds "no home");
  - a ticket under a block with no kind and no end condition (its `why` holds "no end condition").
A hole counts at any depth of a ticket's `then` chain (what the ticket would be after its park or hold ends).

Exit 0: both counts are 0. Exit 1: a hole is left. Exit 2: could not look (the cause is printed).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "testless_census.py")
KINDS = (("no-home", "no home"), ("untyped-block", "no end condition"))


def hole_whys(ticket):
    out = []
    while isinstance(ticket, dict):
        if ticket.get("hole"):
            out.append(ticket.get("why") or "")
        ticket = ticket.get("then")
    return out


def main():
    try:
        run = subprocess.run([sys.executable, "-I", CENSUS, "--json"], capture_output=True, text=True)
    except OSError as err:
        print(f"COULD NOT LOOK: the census did not start: {err}")
        return 2
    if run.returncode != 0:
        print(f"COULD NOT LOOK: the census exited {run.returncode}: {run.stderr.strip()[-300:]}")
        return 2
    try:
        tickets = json.loads(run.stdout)
    except ValueError as err:
        print(f"COULD NOT LOOK: the census output is not JSON: {err}")
        return 2
    if not isinstance(tickets, dict) or not tickets:
        print("COULD NOT LOOK: the census listed no ticket, so the instrument cannot be shown to see")
        return 2
    counts = {}
    for name, words in KINDS:
        counts[name] = sorted(i for i, t in tickets.items() if any(words in w for w in hole_whys(t)))
    for name, _ in KINDS:
        ids = counts[name]
        print(f"{name} holes: {len(ids)} of {len(tickets)} open tickets with no test" + (f"; first: {', '.join(ids[:3])}" if ids else ""))
    left = sum(len(v) for v in counts.values())
    print("HOLDS: no hole of either kind" if not left else "FAILS: a hole is left")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
