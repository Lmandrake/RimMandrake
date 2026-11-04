#!/usr/bin/env python3
"""repeat_guard.py -- what a class guard test must be, and how one is shown failing (REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN).

Design idea 5 (design/RimMandrake/build_system_practices_2026-11-03.md): a twice-seen alarm closes only with a class fix, a
guard test that fails on the whole class and is shown failing on the instance before the fix lands. `rimflow guard` runs the
test here and records the red; `rimflow close` reruns it green. The state half (is one owed?) is model.guard_owed.

A guard is a selftest*.py under the suite's roots, so the nightly sweep keeps running it: a test nothing runs guards nothing.
A crash is not a red: a test that cannot import shows nothing about the instance.
"""
import hashlib
import os
import re
import subprocess

ROOTS = ("src/", ".claude/hooks/", "skills/", "infrastructure/dashboards/hub/", "infrastructure/stevedesktop/")   # run_selftests.SEARCH_ROOTS
TIMEOUT_S = 240
# what a test that never reached its own checks dies of; AssertionError is a test failing, and is a red
CRASH = re.compile(r"^(?:\w+\.)*(?:ImportError|ModuleNotFoundError|SyntaxError|IndentationError|TabError|NameError|TypeError|"
                   r"AttributeError|FileNotFoundError|PermissionError|OSError|KeyError|IndexError|ValueError|MemoryError)\b", re.M)


def test_problem(root, test):
    """-> why `test` (repo-relative) cannot be a guard, or None."""
    if os.path.isabs(test) or ".." in test.split("/"):
        return "%s: name it relative to the repo root" % test
    if not re.match(r"selftest.*\.py$", os.path.basename(test)) or not test.startswith(ROOTS):
        return "%s: a guard is a selftest*.py under %s, so the nightly sweep runs it" % (test, ", ".join(ROOTS))
    if not os.path.isfile(os.path.join(root, test)):
        return "%s: no such file" % test
    return None


def digest(data):
    return hashlib.sha256(data).hexdigest()[:16]


def file_hash(root, test):
    with open(os.path.join(root, test), "rb") as f:
        return digest(f.read())


def committed_hash(root, sha, test):
    """-> the test's hash in commit `sha`, or None when that commit does not hold it."""
    r = subprocess.run(["git", "show", "%s:%s" % (sha, test)], cwd=root, capture_output=True, timeout=60, stdin=subprocess.DEVNULL)
    return digest(r.stdout) if r.returncode == 0 else None


def run(root, test, instance="", timeout=TIMEOUT_S):
    """-> (exit code, its output's tail). 124 when it ran out of time."""
    try:
        r = subprocess.run(["python3", test] + (instance or "").split(), cwd=root, capture_output=True, text=True, errors="replace",
                           timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return 124, "ran past %d s" % timeout
    return r.returncode, ((r.stdout or "") + (r.stderr or ""))[-1500:]


def red_problem(rc, out):
    """-> why this run does not show the guard failing on the instance, or None."""
    if rc == 0:
        return "it passed: a guard shown failing on the instance fails there (run it before the fix lands, or replay the instance with --instance)"
    if rc < 0 or rc >= 124:
        return "it died (exit %d), which shows nothing about the instance: %s" % (rc, out[-200:])
    if "Traceback (most recent call last)" in out and CRASH.search(out.rsplit("Traceback (most recent call last)", 1)[1]):
        return "it crashed before its checks ran: %s" % out[-300:]
    return None
