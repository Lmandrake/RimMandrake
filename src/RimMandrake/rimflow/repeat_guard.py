#!/usr/bin/env python3
"""repeat_guard.py -- what a class guard test must be, and how one is shown failing (REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN).

Design idea 5 (design/RimMandrake/build_system_practices_2026-11-03.md): a twice-seen alarm closes only with a class fix, a
guard test that fails on the whole class and is shown failing on the instance before the fix lands. `rimflow guard` runs the
test here and records the red; `rimflow close` reruns it green. The state half (is one owed?) is model.guard_owed.

A guard is a selftest*.py under the suite's roots, so the nightly sweep keeps running it: a test nothing runs guards nothing.
A crash is not a red: a test that cannot import shows nothing about the instance.
"""
import ast
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


# an added line that ends the test early would make any test green: a cure row never needs one
_EXIT = re.compile(r"\b(?:sys\.exit|os\._exit|exit|quit)\s*\(|\braise\s+SystemExit\b")
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def early_returns(source, added):
    """-> the added line numbers holding a `return` that can end the test early. GUARD_GATE_FIX_NESTED_RETURN_LOOKS_EARLY: the one
    harmless return is in a helper added whole and nested in a function: it ends that helper, not the test. A return at a
    function's own level (or module level) can skip every check below it, and one added to a def the red version already had
    can skip a check that def holds. Raises SyntaxError or ValueError when `source` does not parse."""
    found = set()

    def walk(node, funcs):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Return) and child.lineno in added:
                helper = funcs[-1] if len(funcs) > 1 else None
                if helper is None or not added.issuperset(range(helper.lineno, helper.end_lineno + 1)):
                    found.add(child.lineno)
            walk(child, funcs + [child] if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else funcs)
    walk(ast.parse(source), [])
    return found


def grown_from(root, sha, test, red_hash):
    """-> None when the test at `sha` is the red version grown by added lines only, else why not.
    GUARD_GATE_FIX_CURE_IN_THE_TEST: a census guard whose cure IS a row in the test itself (an allowlist entry) can never
    be committed with the hash it had when shown red. The red version must be committed in `sha`'s own history (found by
    hash), and the test at `sha` may only add lines to it: none removed or changed, none that ends the run early."""
    def git(*a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, timeout=60, stdin=subprocess.DEVNULL)
    now = git("show", "%s:%s" % (sha, test))
    if now.returncode:
        return "%s is not committed at %s" % (test, str(sha)[:12])
    log = git("log", "--format=%H", sha, "--", test)
    red = None
    for c in log.stdout.decode().split() if log.returncode == 0 else ():
        if committed_hash(root, c, test) == red_hash:
            red = c
            break
    if red is None:
        return "the red version (%s) of %s is committed nowhere in %s's history" % (red_hash, test, str(sha)[:12])
    d = git("diff", "--no-color", "-U0", "%s:%s" % (red, test), "%s:%s" % (sha, test))
    if d.returncode not in (0, 1):
        return "git diff failed: %s" % d.stderr.decode(errors="replace")[-200:]
    added = {}
    at = None   # the next line number in the test at `sha`; None is still the file header, whose ---/+++ are no content
    for line in d.stdout.decode(errors="replace").split("\n"):   # not splitlines: a form feed in a line would throw the count off
        hunk = _HUNK.match(line)
        if hunk:
            at = int(hunk.group(1))
        elif at is None:
            continue
        elif line.startswith("-"):
            return "%s at %s removes or changes a line of the red version %s: %r" % (test, str(sha)[:12], red[:12], line[1:80])
        elif line.startswith("+"):
            added[at] = line[1:]
            at += 1
    if not added:
        return None
    try:
        early = early_returns(now.stdout.decode(errors="replace"), set(added))
    except (SyntaxError, ValueError) as e:
        return "%s at %s cannot parse, so its added lines cannot be read: %s" % (test, str(sha)[:12], e)
    for n, line in sorted(added.items()):
        if n in early or _EXIT.search(line):
            return "%s at %s adds a line that ends the test early: %r" % (test, str(sha)[:12], line[:80])
    return None


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
