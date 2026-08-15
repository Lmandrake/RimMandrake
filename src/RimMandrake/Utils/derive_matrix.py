#!/usr/bin/env python3
"""derive_matrix.py — build status_matrix.json from the queues. Nobody hand-maintains it.

    python3 src/RimMandrake/Utils/derive_matrix.py

Counts every item in queue/{DECIDE,BUILD,CHECK}.md, groups by the `row:` field, and
writes the matrix the board renders.

A hand-kept board drifts because the agent that closes work and the agent that
records it are different agents. Deriving removes the second agent.

Item fields read:
    row:    the V1.md row number this serves. Missing -> "unassigned".
    state:  done | ready | doing | blocked | dropped
            dropped items are resolved, not outstanding, and are not counted.
Cell state is: blocked if any item is blocked, working if any is doing,
idle if any remain, done if none remain.

CLOSED WORK IS COUNTED FROM GIT, NOT FROM THE QUEUE
===================================================
An item that is finished leaves its queue, so a denominator of "items currently
filed" shrinks as work gets done and the bar can never fill. Measured 2026-08-14:
124 item IDs had ever existed, 51 were still filed, and `state: done` had been
written 3 times in the whole history — the board was reporting 1/50 while most of
the work was invisible.

So the numerator comes from commit trailers instead:

    Closes: B12

The commit that closes an item is also the commit that deletes it, so the item
still exists in that commit's PARENT — which is where its `row:` is read from.
Nothing is hand-kept and nothing has to be remembered after the fact. The
resolved pairs are cached in `closed_ledger.json`, which is derived: delete it
and the next run rebuilds it.

Total is open + closed, so the denominator only ever grows.
"""
import json
import os
import re
import subprocess
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


LEDGER = "closed_ledger.json"
CLOSES_RE = re.compile(r"^Closes:\s*([A-Z][A-Z0-9-]*)\s*$", re.M)


def git(*args):
    """stdout, or None on any failure. Never raises — the board must still render."""
    try:
        p = subprocess.run(["git", "-C", ROOT, *args],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def resolve_closed(item_id, sha):
    """(row, col) for an item closed at `sha`, read from that commit's parent.

    The closing commit usually deletes the item, so the parent is the last tree
    that still has its `row:`. Returns None if the item cannot be found there —
    a trailer naming an ID that never existed is a typo, not a closure.
    """
    for col in COLS:
        blob = git("show", "%s^:infrastructure/state/queue/%s.md" % (sha, col))
        if not blob:
            continue
        cur, row = None, None
        for ln in blob.splitlines():
            if ln.startswith("## "):
                if cur == item_id:
                    return row, col
                cur = ln[3:].split()[0] if len(ln) > 3 else None
                row = None
            elif cur == item_id:
                m = re.match(r"\s*row\s*:\s*(.+?)\s*$", ln)
                if m:
                    row = m.group(1)
        if cur == item_id:
            return row, col
    return None


def closed_items():
    """-> {id: {'row':.., 'col':..}} for every `Closes:` trailer in history.

    Cached by commit SHA so the common case walks only the new commits.
    """
    path = os.path.join(STATE, LEDGER)
    try:
        with open(path) as fh:
            cache = json.load(fh)
    except (OSError, ValueError):
        cache = {"head": None, "items": {}}

    log = git("log", "--format=%H%x1f%B%x1e")
    if log is None:
        return cache.get("items", {}), []
    items, unresolved = dict(cache.get("items", {})), []
    for rec in log.split("\x1e"):
        if "\x1f" not in rec:
            continue
        sha, body = rec.strip().split("\x1f", 1)
        for item_id in CLOSES_RE.findall(body):
            if item_id in items:
                continue
            found = resolve_closed(item_id, sha)
            if found:
                items[item_id] = {"row": found[0], "col": found[1], "sha": sha[:7]}
            else:
                unresolved.append((item_id, sha[:7]))

    head = git("rev-parse", "HEAD")
    try:
        with open(path + ".tmp", "w") as fh:
            json.dump({"head": (head or "").strip(), "items": items}, fh, indent=1)
        os.replace(path + ".tmp", path)
    except OSError:
        pass
    return items, unresolved


def main():
    names = rownames()
    grid = {}
    for col in COLS:
        for it in parse(os.path.join(STATE, "queue", "%s.md" % col)):
            key = (it.get("row") or "").strip() or "unassigned"
            grid.setdefault(key, {c: [] for c in COLS})[col].append(it)

    # Closed work, from the commit trailers. An item still filed AND closed is
    # counted once — the trailer wins, because it is the durable record.
    closed, unresolved = closed_items()
    open_ids = {i["id"] for c in grid.values() for its in c.values() for i in its}
    shut = {}
    for item_id, meta in closed.items():
        if item_id in open_ids:
            continue
        key = (meta.get("row") or "").strip() or "unassigned"
        shut.setdefault(key, {c: 0 for c in COLS})
        if meta.get("col") in COLS:
            shut[key][meta["col"]] += 1

    # Always emit every V1 row, in order, even with no items — a row that
    # vanishes because nothing is queued against it reads as finished.
    # Unassigned items get their own row at the end rather than being hidden.
    order = sorted(names, key=int)
    order += [k for k in sorted(grid) if k not in names]
    order += [k for k in sorted(shut) if k not in names and k not in grid]
    rows = []
    for key in order:
        cells = {}
        for col in COLS:
            its = [i for i in grid.get(key, {}).get(col, [])
                   if not str(i.get("state","")).startswith("dropped")]
            was = shut.get(key, {}).get(col, 0)
            done = sum(1 for i in its if i.get("state") == "done") + was
            st = ("blocked" if any(i.get("state") == "blocked" for i in its)
                  else "working" if any(i.get("state") == "doing" for i in its)
                  else "offline" if not its and not was
                  else "idle")
            cells[col] = {"done": done, "total": len(its) + was, "state": st}
        rows.append({"name": names.get(key, key), "cells": cells})

    out = os.path.join(STATE, "status_matrix.json")
    with open(out + ".tmp", "w") as fh:
        json.dump({"rows": rows}, fh, indent=1)
    os.replace(out + ".tmp", out)
    tot = sum(c["total"] for r in rows for c in r["cells"].values())
    don = sum(c["done"] for r in rows for c in r["cells"].values())
    print("%s: %d row(s), %d item(s), %d closed" % (out, len(rows), tot, don))
    # A trailer naming an ID that was never filed is a typo, and a silent one
    # would quietly undercount forever.
    for item_id, sha in unresolved:
        print("  ⚠ Closes: %s at %s — no such item in that commit's parent"
              % (item_id, sha), file=sys.stderr)
    if not tot:
        print("queues are empty — the board will render an empty grid",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
