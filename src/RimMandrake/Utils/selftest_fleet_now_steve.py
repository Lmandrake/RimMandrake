#!/usr/bin/env python3
"""selftest_fleet_now_steve.py: one test per promise on design/specs/2026-11-24-fleet-now-stevedesktop/boundary.md.

The checks themselves are in selftest_running_now.py, named `<promise>: ...`. It runs once here; each test asks that every check
of its promise ran and passed. A promise with no check line, or a run that died, fails.
    python3 src/RimMandrake/Utils/selftest_fleet_now_steve.py      exit 0 all pass, 1 a test failed
"""
import functools
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


@functools.lru_cache(maxsize=1)
def lines():
    r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_running_now.py")], capture_output=True, text=True)
    return r.stdout.splitlines(), r.stderr[-400:]


def promise(name):
    out, err = lines()
    mine = [x for x in out if x.startswith(("PASS %s: " % name, "FAIL %s: " % name))]
    assert mine, "no check of %s ran: %s" % (name, err)
    assert all(x.startswith("PASS") for x in mine), [x for x in mine if x.startswith("FAIL")]


def t_steve_games_up_and_driver():
    promise("steve-games-up-and-driver")


def t_steve_jobs_by_name():
    promise("steve-jobs-by-name")


def t_steve_every_reading_has_its_age():
    promise("steve-every-reading-has-its-age")


def t_steve_unread_is_unmeasured_with_cause():
    promise("steve-unread-is-unmeasured-with-cause")


def t_steve_no_second_connection():
    promise("steve-no-second-connection")


def t_steve_panel_names_the_games_right():
    promise("steve-panel-names-the-games-right")


def main():
    bad = 0
    tests = [t_steve_games_up_and_driver, t_steve_jobs_by_name, t_steve_every_reading_has_its_age,
             t_steve_unread_is_unmeasured_with_cause, t_steve_no_second_connection, t_steve_panel_names_the_games_right]
    for t in tests:
        try:
            t()
            print("PASS %s" % t.__name__)
        except AssertionError as e:
            bad += 1
            print("FAIL %s %s" % (t.__name__, e))
    print("FAILED %d" % bad if bad else "ALL PASS (%d)" % len(tests))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
