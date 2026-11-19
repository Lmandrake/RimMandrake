#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_CUT_CONTROL_STORE_TO_PAGE_ARGV_READER_GOES.

control.py is cut, once, to design/specs/2026-11-18-pipeline-control-surface/boundary.md: a launch names its unit as a
field, so nothing reads systemd-run's own options; an input the page puts outside ACCEPTS is refused by name; and the
file is smaller than it was at filing. Exit 0 = every check passes (expected: 4)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, os.path.dirname(HERE))
import control as C  # noqa: E402

LINES_AT_FILING = 2810      # wc -l control.py on a6aac8a6fc7c
FAILS = []


def check(name, ok, got=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else got))
    FAILS.append(name) if not ok else None


def refused(fn):
    try:
        fn()
    except C.Refused:
        return True
    except Exception as e:      # noqa: BLE001
        return "%s: %s" % (type(e).__name__, e)
    return "accepted"


check("no reader of systemd-run's options is left (_sr_unit, SR_VALUE_OPTS)",
      not hasattr(C, "_sr_unit") and not hasattr(C, "SR_VALUE_OPTS"))
called = []
r = C.launch_unit(["systemd-run", "--user", "--unit", "rm-probe-other", "true"], {"family": "probe", "unit": "rm-probe-cut"},
                  runner=lambda a, **k: called.append(a))
check("a launch whose argv names another unit than its spec is refused and never run", getattr(r, "refused", False)
      and not called, (r, called))
got = refused(lambda: C.hook_cmd("condition", "run_x", "/tmp/${HOME}/control.db"))
check("plain-paths: a store path with $ in it is refused by name", got is True, got)
with open(C.__file__.replace(".pyc", ".py"), encoding="utf-8") as f:
    n = sum(1 for _ in f)
check("control.py is smaller than at filing (%d lines)" % LINES_AT_FILING, n < LINES_AT_FILING, n)
print("FAILED %d" % len(FAILS) if FAILS else "PASS control_cut_to_page_accept (4 checks)")
sys.exit(1 if FAILS else 0)
