#!/usr/bin/env python3
"""time_budget_lint goes red on a planted tight budget and on one with no danger, and stays green on this tree.

Page: design/specs/2026-11-24-time-budgets/boundary.md. exit 0 all pass, 1 a promise is broken.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import time_budget as T  # noqa: E402
import time_budget_lint as L  # noqa: E402

BAD = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        BAD.append(what)


def py(text, known=None):
    return L.judge(L.budgets_in_py("src/x.py", text), known or {})


CALL = "import subprocess\ndef f():\n    subprocess.run(['git', 'x'], timeout=%s)%s\n"
TAG = "  # budget: danger=a hung git holds the tick; evidence=x; longest=%s (a record)"
KNOWN = {"src/x.py::f::timeout": {"values": [30.0]}}


def t_no_danger_is_refused():
    r = py(CALL % ("30", ""))
    check(len(r) == 1 and "names no danger" in r[0] and "src/x.py:3" in r[0], "no-danger-is-refused: a call (%s)" % r)
    check(len(py("LOAD_TIMEOUT_S = 90\n")) == 1, "no-danger-is-refused: a constant")
    check(len(py("def f(a, wait_s=5):\n    pass\n")) == 1, "no-danger-is-refused: a parameter default")
    check(len(py("ap.add_argument('--run-timeout', type=int, default=90)\n")) == 1, "no-danger-is-refused: an argparse default")
    check(len(L.judge(L.budgets_in_unit("a.service", "[Service]\nTimeoutStartSec=2min\n"), {})) == 1,
          "no-danger-is-refused: a unit")
    check(len(L.judge(L.budgets_in_unit("a.service", "ExecStart=x --max-seconds 1800\n"), {})) == 1,
          "no-danger-is-refused: --max-seconds in a unit")
    check(len(L.judge(L.budgets_in_json("a.json", '{"p": {"run_max_s": 60}}'), {})) == 1, "no-danger-is-refused: a json key")
    check(len(L.judge(L.budgets_in_sh("a.sh", "timeout 70 x.exe\n"), {})) == 1, "no-danger-is-refused: a shell timeout")
    check(len(py(CALL % ("30", "  # budget: danger=none; longest=1s"))) == 1, "no-danger-is-refused: `danger=none` is no danger")
    check(len(py(CALL % ("30", "  # budget: danger=a hang"))) == 1, "no-danger-is-refused: a tag with no longest run")
    check(len(py(CALL % ("30", "  # budget: class=nosuch"))) == 1, "no-danger-is-refused: an unknown class")


def t_tight_is_refused():
    r = py(CALL % ("99", TAG % "10s"))
    check(len(r) == 1 and "9.9 times" in r[0], "tight-is-refused: 99 s over a 10 s run (%s)" % r)
    check(py(CALL % ("100", TAG % "10s")) == [], "tight-is-refused: 100 s over a 10 s run is green")
    check(len(py(CALL % ("599", TAG % "1min"))) == 1 and py(CALL % ("600", TAG % "1min")) == [], "tight-is-refused: a unit in min")
    check(len(py(CALL % ("60 * 9", TAG % "60"))) == 1, "tight-is-refused: an arithmetic number is read")
    check(len(L.judge(L.budgets_in_unit("a.service", "# budget: danger=a hang; longest=90.3s\nTimeoutStartSec=90\n"), {})) == 1,
          "tight-is-refused: the rm-running.service of 2026-11-23 (90 s over a 90.3 s run)")
    check(len(L.judge(L.budgets_in_json("a.json", '{"_limit_s": "danger=a hang; longest=5.7s", "limit_s": 4}'), {})) == 1,
          "tight-is-refused: the metronome's 4 s over a 5.7 s run")
    check(len(py(CALL % (str(T.PUBLISH_S // 20), "  # budget: class=publish"))) == 1 and
          py(CALL % (str(T.PUBLISH_S), "  # budget: class=publish")) == [], "tight-is-refused: a class's own longest run")


def t_one_constant():
    keep = T.FACTOR
    try:
        T.FACTOR = 3
        check(py(CALL % ("30", TAG % "10s")) == [], "one-constant: FACTOR alone moves the line")
    finally:
        T.FACTOR = keep


def t_stays_green():
    check(py(CALL % ("30", TAG % "UNMEASURED")) == [], "stays-green: an UNMEASURED longest run with a danger")
    check(py(CALL % ("5", TAG.replace("%s", "4s") + "; stays=his per-run stop")) == [], "stays-green: `stays` with its reason")
    check(py(CALL % ("time_budget.CALL_S", "")) == [], "stays-green: a name from time_budget.py")
    check(py("# budget: danger=a hang; longest=2s\n# more text\nX_TIMEOUT_S = 20\n") == [], "stays-green: a tag above the line")
    check(py("POLL_S = 3\nSTALE_COUNT = 3\nWINDOW_DAYS = 7\nBUDGET_USD = 5\nretries = 3\nx = dict(size=4)\n") == [],
          "stays-green: a poll, a window, a spend and a count are no time budget")


def t_known_stands():
    check(py(CALL % ("30", ""), KNOWN) == [], "known-stands: at its value")
    check(py(CALL % ("60", ""), KNOWN) == [], "known-stands: raised")


def t_lowered_is_refused():
    r = py(CALL % ("20", ""), KNOWN)
    check(len(r) == 1 and "lowered" in r[0], "lowered-is-refused: 30 s to 20 s")


def t_added_is_refused():
    two = CALL % ("30", "") + "    subprocess.run(['git', 'y'], timeout=30)\n"
    check(len(py(two, KNOWN)) == 1, "added-is-refused: a second call in the same function")


def t_known_is_held_to_the_factor():
    check(len(py(CALL % ("30", ""), {"src/x.py::f::timeout": {"values": [30.0], "longest_s": 3.8}})) == 1,
          "known-is-held-to-the-factor: 30 s over a 3.8 s record")


def t_blind():
    check(L.scan(files=["nothing.txt"])[0] == [], "blind: no file in scope finds nothing, which main() reads as UNMEASURED")


def t_the_tree():
    budgets, unread = L.scan()
    check(budgets is not None and len(budgets) > 400 and not unread, "the-tree: the scan can see (%d budgets)" % len(budgets or ()))
    reds = L.judge(budgets or [], L.load_known())
    for x in reds[:10]:
        print("     RED " + x)
    check(not reds, "the-tree: green (%d red)" % len(reds))


def main():
    for t in (t_no_danger_is_refused, t_tight_is_refused, t_one_constant, t_stays_green,
              t_known_stands, t_lowered_is_refused, t_added_is_refused,
              t_known_is_held_to_the_factor, t_blind, t_the_tree):
        t()
    print("RESULT: %s" % ("FAIL %d" % len(BAD) if BAD else "PASS"))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
