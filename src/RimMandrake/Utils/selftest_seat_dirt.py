#!/usr/bin/env python3
"""selftest_seat_dirt.py — seat_dirt lands only the safe classes, counts old dirt, and leaves fresh paths alone.

RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR. Fixture: a bare origin whose ledger files item FILED_ITEM_X, and
a clone holding (all two hours old unless said): the item's untracked prose, an unfiled item's prose, a conversation
record, a modified tracked file, and a fresh (one-minute) untracked file.
"""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seat_dirt  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    subprocess.run(["git", "-C", cwd] + list(a), check=True, capture_output=True, text=True)


def write(repo, rel, text, age_s=None):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)
    if age_s is not None:
        t = time.time() - age_s
        os.utime(p, (t, t))


def main():
    old = 2 * 3600
    with tempfile.TemporaryDirectory() as td:
        o, c = os.path.join(td, "origin.git"), os.path.join(td, "clone")
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, c)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c, "config", k, v)
        write(c, "infrastructure/state/ledger/events/BENCH.jsonl",
              '{"seat":"BENCH","event":"file","id":"FILED_ITEM_X","title":"x"}\n'
              '{"seat":"BENCH","event":"note","id":"UNFILED_ITEM_Y","text":"a note is not a filing"}\n')
        write(c, "tracked.txt", "one\n")
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "base")
        git(c, "push", "-q", "origin", "main")

        write(c, "infrastructure/state/items/FILED_ITEM_X.md", "# FILED_ITEM_X\n", old)
        write(c, "infrastructure/state/items/UNFILED_ITEM_Y.md", "# UNFILED_ITEM_Y\n", old)
        write(c, "conversations/2026-11-16-0000-abcd.md", "record\n", old)
        write(c, "tracked.txt", "two\n", old)
        write(c, "live/fresh.json", "{}\n", 60)

        cl = seat_dirt.classify(c)
        check(sorted(cl["landable"]) == ["conversations/2026-11-16-0000-abcd.md",
                                         "infrastructure/state/items/FILED_ITEM_X.md"],
              "landable = the filed item's prose and the conversation record: %s" % cl["landable"])
        check(sorted(cl["stale"]) == ["infrastructure/state/items/UNFILED_ITEM_Y.md", "tracked.txt"],
              "stale = unfiled prose and the old tracked edit: %s" % cl["stale"])
        check(cl["fresh"] == ["live/fresh.json"], "a one-minute-old file is fresh, never counted: %s" % cl["fresh"])

        r = seat_dirt.tidy(c)
        check(r.startswith("PUBLISHED "), "tidy lands the safe classes: %s" % r)
        tree = subprocess.run(["git", "-C", o, "ls-tree", "-r", "--name-only", "main"], capture_output=True,
                              text=True).stdout.split()
        check("infrastructure/state/items/FILED_ITEM_X.md" in tree and "conversations/2026-11-16-0000-abcd.md" in tree,
              "origin now holds both")
        check("infrastructure/state/items/UNFILED_ITEM_Y.md" not in tree and "live/fresh.json" not in tree,
              "origin does not hold the unfiled prose or the fresh file")
        check(subprocess.run(["git", "-C", o, "show", "main:tracked.txt"], capture_output=True,
                             text=True).stdout == "one\n", "the tracked edit was not landed")
        rd = seat_dirt.reading(c)
        check(rd["stale"] == 2 and rd["landable"] == 0, "after tidy the reading is 2 stale, 0 landable: %s" % rd)
        check(seat_dirt.tidy(c) == "nothing to land", "a second tidy lands nothing")
    if FAILS:
        print("FAIL %d" % len(FAILS))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
