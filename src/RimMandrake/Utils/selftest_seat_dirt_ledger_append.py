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
Expected after the fix: 6 ok, 0 FAIL. Base (2026-11-23): (a) and (c) FAIL.

RELAPSE_WORK_BELT_FIX_DIED_TWICE: 6 of 32 bench tidies 2026-11-23 18:57..11-24 10:34 PST were refused. The tidy merged a
shard, then land.sh fetched a newer origin and landed the merge whole: it lost every line that arrived between (the
pre-push lint refused it NOT_APPEND). race(): a peer lands a line during the push; every line must reach origin.
names(): a ring of disk.seat_dirt names its paths (ring 6 could not be traced: only the count was kept).
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


def race(hook_says):
    """A peer lands a ledger line on origin while the tidy pushes: origin keeps it, and the clone's line lands too.
    hook_says: "exit 0" (git itself rejects the moved ref) or the lint's refusal (its base is the newer origin)."""
    with tempfile.TemporaryDirectory() as td:
        o, c, peer = (os.path.join(td, x) for x in ("origin.git", "clone", "peer"))
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, c)
        write(c, L + "BENCH.jsonl", ev(1) + ev(2))
        write(c, "conversations/a.md", "old\n")
        write(c, ".gitattributes", L + "*.jsonl merge=union\n")       # as in the repo: what lets seat_sync level a shard
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c, "config", k, v)
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "base")
        git(c, "push", "-q", "origin", "main")
        git(td, "clone", "-q", o, peer)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(peer, "config", k, v)
        write(peer, L + "BENCH.jsonl", ev(1) + ev(2) + ev(8))
        git(peer, "commit", "-q", "-am", "peer line")
        hook = os.path.join(c, ".git", "hooks", "pre-push")
        write(c, ".git/hooks/pre-push", "#!/bin/sh\n[ -e %s/raced ] && exit 0\ntouch %s/raced\n"
              "git -C %s push -q origin HEAD:main\n%s\n" % (td, td, peer, hook_says))
        os.chmod(hook, 0o755)
        write(c, L + "BENCH.jsonl", ev(1) + ev(2) + ev(3), age_s=7200)
        try:
            res = seat_dirt.tidy(c, settle_min=0)
        except Exception as e:  # noqa: BLE001 - a refused tidy is the fault under test
            res = "raised %s" % e
        got = subprocess.run(["git", "-C", o, "show", "main:" + L + "BENCH.jsonl"], capture_output=True, text=True).stdout
        check(os.path.exists(os.path.join(td, "raced")), "race[%s]: " % hook_says[:6] + "the peer's landing really happened inside the push")
        check(ev(8) in got, "race[%s]: " % hook_says[:6] + "the line a peer landed during the push stays on origin: %r (%s)" % (got, res))
        check(got.count(ev(3)) == 1 and "PUBLISHED" in res, "race[%s]: " % hook_says[:6] + "the clone's line lands once, and the tidy says so: %s" % res)
        check(seat_dirt.dirty(c) == [], "race[%s]: " % hook_says[:6] + "the clone is clean after: %s" % seat_dirt.dirty(c))
        # both kinds in one pass: the record goes with land.sh, the line as a line
        write(c, "conversations/a.md", "new\n", age_s=-5)
        write(c, L + "BENCH.jsonl", got + ev(4), age_s=7200)
        res = seat_dirt.tidy(c, settle_min=-1)
        show = lambda p: subprocess.run(["git", "-C", o, "show", "main:" + p], capture_output=True, text=True).stdout  # noqa: E731
        check(show("conversations/a.md") == "new\n" and show(L + "BENCH.jsonl") == got + ev(4),
              "mixed: a record and a ledger line land in one tidy: %s" % res)
        # a hook's verdict is said, not swallowed, and the line stays in the clone
        write(c, ".git/hooks/pre-push", "#!/bin/sh\necho 'pre-push REFUSED (test)' >&2\nexit 1\n")
        write(c, L + "BENCH.jsonl", got + ev(4) + ev(5), age_s=7200)
        try:
            res = "returned %s" % seat_dirt.tidy(c, settle_min=0)
        except Exception as e:  # noqa: BLE001
            res = "raised %s" % e
        with open(os.path.join(c, L + "BENCH.jsonl")) as f:
            kept = ev(5) in f.read()
        check(res.startswith("raised") and "pre-push REFUSED (test)" in res and kept,
              "refused: the tidy fails with the hook's words and the clone keeps its line: %s" % res)


def names():
    """The real rules row of disk.seat_dirt, run through run_alarms: the filing names the path, a new path is a note."""
    import json
    import pathlib
    with tempfile.TemporaryDirectory() as td:
        for k in ("RM_OPS_WATCH_DIR", "TESTQ_QUEUE", "RM_DATA_ROOT"):
            os.environ[k] = os.path.join(td, k)
            os.makedirs(os.environ[k])
        import ops_watch as OW
        rules = json.loads((pathlib.Path(HERE) / "ops_watch_rules.json").read_text())
        rules["targets"] = [t for t in rules["targets"] if t["key"] == "disk.seat_dirt"]
        pt = lambda *p: {"disk.seat_dirt": OW.M(len(p), "paths dirty", paths=list(p))}  # noqa: E731
        seen = []

        def filer(todo, conf):
            seen.extend(todo)
            return {a["name"]: None for a in todo}
        now = time.time()
        OW.run_alarms(pt("left/a.json"), rules, now, set(), filer, open_ids=None)
        check(len(seen) == 1 and "left/a.json" in str(seen[0].get("title")), "names: the ring's title names the path: %s" % seen)
        n = len(seen)
        OW.run_alarms(pt("left/a.json", "left/b.json"), rules, now + 600, set(), filer, open_ids=None)
        check(len(seen) > n and any("left/b.json" in json.dumps(a) for a in seen[n:]),
              "names: a path that joins an open ring is told: %s" % seen[n:])
        n = len(seen)
        OW.run_alarms(pt("left/a.json", "left/b.json"), rules, now + 1200, set(), filer, open_ids=None)
        check(len(seen) == n, "names: the same paths again say nothing: %s" % seen[n:])


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
        # tidy-level: origin's newer line (9) and the clone's appended lines both reach origin; nothing is lost
        res = seat_dirt.tidy(c, settle_min=0)
        shows = lambda sh: subprocess.run(["git", "-C", o, "show", "main:" + L + sh + ".jsonl"], capture_output=True,  # noqa: E731
                                          text=True).stdout
        d = shows("DISPATCHER")
        check(d == ev(1) + ev(2) + ev(9) + ev(4), "tidy keeps origin's newer line and lands the clone's: %r (%s)" % (d, res))
        check(shows("BENCH") == ev(1) + ev(2) + ev(3), "tidy lands the appended BENCH line")
        check(shows("OWNER") == ev(1) + ev(2), "tidy never lands a shard that lost a line")
    race("exit 0")
    race("echo 'pre-push REFUSED (ledger_lint) on x: NOT_APPEND' >&2; exit 1")
    names()
    print("%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
