#!/usr/bin/env python3
"""test_process.py -- the one definition of "this process is a test", and the refusal of a live effect from one.

A test process is: a program named selftest*.py or run_selftests.py; a process with RM_UNDER_SELFTEST in its
environment (run_selftests.py sets it); or any descendant of such a program. The descendant clause is the one a mark in
the environment cannot give: on 2026-11-21 a selftest run by hand started a helper with a clean environment, and that
helper reached the real launcher (two real runs and real items on a fixture mod).

The doors to a live effect ask here, each in one line: control.launch_unit (a real unit), model.append (this checkout's
ledger), conductor_log_guard.refuse_if_test (the Conductor's log). A test that wants an effect brings its own target: a
runner, a ledger path, a log path. Page: design/specs/2026-11-18-pipeline-control-surface/boundary.md.

A parent whose /proc entry cannot be read ends the walk as "not a test": the walk guards against a leak and must never
stop real work on a reading it could not make.
"""
import os
import sys

MARK = "RM_UNDER_SELFTEST"


class TestLiveEffect(OSError):
    """A test process tried to make a live effect."""


def _test_program(argv):
    """True when argv is a Python run of selftest*.py or run_selftests.py (the script, not text after -c or -m)."""
    if not argv or not os.path.basename(argv[0]).startswith("python"):
        return False
    for a in argv[1:]:
        if a in ("-c", "-m"):
            return False
        if not a.startswith("-"):
            b = os.path.basename(a)
            return b.startswith("selftest") or b == "run_selftests.py"
    return False


def under_test():
    if os.environ.get(MARK):
        return True
    b = os.path.basename(sys.argv[0] if sys.argv else "")
    if b.startswith("selftest") or b == "run_selftests.py":
        return True
    pid = os.getppid()
    while pid > 1:
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as f:
                argv = [x.decode("utf-8", "replace") for x in f.read().split(b"\0") if x]
            with open("/proc/%d/stat" % pid) as f:
                pid = int(f.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            return False
        if _test_program(argv):
            os.environ[MARK] = "1"      # this process's own children need no walk
            return True
    return False


def refuse(what, repair):
    """Raise TestLiveEffect when this is a test process. `what` names the live effect, `repair` what the test does."""
    if under_test():
        raise TestLiveEffect("a test process may not %s: %s" % (what, repair))
