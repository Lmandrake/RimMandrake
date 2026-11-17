#!/usr/bin/env python3
"""selftest_designer_closed_item_source.py - a concept record's source `infrastructure/state/items/<ID>.md` still
resolves after the item closes and its prose moves to `items/closed/<ID>.md`
(RIMMANDRAKE_FOLLOW_CLOSED_ITEM_PROSE_SWEEP_BROKE_TWO_SOURCES: the 2026-11-16 Pyrelands ticket sweep closed
PYRELANDS_GREEN_MINIMAL_1 and PYRELANDS_GREEN_FULL_1, and every stage-4 check on Pyrelands then refused its
record.json). Runs in a temp dir; touches no real concept."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

FAILS = []
ITEMS = "infrastructure/state/items/"


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def write(repo, rel):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write("x\n")


def main():
    with tempfile.TemporaryDirectory() as repo:
        write(repo, ITEMS + "LIVE_ONE_1.md")
        write(repo, ITEMS + "closed/MOVED_HERE_1.md")
        nowhere = lambda p: False          # noqa: E731  origin/main holds nothing
        origin_closed = lambda p: p == ITEMS + "closed/MOVED_THERE_1.md"   # noqa: E731

        def errs(src, on_origin=nowhere):
            return DS.source_errors(src, "x", repo, None, on_origin=on_origin)

        e = errs(ITEMS + "LIVE_ONE_1.md")
        check("a live item's prose resolves", e == [], e)
        e = errs(ITEMS + "MOVED_HERE_1.md")
        check("a closed item's prose, moved to items/closed/ here, resolves", e == [], e)
        e = errs(ITEMS + "MOVED_THERE_1.md", origin_closed)
        check("a closed item's prose, moved to items/closed/ on origin/main only, resolves", e == [], e)
        e = errs([ITEMS + "MOVED_HERE_1.md", ITEMS + "LIVE_ONE_1.md"])
        check("a list of a closed and a live item resolves", e == [], e)
        e = errs(ITEMS + "NEVER_FILED_1.md")
        check("an item in neither place is still missing", len(e) == 1 and "does not exist" in e[0], e)
        e = errs(ITEMS + "closed/NEVER_FILED_1.md")
        check("a missing items/closed/ path is still missing", len(e) == 1 and "does not exist" in e[0], e)
        write(repo, "design/other/closed/THING.md")
        e = errs("design/other/THING.md")
        check("only items/ prose follows the move: another folder's closed/ copy does not stand in",
              len(e) == 1 and "does not exist" in e[0], e)
        e = errs(ITEMS + "sub/MOVED_HERE_1.md")
        check("only a top-level item file follows the move", len(e) == 1 and "does not exist" in e[0], e)
        e = errs(ITEMS + "NEVER_FILED_1.md", lambda p: None)
        check("origin/main unreadable for both paths: still refused, saying so",
              len(e) == 1 and "could not be read" in e[0], e)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
