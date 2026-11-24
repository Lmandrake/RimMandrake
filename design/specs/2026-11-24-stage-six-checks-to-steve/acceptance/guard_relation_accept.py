#!/usr/bin/env python3
"""Contract: the filler does not run a chain again when the change since its PASS touches nothing that the chain's stage-6
check reads (standing_rulings.md §After a change, only the checks that the change touches run again).

  gaps.untouched(mod, chain, old_sha, new_sha, changed=None, tests=None) -> True | False | None
      True: every stage-6 check whose testq block names the chain declares `reads`, and no changed file is one of them
      (or under one of them). False: a changed file is. None: no check of the chain declares reads, or the change cannot
      be read: the chain runs again. changed / tests: stand-ins for git's file list and the test table.
  gaps.settled counts a chain settled when its last verdict is PASS and untouched() is True since that run's commit.
"""
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "testq"))
A = "src/RimMandrake/M/Source/A.cs"
B = "src/RimMandrake/M/Source/B.cs"
T = {"c1": {"stage": "6", "reads": [A], "testq": {"chains": ["a"]}}, "c2": {"stage": "6", "reads": [A, B], "testq": {"chains": ["a", "b"]}},
     "c3": {"stage": "6", "testq": {"chains": ["n"]}}}


def u(chain, changed, tests=T):
    import gaps
    return gaps.untouched("M", chain, "0000001", "0000002", changed=changed, tests=tests)


CASES = [
    ("a file no check of the chain reads", lambda: u("a", ["src/RimMandrake/M/Source/C.cs"]) is True),
    ("a file one of its checks reads", lambda: u("a", [B]) is False),
    ("a chain no check declares", lambda: u("zz", [B]) is None),
    ("a check with no reads", lambda: u("n", ["x"]) is None),
    ("a change that could not be read", lambda: u("a", None, T) is None),
    ("nothing changed", lambda: u("a", []) is True),
    ("settled asks it", lambda: "untouched(" in open(os.path.join(REPO, "src", "RimMandrake", "Utils", "testq", "gaps.py")).read().split("def settled")[1]),
]
ok = 0
for name, fn in CASES:
    try:
        got = fn()
    except Exception as e:  # noqa: BLE001
        got = "%s: %s" % (type(e).__name__, e)
    ok += got is True
    print("%s %s%s" % ("ok  " if got is True else "FAIL", name, "" if got is True else " -> %s" % got))
print("%s %d/%d" % ("PASS" if ok == len(CASES) else "FAIL", ok, len(CASES)))
sys.exit(0 if ok == len(CASES) else 1)
