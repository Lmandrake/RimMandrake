#!/usr/bin/env python3
"""selftest_seat_dirt.py — seat_dirt lands only the safe classes, counts old dirt, and leaves fresh paths alone.

RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR. Fixture: a bare origin whose ledger files item FILED_ITEM_X, and
a clone holding (all two hours old unless said): the item's untracked prose, an unfiled item's prose, a conversation
record, a modified tracked file, and a fresh (one-minute) untracked file; and three concept folders
(RIMMANDRAKE_LAND_DESIGNER_RUN_DONE_BUT_NEVER_HARVESTED): Done (a finished run's state never landed: stage.json
advanced, a new result file, result.json renamed away), Busy (the same, with a run open) and Recent (no run open, one
file changed five minutes ago).
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


def fetch_cost():
    """RIMMANDRAKE_SKIP_SEAT_DIRT_FETCH_IN_CLEAN_CLONE (2026-11-22): tidy runs inside ops_watch's disk sense
    phase, which the metronome kills at its limit. An unconditional `git fetch` in each of five clones (20-24 s for
    two role clones behind origin) overran that phase on every beat from 10:00Z and blinded every disk.* reading for
    4 h; the kill aborted each fetch, so the clones never caught up. A clean clone must not fetch, and a fetch past its
    deadline must land nothing and return, never raise or hang."""
    with tempfile.TemporaryDirectory() as td:
        o, c = os.path.join(td, "origin.git"), os.path.join(td, "clone")
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, c)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c, "config", k, v)
        write(c, "tracked.txt", "one\n")
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "base")
        git(c, "push", "-q", "origin", "main")
        calls, real = [], seat_dirt.git

        def spy(clone, *a, **kw):
            calls.append(a[0])
            return real(clone, *a, **kw)
        seat_dirt.git = spy
        try:
            r = seat_dirt.tidy(c)
            check(r == "nothing to land" and "fetch" not in calls,
                  "a clean clone's tidy never fetches (%s, git calls %s)" % (r, calls))

            def slow(clone, *a, **kw):
                if a[0] == "fetch":
                    raise subprocess.TimeoutExpired(["git", "fetch"], 6)
                return real(clone, *a, **kw)
            seat_dirt.git = slow
            write(c, "conversations/2026-11-22-0000-x.md", "record\n", age_s=2 * 3600)
            try:
                r = seat_dirt.tidy(c)
            except Exception as e:  # noqa: BLE001 - the failure under test
                r = "raised %r" % e
            head = subprocess.run(["git", "-C", o, "rev-list", "--count", "main"], capture_output=True, text=True).stdout
            check(r.startswith("not landed") and head.strip() == "1",
                  "a fetch past its deadline lands nothing and returns (%s; origin commits %s)" % (r, head.strip()))
        finally:
            seat_dirt.git = real


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
        for mod in ("Done", "Busy", "Recent"):
            write(c, "design/concepts/%s/stage.json" % mod, '{"stage": 3, "running": null}\n')
            write(c, "design/concepts/%s/result.json" % mod, '{"run": "r1"}\n')
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "base")
        git(c, "push", "-q", "origin", "main")

        write(c, "infrastructure/state/items/FILED_ITEM_X.md", "# FILED_ITEM_X\n", old)
        write(c, "infrastructure/state/items/UNFILED_ITEM_Y.md", "# UNFILED_ITEM_Y\n", old)
        write(c, "conversations/2026-11-16-0000-abcd.md", "record\n", old)
        write(c, "tracked.txt", "two\n", old)
        write(c, "live/fresh.json", "{}\n", 60)
        for mod, running in (("Done", "null"), ("Busy", '{"run": "r2"}'), ("Recent", "null")):
            write(c, "design/concepts/%s/stage.json" % mod, '{"stage": 4, "running": %s}\n' % running, old)
            os.rename(os.path.join(c, "design/concepts/%s/result.json" % mod),
                      os.path.join(c, "design/concepts/%s/result.r1.json" % mod))
            t = time.time() - old
            os.utime(os.path.join(c, "design/concepts/%s" % mod), (t, t))
            os.utime(os.path.join(c, "design/concepts/%s/result.r1.json" % mod), (t, t))
        write(c, "design/concepts/Recent/record.json", "{}\n", 300)
        done = ["design/concepts/Done/result.json", "design/concepts/Done/result.r1.json",
                "design/concepts/Done/stage.json"]

        cl = seat_dirt.classify(c)
        check(sorted(cl["landable"]) == ["conversations/2026-11-16-0000-abcd.md"] + done +
              ["infrastructure/state/items/FILED_ITEM_X.md"],
              "landable = the filed item's prose, the conversation record and the settled concept's state: %s"
              % cl["landable"])
        busy = ["design/concepts/Busy/result.json", "design/concepts/Busy/result.r1.json",
                "design/concepts/Busy/stage.json"]
        recent_old = ["design/concepts/Recent/result.r1.json", "design/concepts/Recent/stage.json"]
        check(sorted(cl["stale"]) == busy + recent_old + ["infrastructure/state/items/UNFILED_ITEM_Y.md", "tracked.txt"],
              "stale = a concept with a run open, a recently touched concept's old files, unfiled prose and the old "
              "tracked edit: %s" % cl["stale"])
        check(not [p for p in cl["landable"] if "/Recent/" in p],
              "a concept folder changed five minutes ago lands nothing, old files included: %s" % cl["landable"])
        check("live/fresh.json" in cl["fresh"] and "design/concepts/Recent/record.json" in cl["fresh"],
              "a one-minute-old file is fresh, never counted: %s" % cl["fresh"])

        r = seat_dirt.tidy(c)
        check(r.startswith("PUBLISHED "), "tidy lands the safe classes: %s" % r)
        tree = subprocess.run(["git", "-C", o, "ls-tree", "-r", "--name-only", "main"], capture_output=True,
                              text=True).stdout.split()
        check("infrastructure/state/items/FILED_ITEM_X.md" in tree and "conversations/2026-11-16-0000-abcd.md" in tree,
              "origin now holds both")
        check("infrastructure/state/items/UNFILED_ITEM_Y.md" not in tree and "live/fresh.json" not in tree,
              "origin does not hold the unfiled prose or the fresh file")
        check("design/concepts/Done/result.r1.json" in tree and "design/concepts/Done/result.json" not in tree and
              subprocess.run(["git", "-C", o, "show", "main:design/concepts/Done/stage.json"], capture_output=True,
                             text=True).stdout.startswith('{"stage": 4'),
              "origin holds the settled concept's advanced state, its renamed result and the deletion")
        check("design/concepts/Busy/result.r1.json" not in tree and "design/concepts/Recent/result.r1.json" not in tree,
              "origin holds nothing of the concept with a run open or the one changed five minutes ago")
        check(subprocess.run(["git", "-C", o, "show", "main:tracked.txt"], capture_output=True,
                             text=True).stdout == "one\n", "the tracked edit was not landed")
        rd = seat_dirt.reading(c)
        check(rd["stale"] == 7 and rd["landable"] == 0, "after tidy the reading is 7 stale, 0 landable: %s" % rd)
        check(seat_dirt.tidy(c) == "nothing to land", "a second tidy lands nothing")

        # Codex review 2026-11-18: a staged rename is two NUL fields; a spaced ledger line; a non-object JSON line
        write(c, "design/concepts/Staged/stage.json", '{"stage": 3, "running": null}\n')
        write(c, "design/concepts/Staged/result.json", '{"run": "r1"}\n')
        git(c, "add", "design/concepts/Staged")
        git(c, "commit", "-q", "-m", "staged base")
        git(c, "push", "-q", "origin", "main")
        t = time.time() - old
        for n in ("stage.json", "result.json"):
            os.utime(os.path.join(c, "design/concepts/Staged", n), (t, t))
        git(c, "mv", "design/concepts/Staged/result.json", "design/concepts/Staged/result.r1.json")
        rows = seat_dirt.dirty(c)
        check(not [p for _s, p in rows if not p.startswith(("design/", "infrastructure/", "tracked", "live/"))],
              "a staged rename's source field is no bogus path: %s" % rows)
        t = time.time() - old
        os.utime(os.path.join(c, "design/concepts/Staged"), (t, t))
        cl = seat_dirt.classify(c)
        check(not [p for p in cl["landable"] if "/Staged/" in p],
              "a concept folder with a staged change never lands (a hand edit; its rename source would be lost): %s"
              % cl["landable"])
        git(c, "mv", "design/concepts/Staged/result.r1.json", "design/concepts/Staged/result.json")
        write(c, "infrastructure/state/ledger/events/OTHER.jsonl",
              '[{"event":"file","id":"SPACED_ITEM_Z"}]\n{"seat": "OTHER", "event": "file", "id": "SPACED_ITEM_Z"}\n')
        git(c, "add", "infrastructure/state/ledger/events/OTHER.jsonl")
        git(c, "commit", "-q", "-m", "spaced filing")
        git(c, "push", "-q", "origin", "main")
        write(c, "infrastructure/state/items/SPACED_ITEM_Z.md", "# SPACED_ITEM_Z\n", old)
        try:
            cl = seat_dirt.classify(c)
        except Exception as e:  # noqa: BLE001 - the crash is the defect
            cl = {"landable": [], "crash": repr(e)}
        check("infrastructure/state/items/SPACED_ITEM_Z.md" in cl["landable"],
              "a filing written with spaces is found, and a JSON array line spoils nothing: %s" % cl)

        # RIMMANDRAKE_STOP_SEAT_DIRT_LANDING_STALE_COPY_OVER_NEWER_ORIGIN (2026-11-22): tidy lands a file whole, so a clone
        # behind origin landed its stale FlowWorks DISPATCH.jsonl over origin's newer one and deleted 4 ledger lines.
        os.remove(os.path.join(c, "infrastructure/state/items/SPACED_ITEM_Z.md"))
        git(c, "reset", "-q", "--hard")
        git(c, "clean", "-qfd")
        git(c, "pull", "-q", "--rebase")
        for mod in ("Lagged", "Ahead"):
            write(c, "design/concepts/%s/stage.json" % mod, '{"stage": 3, "running": null}\n')
            write(c, "design/concepts/%s/ledger/DISPATCH.jsonl" % mod, '{"n": 1}\n')
        write(c, "conversations/2026-11-22-0000-older.md", "record v1\n")
        write(c, "conversations/2026-11-22-0000-newer.md", "record v1\n")
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "lag base")
        git(c, "push", "-q", "origin", "main")
        p = os.path.join(td, "peer")
        git(td, "clone", "-q", o, p)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(p, "config", k, v)
        write(p, "design/concepts/Lagged/ledger/DISPATCH.jsonl", '{"n": 1}\n{"n": 2}\n{"n": 3}\n')
        write(p, "design/concepts/Ahead/ledger/DISPATCH.jsonl", '{"n": 1}\n{"n": 2}\n')
        write(p, "conversations/2026-11-22-0000-older.md", "record v3, six turns\n")
        write(p, "conversations/2026-11-22-0000-newer.md", "record v2\n")
        git(p, "add", "-A")
        subprocess.run(["git", "-C", p, "commit", "-q", "-m", "peer moves origin"], check=True, capture_output=True,
                       env=dict(os.environ, GIT_COMMITTER_DATE="@%d +0000" % int(time.time() - 3600)))
        git(p, "push", "-q", "origin", "main")
        # the clone does not pull: it writes on its old base, as the seat clone did 42 commits behind
        write(c, "design/concepts/Lagged/ledger/DISPATCH.jsonl", '{"n": 1}\n{"n": 2}\n', old)
        write(c, "design/concepts/Ahead/ledger/DISPATCH.jsonl", '{"n": 1}\n{"n": 2}\n{"n": 3}\n', old)
        write(c, "conversations/2026-11-22-0000-older.md", "record v2, five turns\n", old)
        write(c, "conversations/2026-11-22-0000-newer.md", "record v3\n", 15 * 60)
        for mod in ("Lagged", "Ahead"):
            for d in ("design/concepts/%s/ledger" % mod, "design/concepts/%s" % mod):
                t = time.time() - old
                os.utime(os.path.join(c, d), (t, t))
        git(c, "fetch", "-q")
        cl = seat_dirt.classify(c)
        check("design/concepts/Lagged/ledger/DISPATCH.jsonl" not in cl["landable"],
              "a concept file whose origin copy moved past the clone's base never lands: %s" % cl["landable"])
        check("design/concepts/Lagged/ledger/DISPATCH.jsonl" in cl["stale"],
              "the stale-base concept file is counted, so the alarm names it: %s" % cl["stale"])
        check("design/concepts/Ahead/ledger/DISPATCH.jsonl" in cl["landable"],
              "an append-only file that extends origin's newer copy still lands: %s" % cl["landable"])
        check("conversations/2026-11-22-0000-older.md" not in cl["landable"],
              "a conversation record older than origin's last commit of it never lands: %s" % cl["landable"])
        check("conversations/2026-11-22-0000-newer.md" in cl["landable"],
              "a conversation record written after origin's last commit of it lands: %s" % cl["landable"])
        r = seat_dirt.tidy(c)
        show = lambda rel: subprocess.run(["git", "-C", o, "show", "main:" + rel], capture_output=True,  # noqa: E731
                                          text=True).stdout
        check(show("design/concepts/Lagged/ledger/DISPATCH.jsonl").count("\n") == 3,
              "after tidy origin keeps all 3 Lagged ledger lines (%s): %r"
              % (r, show("design/concepts/Lagged/ledger/DISPATCH.jsonl")))
        check(show("conversations/2026-11-22-0000-older.md").startswith("record v3"),
              "after tidy origin keeps its newer conversation record")
    fetch_cost()
    if FAILS:
        print("FAIL %d" % len(FAILS))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
