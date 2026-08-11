#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse blanket git staging in this repo.

WHY
===
Four threads work in this one working tree. At any moment most of what
`git status` shows belongs to someone else, mid-edit. A blanket add sweeps
their unfinished work — and their *staged* work — into your commit, under your
message.

Both failure modes have already happened here, in the same commit (76d7f64,
2026-08-11):
  - it swept three staged `git mv` renames out of another thread's in-flight
    docs audit and committed them under a message about load order;
  - it committed documentation for a script while leaving the script behind,
    because `git commit -a` stages tracked modifications and ignores new
    untracked files.

So the rule in CLAUDE.md is: name every path. This enforces it.

WHAT IS BLOCKED
===============
  git add -A / --all / . / -u / --update       (and short bundles like -An)
  git commit -a / -am / --all
  the same via `git -C <dir> ...`, and inside compound commands

WHAT IS NOT BLOCKED
===================
  git add <explicit paths>      git commit -m "..."      git commit --amend
  git diff --cached --stat      git restore --staged <p>  everything non-git

`-u`/`--update` is included deliberately: it is `commit -a` in `add` form —
every tracked modification in the tree, including other threads'.

Reads the hook JSON on stdin, writes a PreToolUse deny decision on stdout.
Fails OPEN: any parse problem allows the command through, because a broken
hook must never wedge the session.
"""
import json
import re
import shlex
import sys

# global options that consume the following token, e.g. `git -C /path add -A`
TAKES_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

ADD_BLANKET = {"-A", "--all", "--no-ignore-removal", "-u", "--update", "."}


def offence(segment):
    """Return a reason string if this one command is a blanket stage, else None."""
    try:
        tok = shlex.split(segment)
    except ValueError:
        return None                      # unbalanced quotes: not our problem
    if not tok or tok[0] != "git":
        return None

    i = 1
    while i < len(tok) and tok[i].startswith("-"):
        i += 1 if tok[i] not in TAKES_ARG else 2
    if i >= len(tok):
        return None
    sub, args = tok[i], tok[i + 1:]

    if sub in ("add", "stage"):
        for a in args:
            if a in ADD_BLANKET:
                return "`git %s %s` stages everything in the tree" % (sub, a)
            # short bundles: -An, -Av ...
            if re.fullmatch(r"-[A-Za-z]*[Au][A-Za-z]*", a):
                return "`git %s %s` bundles a blanket flag" % (sub, a)
    elif sub in ("commit", "ci"):
        for a in args:
            if a == "--all":
                return "`git commit --all` stages every tracked modification"
            # -a, -am, -ma ... but never --amend / --author (they start with --)
            if re.fullmatch(r"-[A-Za-z]*a[A-Za-z]*", a):
                return "`git commit %s` stages every tracked modification" % a
    return None


def main():
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get("tool_input", {}).get("command", "")
    except Exception:
        return 0                          # fail open

    if not cmd or "git" not in cmd:
        return 0

    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        why = offence(seg.strip())
        if not why:
            continue
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Blocked by project house rule: %s.\n\n"
                    "Four threads share this working tree, so a blanket add "
                    "sweeps another thread's unfinished work into your commit. "
                    "Name every path instead:\n"
                    "    git add path/one.md path/two.xml\n"
                    "    git diff --cached --stat   # read it before committing\n"
                    "See CLAUDE.md > 'Commit explicit paths only'." % why
                ),
            }
        }))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
