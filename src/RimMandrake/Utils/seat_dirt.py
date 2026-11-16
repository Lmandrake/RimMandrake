#!/usr/bin/env python3
"""seat_dirt.py — keep the Conductor's seat clone clean: land what is safe to land, alarm on the rest.

RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR (2026-11-16): the seat clone /home/mandrake/rm/bench held 150
dirty paths (92 conversation records, 14 items whose ledger `file` event was on origin but whose prose never landed,
5 Designer edits, 15 queue views, ...) and nothing noticed. Two classes are always safe to land and are landed here:

    conversations/*.md           written by ~/dev/Lodestar/bin/conversations.py, landed before only at a handoff
    infrastructure/state/items/<ID>.md, untracked, when origin's ledger has a `file` event for <ID> and origin has
                                 no such file: the item exists, its prose is simply missing from origin

Everything else older than STALE_MIN is counted as `disk.seat_dirt` by ops_watch (alarm OPS_SEAT_CLONE_DIRT_RESTORE):
a writer is dirtying the seat clone instead of its own clone. A path written in the last STALE_MIN minutes is taken
to be held by a live run and is never counted or landed.

    seat_dirt.py report [--clone DIR]        one JSON reading
    seat_dirt.py tidy [--clone DIR] --apply  land the safe classes, then print the reading
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SEAT_CLONE = os.environ.get("RM_SEAT_CLONE", "/home/mandrake/rm/bench")
STALE_MIN = 60           # older than this and not landable -> dirt (the alarm)
SETTLE_MIN = 10          # a safe-class file is landed only once it has not changed for this long
ITEMS = "infrastructure/state/items/"
LEDGER = "infrastructure/state/ledger/"
LAND = os.path.join(HERE, "land.sh")
ITEM_RE = re.compile(r"^infrastructure/state/items/([A-Z0-9_]+)\.md$")


def git(clone, *a, check=True):
    r = subprocess.run(["git", "-C", clone] + list(a), capture_output=True, text=True, timeout=120)
    if check and r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a[:2]), r.stderr.strip()[:300]))
    return r.stdout


def dirty(clone):
    """-> [(status, path)] for every modified, deleted or untracked path (ignored files never count)."""
    out = []
    for rec in git(clone, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"):
        if len(rec) > 3:
            out.append((rec[:2], rec[3:]))
    return out


def age_min(clone, path, now):
    """Minutes since the path last changed; a deleted path takes its directory's time (when it was removed)."""
    p = os.path.join(clone, path)
    while not os.path.lexists(p) and p != clone:
        p = os.path.dirname(p)
    try:
        return (now - os.lstat(p).st_mtime) / 60.0
    except OSError:
        return 0.0


def filed_on_origin(clone, ids, ref="origin/main"):
    """-> the subset of ids that origin's ledger holds a `file` event for."""
    if not ids:
        return set()
    pats = []
    for i in sorted(ids):
        pats += ["-e", '"id":"%s"' % i]
    out = git(clone, "grep", "-h", "-F", *pats, ref, "--", LEDGER, check=False)
    found = set()
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("event") == "file" and e.get("id") in ids:
            found.add(e["id"])
    return found


def on_origin(clone, path, ref="origin/main"):
    return subprocess.run(["git", "-C", clone, "cat-file", "-e", "%s:%s" % (ref, path)],
                          capture_output=True).returncode == 0


def classify(clone, now=None):
    """-> {"landable": [paths], "fresh": [paths], "stale": [paths]} over the clone's dirt."""
    now = time.time() if now is None else now
    rows = [(st, p, age_min(clone, p, now)) for st, p in dirty(clone)]
    item_ids = {ITEM_RE.match(p).group(1) for st, p, _ in rows if st == "??" and ITEM_RE.match(p)}
    filed = filed_on_origin(clone, item_ids)
    out = {"landable": [], "fresh": [], "stale": []}
    for st, p, age in rows:
        m = ITEM_RE.match(p)
        safe = (p.startswith("conversations/") and p.endswith(".md") and st != " D") or \
               (st == "??" and m and m.group(1) in filed and not on_origin(clone, p))
        if safe and age >= SETTLE_MIN:
            out["landable"].append(p)
        elif age < STALE_MIN:
            out["fresh"].append(p)
        else:
            out["stale"].append(p)
    return out


def reading(clone=SEAT_CLONE, now=None):
    c = classify(clone, now)
    return {"clone": clone, "stale": len(c["stale"]), "landable": len(c["landable"]), "fresh": len(c["fresh"]),
            "stale_paths": c["stale"][:12]}


def tidy(clone=SEAT_CLONE, now=None, land=LAND):
    """Land the safe classes in one land.sh -m commit (a temp index from origin/main: the clone's index, HEAD and a
    peer's edits are never touched). -> "PUBLISHED <sha>" | "nothing to land" | raises RuntimeError on a refusal."""
    paths = classify(clone, now)["landable"]
    if not paths:
        return "nothing to land"
    msg = ("seat_dirt: land %d safe path(s) left in the seat clone (conversation records, filed item prose)\n\n"
           "RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR (seat_dirt.py tidy)." % len(paths))
    p = subprocess.run(["sh", land, "-m", msg] + paths, cwd=clone, capture_output=True, text=True, timeout=600,
                       env=dict(os.environ, LAND_REPO=clone))
    if p.returncode == 0:
        return (p.stdout.strip().splitlines() or ["PUBLISHED ?"])[-1]
    if "nothing to land" in p.stderr:
        return "nothing to land"
    raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()[-400:]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("report", "tidy"))
    ap.add_argument("--clone", default=SEAT_CLONE)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "tidy":
        if a.apply:
            print(tidy(a.clone))
        else:
            print("\n".join(classify(a.clone)["landable"]) or "nothing to land")
    print(json.dumps(reading(a.clone)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
