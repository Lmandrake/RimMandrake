#!/usr/bin/env python3
"""The polish door of ./publish: a helper run that adds a polish.md line about a file it changed does that polish now.

The rule (CLAUDE.md §Touching code has a cost; design/RimMandrake/standing_rulings.md §Touching code has a cost, the
polish rule): a run that changed a file in this run does the polish of that file in this run, before the fresh reader.
A polish line stays allowed when it names a file the run did not change, or names a concrete risk (`risk:`), or the
change would move a bar, be a new feature or need one of the owner's five acts (`risk:` names which).

check() reads the local commits since origin (the run's own changes) and returns the refusal text, or None. publish.py
raises it as a Refuse before its door checks, so the run's commit comes off HEAD with its files as written, and the run
does the polish and publishes again (a fault of form, returned to the same run: CLAUDE.md §A fault of form). Only a
helper run is checked (RM_ROLE_UNIT or RM_DETACHED_UNIT set); the Conductor and the owner are never refused.
"""
import os
import re
import subprocess

import time_budget

RISK_RX = re.compile(r"\brisk:", re.I)
HELPER_VARS = ("RM_ROLE_UNIT", "RM_DETACHED_UNIT")
NOT_CODE = re.compile(r"(^|/)polish\.md$|^infrastructure/state/ledger/")

RULE = ("A run that changed a file in this run does the polish of that file in this run, before the fresh reader. "
        "A polish line stays only when it names a file that the run did not change, or carries a `risk:` part that "
        "names the concrete risk (this change, this possible wrong result), or the change would move a bar, add a "
        "feature or need one of the owner's five acts (say which after `risk:`).")


def helper_run(env=None):
    env = os.environ if env is None else env
    return any((env.get(v) or "").strip() for v in HELPER_VARS)


def _names(line, path):
    """True when `line` names `path`: its repo path, or its file name as a whole word (not the tail of a longer name)."""
    if path in line:
        return True
    base = os.path.basename(path)
    return bool(base) and re.search(r"(?<![\w./-])%s(?![\w-])" % re.escape(base), line) is not None


def returned(added, changed):
    """added: [(polish path, line)] new in this run; changed: the paths the run changed. -> [(polish path, line, the
    changed file it names)] for each line with no `risk:` part that names a changed file (a polish.md or a ledger shard
    is not a file of code)."""
    code = [p for p in (changed or ()) if not NOT_CODE.search(p)]
    out = []
    for polish, line in added:
        if RISK_RX.search(line):
            continue
        hit = next((p for p in code if _names(line, p)), None)
        if hit:
            out.append((polish, line, hit))
    return out


def _git(top, *a):
    # hang guard (time_budget.CALL_S): one local git read takes under a second; a hung git would hold the landing
    return subprocess.run(["git", *a], cwd=top, capture_output=True, text=True, timeout=time_budget.CALL_S)


def added_lines(top, track):
    """-> [(polish path, line)]: the bullet lines that the local commits since `track` add to any polish.md."""
    r = _git(top, "diff", "-U0", "--no-color", "%s...HEAD" % track, "--", "*polish.md")
    out, cur = [], None
    for ln in (r.stdout or "").splitlines():
        if ln.startswith("+++ "):
            cur = ln[6:] if ln.startswith("+++ b/") else None
        elif ln.startswith("+") and cur and ln[1:].lstrip().startswith(("- ", "* ")):
            out.append((cur, ln[1:].strip()))
    return out


def changed_paths(top, track):
    r = _git(top, "diff", "--name-only", "%s...HEAD" % track)
    return [p for p in (r.stdout or "").splitlines() if p]


def check(top, track, env=None):
    """-> the refusal text, or None (not a helper run, no new polish line, or every new line may stay)."""
    if not helper_run(env):
        return None
    if _git(top, "rev-parse", "--verify", "-q", track).returncode:
        return None                                   # no origin to diff against: the run's own changes are unknown
    hits = returned(added_lines(top, track), changed_paths(top, track))
    if not hits:
        return None
    rows = "\n".join("      %s: %s  (names %s, which this run changed)" % h for h in hits)
    return ("POLISH OF YOUR OWN FILE: this run adds %d polish line(s) about a file it changed:\n%s\n    The rule: %s\n"
            "    Repair: do each polish now, remove its line from the polish.md, and publish again. If a line names a "
            "concrete risk, write that risk after `risk:` on the line." % (len(hits), rows, RULE))
