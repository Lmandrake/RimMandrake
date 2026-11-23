#!/usr/bin/env python3
"""selftest_seat_dirt_ledger_append.py — a ledger shard whose only change is appended lines is a safe class.

RIMMANDRAKE_LAND_APPENDED_LEDGER_LINES_IN_TIDY_FIFTH_RING. disk.seat_dirt rang on 2026-11-19, 11-20, 11-22 (twice)
and 11-23 for one cause: a window appends a ledger event line in the seat clone (rimflow) and does not land it.
seat_dirt has no class for a ledger shard, so each ring costs an Operations run and a hand land.
Fixture: a bare origin with ledger shard BENCH.jsonl (2 lines); a clone two hours old holding
  (a) BENCH.jsonl with one appended line       -> landable
  (b) OWNER.jsonl with one line removed        -> stale (never a safe class: a lost line)
  (c) DISPATCHER.jsonl, origin has since appended a line the clone lacks, and the clone appends its own
      -> landable (the clone's lines are an append over its own HEAD; the tidy lands lines, never the whole file)
Expected after the fix: 3 ok, 0 FAIL. Base (2026-11-23): (a) and (c) FAIL.
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
L = "infrastructure/state/ledger/events/"


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


def ev(n):
    return '{"seat":"BENCH","event":"note","id":"X_%d","text":"t","ts":"2026-11-23T00:00:%02dZ"}\n' % (n, n)


def main():
    with tempfile.TemporaryDirectory() as td:
        o, c, c2 = (os.path.join(td, x) for x in ("origin.git", "clone", "other"))
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, c)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c, "config", k, v)
        for shard in ("BENCH", "OWNER", "DISPATCHER"):
            write(c, L + shard + ".jsonl", ev(1) + ev(2))
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "base")
        git(c, "push", "-q", "origin", "main")
        # (c): another writer appends to DISPATCHER.jsonl on origin
        git(td, "clone", "-q", o, c2)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c2, "config", k, v)
        write(c2, L + "DISPATCHER.jsonl", ev(1) + ev(2) + ev(9))
        git(c2, "commit", "-q", "-am", "origin append")
        git(c2, "push", "-q", "origin", "main")
        git(c, "fetch", "-q", "origin")
        two_h = 2 * 3600
        write(c, L + "BENCH.jsonl", ev(1) + ev(2) + ev(3), age_s=two_h)
        write(c, L + "OWNER.jsonl", ev(1), age_s=two_h)
        write(c, L + "DISPATCHER.jsonl", ev(1) + ev(2) + ev(4), age_s=two_h)
        r = seat_dirt.classify(c)
        check(L + "BENCH.jsonl" in r["landable"], "(a) an appended ledger line is landable: %s" % r)
        check(L + "OWNER.jsonl" in r["stale"], "(b) a ledger shard that lost a line is stale, never landable")
        check(L + "DISPATCHER.jsonl" in r["landable"],
              "(c) an append over a HEAD that origin has since appended to is still landable")
    print("%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
