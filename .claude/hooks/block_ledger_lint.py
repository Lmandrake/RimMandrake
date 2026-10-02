#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse a `git push` whose HEAD carries a bad ledger shard.

Git plan §2.5: shards merge with `merge=union`, so git itself never stops a torn line,
a missing newline or an in-place edit from landing. `src/RimMandrake/Utils/ledger_lint.py
--rev HEAD --base <upstream>` does; this hook only runs it before a push and relays a
refusal. Fails OPEN on any parse/git/subprocess problem — a broken guard must never
wedge a push; the lint is runnable by hand and runs in run_selftests.py too.
"""
import json
import os
import re
import shlex
import subprocess
import sys

TAKES_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def is_push(tok):
    i = 1
    where = None
    while i < len(tok) and tok[i].startswith("-"):
        if tok[i] == "-C" and i + 1 < len(tok):
            where = tok[i + 1]
        i += 1 if tok[i] not in TAKES_ARG else 2
    return (i < len(tok) and tok[i] == "push"), where


def main():
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get("tool_input", {}).get("command", "")
        cwd = payload.get("cwd") or os.getcwd()
    except Exception:
        return 0
    if "git" not in cmd or "push" not in cmd:
        return 0
    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        try:
            tok = shlex.split(seg.strip())
        except ValueError:
            continue
        if not tok:
            continue
        if tok[0] == "cd" and len(tok) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(tok[1]))
            continue
        if tok[0] != "git":
            continue
        push, where = is_push(tok)
        if not push:
            continue
        where = os.path.join(cwd, where) if where else cwd
        try:
            root = subprocess.run(["git", "-C", where, "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True, timeout=8).stdout.strip()
            script = os.path.join(root, "src", "RimMandrake", "Utils", "ledger_lint.py")
            if not root or not os.path.isfile(script):
                continue
            r = subprocess.run([sys.executable or "python3", script, "--rev", "HEAD",
                                "--root", root, "--base", "origin/main"],
                               capture_output=True, text=True, timeout=40)
        except Exception:
            return 0
        if r.returncode != 1:
            continue                       # 0 clean, 2 could not run -> fail open
        found = [l for l in r.stdout.splitlines() if not l.startswith(("note:", "ledger_lint:"))]
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked by project house rule: ledger shards are append-only and "
                "union-merged (git plan §2.5), so ledger_lint.py must pass on HEAD "
                "before a push. Findings:\n  " + "\n  ".join(found[:12]) +
                "\nFix forward: never edit or delete a ledger line — append a "
                "correcting event; a torn line is repaired with "
                "src/RimMandrake/Utils/repair_torn_ledger.py."),
        }}))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
