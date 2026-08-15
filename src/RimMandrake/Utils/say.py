#!/usr/bin/env python3
"""say.py — an agent states what it is doing, and why. Feeds the board's CURRENTLY panel.

    python3 src/RimMandrake/Utils/say.py "counting slag on the 13:54 map" \
            --why "row 4 cannot close until we know if the 4 chunks are ours"

Run it when you change task. Nothing else writes these files.
The `why` is the half a supervisor actually needs and the half a busy agent drops
first; an entry without one renders as a visible gap rather than looking fine.
"""
import argparse
import json
import os
import sys
import time

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DIR = os.path.join(ROOT, "infrastructure/state/status")
AGENTS = os.path.join(ROOT, "infrastructure/agents")


def roster():
    """The seats that exist, read from the identity files rather than a list here.

    A typo or a retired seat name used to create a stamp file that no board ever
    reads and no one ever deletes.
    """
    try:
        return {f[:-3].upper() for f in os.listdir(AGENTS)
                if f.endswith(".md") and f != "POLICY.md"}
    except OSError:
        return set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("item", nargs="*", help="what you are doing now")
    ap.add_argument("--why", default=None, help="why it matters / what it unblocks")
    ap.add_argument("--seat", default=os.environ.get("AGENT_SEAT", ""))
    a = ap.parse_args()

    seat = a.seat.upper()
    if not seat:
        print("no AGENT_SEAT and no --seat", file=sys.stderr)
        return 2
    seats = roster()
    if seats and seat not in seats:
        print("%s is not a seat (%s)" % (seat, ", ".join(sorted(seats))), file=sys.stderr)
        return 2

    p = os.path.join(DIR, "%s.json" % seat)
    os.makedirs(DIR, exist_ok=True)
    cur = {}
    if os.path.exists(p):
        try:
            with open(p) as fh:
                cur = json.load(fh)
        except Exception:
            pass
    if a.item:
        cur["item"] = " ".join(a.item)
    if a.why is not None:
        cur["why"] = a.why
    cur["seat"] = seat
    cur["updated"] = int(time.time())

    tmp = p + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(cur, fh)
    os.replace(tmp, p)                     # atomic: the board never reads a half file
    print("%s: %s" % (seat, cur.get("item", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
