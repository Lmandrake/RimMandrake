#!/usr/bin/env python3
"""selftest_run_host.py: one test per promise of design/specs/2026-11-24-run-on-steve/boundary.md. Offline."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_host as R

GOOD = {"reachable": True, "claude": "2", "account": "a", "picked_account": "a", "push": True,
        "clone": "~/rm/list/X", "free_gb": 9}


def t_refused_by_name():
    assert R.plan("steve9", "X", "/b", GOOD)["verdict"] == "REFUSED"
    assert R.plan("stevedesktop", "X", "/b", dict(GOOD, account="b"))["verdict"] == "REFUSED"
    assert R.plan("stevedesktop", "X", "/b", dict(GOOD, push=False))["verdict"] == "REFUSED"
    assert R.plan("stevedesktop", "X", "/b", dict(GOOD, clone="~/rm/runner"))["verdict"] == "REFUSED"


def t_could_not_look_named():
    for k in GOOD:
        r = R.plan("stevedesktop", "X", "/b", dict(GOOD, **{k: None}))
        assert r["verdict"] == "COULD NOT LOOK" and k in r["why"]


def t_no_spend_stated():
    assert "max-budget-usd" not in " ".join(R.plan("stevedesktop", "X", "/b", GOOD)["argv"])


def main():
    bad = 0
    for f in (t_refused_by_name, t_could_not_look_named, t_no_spend_stated):
        try:
            f()
            print("ok  ", f.__name__)
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("FAIL", f.__name__, e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
