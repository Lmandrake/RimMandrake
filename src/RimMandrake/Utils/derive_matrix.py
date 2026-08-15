#!/usr/bin/env python3
"""derive_matrix.py — build status_matrix.json from the queues. Nobody hand-maintains it.

    python3 src/RimMandrake/Utils/derive_matrix.py

Counts every item in queue/{DECIDE,BUILD,CHECK}.md, groups by the `row:` field, and
writes the matrix the board renders.

A hand-kept board drifts because the agent that closes work and the agent that
records it are different agents. Deriving removes the second agent.

Item fields read:
    row:    the V1.md row number this serves. Missing -> "unassigned".
    state:  done | ready | doing | blocked  (anything else counts as open)
Cell state is: blocked if any item is blocked, working if any is doing,
idle if any remain, done if none remain.
"""
import json
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STATE = os.path.join(ROOT, "infrastructure/state")
COLS = ["DECIDE", "BUILD", "CHECK"]


def parse(path):
    """-> [{'id':.., 'row':.., 'state':..}] . Tolerates missing fields."""
    items, cur = [], None
    try:
        lines = open(path).read().splitlines()
    except OSError:
        return items
    for ln in lines:
        if ln.startswith("## "):
            if cur:
                items.append(cur)
            cur = {"id": ln[3:].split()[0] if len(ln) > 3 else "?",
                   "row": None, "state": "ready"}
        elif cur is not None:
            m = re.match(r"\s*(row|state)\s*:\s*(.+?)\s*$", ln)
            if m:
                cur[m.group(1)] = m.group(2)
    if cur:
        items.append(cur)
    return items


def rownames():
    """Row labels from V1.md's table, so the board and the burn-down cannot disagree."""
    out = {}
    try:
        for ln in open(os.path.join(STATE, "V1.md")):
            m = re.match(r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|", ln)
            if m:
                out[m.group(1)] = "%s %s" % (m.group(1), m.group(2))
    except OSError:
        pass
    return out


def main():
    names = rownames()
    grid = {}
    for col in COLS:
        for it in parse(os.path.join(STATE, "queue", "%s.md" % col)):
            key = (it.get("row") or "").strip() or "unassigned"
            grid.setdefault(key, {c: [] for c in COLS})[col].append(it)

    # Always emit every V1 row, in order, even with no items — a row that
    # vanishes because nothing is queued against it reads as finished.
    # Unassigned items get their own row at the end rather than being hidden.
    order = sorted(names, key=int)
    order += [k for k in sorted(grid) if k not in names]
    rows = []
    for key in order:
        cells = {}
        for col in COLS:
            its = grid.get(key, {}).get(col, [])
            done = sum(1 for i in its if i.get("state") == "done")
            st = ("blocked" if any(i.get("state") == "blocked" for i in its)
                  else "working" if any(i.get("state") == "doing" for i in its)
                  else "offline" if not its
                  else "idle" if done < len(its) else "idle")
            cells[col] = {"done": done, "total": len(its), "state": st}
        rows.append({"name": names.get(key, key), "cells": cells})

    out = os.path.join(STATE, "status_matrix.json")
    with open(out + ".tmp", "w") as fh:
        json.dump({"rows": rows}, fh, indent=1)
    os.replace(out + ".tmp", out)
    tot = sum(c["total"] for r in rows for c in r["cells"].values())
    print("%s: %d row(s), %d item(s)" % (out, len(rows), tot))
    if not tot:
        print("queues are empty — the board will render an empty grid",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
