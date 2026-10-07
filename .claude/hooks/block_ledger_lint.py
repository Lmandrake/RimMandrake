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


def pushed_head(cwd, refspec):
    """The commit a `git push <remote> <src>:<dst>` publishes: <src>, not HEAD
    (ART_LEDGER_SEAT_DEFAULT_1 — `git push origin <sha>:main` used to be checked
    against whatever HEAD happened to be). Falls back to HEAD."""
    src = (refspec or "").lstrip("+").split(":", 1)[0] if refspec else ""
    if src:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--verify", "-q", src + "^{commit}"],
                           capture_output=True, text=True, timeout=8)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return "HEAD"


def is_push(tok):
    i = 1
    where = None
    while i < len(tok) and tok[i].startswith("-"):
        if tok[i] == "-C" and i + 1 < len(tok):
            where = tok[i + 1]
        i += 1 if tok[i] not in TAKES_ARG else 2
    return (i < len(tok) and tok[i] == "push"), where


def push_refspec(tok):
    """The refspec argument of a `git push` token list, or None."""
    i = 1
    while i < len(tok) and tok[i] != "push":
        i += 1 if tok[i] not in TAKES_ARG else 2
    pos = [a for a in tok[i + 1:] if not a.startswith("-")]
    return pos[1] if len(pos) > 1 else None


ZERO = "0" * 40


def git_pre_push(stdin_lines, cwd):
    """Git-native mode (`--git-pre-push`): lint each pushed local sha against the
    remote sha (or origin/main for a new branch). Returns 1 to refuse, else 0."""
    root = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, timeout=8).stdout.strip()
    script = os.path.join(root, "src", "RimMandrake", "Utils", "ledger_lint.py")
    if not root or not os.path.isfile(script):
        return 0
    for line in stdin_lines:
        parts = line.split()
        if len(parts) < 4 or parts[1] == ZERO:
            continue
        base = parts[3] if parts[3] != ZERO else "origin/main"
        r = subprocess.run([sys.executable or "python3", script, "--rev", parts[1],
                            "--root", root, "--base", base],
                           capture_output=True, text=True, timeout=40)
        if r.returncode == 1:
            found = [l for l in r.stdout.splitlines() if not l.startswith(("note:", "ledger_lint:"))]
            sys.stderr.write("pre-push REFUSED (ledger_lint) on %s:\n  %s\n" % (parts[0], "\n  ".join(found[:12])))
            return 1
    return 0


def main():
    if "--git-pre-push" in sys.argv:
        try:
            return git_pre_push(sys.stdin.read().splitlines(), os.getcwd())
        except Exception as e:
            sys.stderr.write("pre-push: ledger guard crashed, failing open: %r\n" % (e,))
            return 0
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
            rev = pushed_head(where, push_refspec(tok))
            r = subprocess.run([sys.executable or "python3", script, "--rev", rev,
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
