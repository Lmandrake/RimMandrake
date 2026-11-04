#!/usr/bin/env python3
"""conductor_log_guard.py -- a test process never appends to the real Conductor log.

Twice a selftest kept a writer's real path and rang fake alarms in the log the Conductor reads at wake: selftest_dispatcher
(CONDUCTOR_LOG_FIX_FAKE_ALARMS_SINCE_1970S, 422 lines) and selftest_known_reds (SELFTEST_ALARM_FIX_ESCAPES_INTO_REAL_LOG,
18 lines). Each test was redirected in turn; this closes the class. Every writer calls refuse_if_test(path) just before
it opens the log, and a refusal is an OSError, which each writer already handles as a log it could not write.

A test process is one whose program is selftest*.py, or anything under run_selftests.py, which sets RM_UNDER_SELFTEST for
its children. selftest_conductor_log_guard.py holds every rules file's path equal to LIVE, so the guard cannot go blind.
"""
import os
import sys

LIVE = "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md"
UNDER_SELFTEST = "RM_UNDER_SELFTEST"


class TestWroteLiveLog(OSError):
    """A test process tried to append to the real Conductor log."""


def under_test():
    return bool(os.environ.get(UNDER_SELFTEST)) or os.path.basename(sys.argv[0] if sys.argv else "").startswith("selftest")


def refuse_if_test(path, live=None):
    """Raise TestWroteLiveLog when this is a test process and `path` is the real log. Any other path or process passes."""
    if under_test() and path and os.path.realpath(path) == os.path.realpath(live or LIVE):
        print("conductor_log_guard: refused a test's append to the real Conductor log: %s" % path, file=sys.stderr)
        raise TestWroteLiveLog("a test process may not append to the real Conductor log: point its rules at a temp path: %s" % path)
