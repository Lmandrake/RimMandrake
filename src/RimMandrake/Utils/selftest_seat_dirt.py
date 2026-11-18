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
    if FAILS:
        print("FAIL %d" % len(FAILS))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
