#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse a real merge in the SHARED working tree.

WHY
===
Several windows edit /mnt/d/Luke/dev/Rimworld at once, so at any moment its
worktree holds other threads' uncommitted work. A merge rewrites files in that
worktree; a merge that stops half-way leaves conflict markers or a MERGE_HEAD in
files nobody in the merging window owns; and the recovery reflex (abort, reset,
checkout) is exactly the move that erases a peer's edits. On 2026-09-25 07:54-07:56,
during a wave of seven branch merges into the shared `main` in three hours, a
tree-wide loss of uncommitted work ate BENCH's Scald def edits (re-landed as
`860b9e0f9`), the TheRot move's staged deletions and uncommitted DLLs.

The rule (owner, 2026-09-25): merges happen in a PRIVATE worktree and are pushed
from there. The shared tree only ever moves forward:

    git worktree add --detach /tmp/claude-1000/merge-<x> origin/main
    cd /tmp/claude-1000/merge-<x> && git merge origin/<branch>   # resolve, build, test
    git push origin HEAD:main
    cd /mnt/d/Luke/dev/Rimworld && git pull --ff-only             # or pull --rebase

WHAT IS BLOCKED (only in the main worktree — linked worktrees are free)
=============================================
  git merge <branch>             unless --ff-only
  git merge --squash <branch>    it still rewrites the shared worktree
  git pull                       unless --ff-only / --rebase / -r (pull.rebase is
                                 unset here, so a bare pull IS a merge)

WHAT IS NOT BLOCKED
===================
  git merge --ff-only / --abort / --continue / --quit
  git pull --ff-only / --rebase / -r
  any merge inside a linked worktree (`git worktree add`, `isolation: worktree`)

Fails OPEN on any parse or git problem: a broken hook must never wedge a session.
"""
import json
import os
import re
import shlex
import subprocess
import sys

TAKES_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
MERGE_SAFE = {"--ff-only", "--abort", "--continue", "--quit"}
PULL_SAFE = {"--ff-only", "--rebase", "-r"}


def is_shared_tree(path):
    """True when `path` is inside the repo's MAIN worktree (not a linked one)."""
    try:
        out = subprocess.run(
            ["git", "-C", path, "rev-parse", "--absolute-git-dir",
             "--git-common-dir"],
            capture_output=True, text=True, timeout=8).stdout.split("\n")
        git_dir = os.path.realpath(out[0])
        common = out[1]
        if not os.path.isabs(common):
            common = os.path.join(path, common)
        return git_dir == os.path.realpath(common)
    except Exception:
        return False                         # fail open


def offence(tok):
    """Reason string if this git command is a real merge, else None."""
    i = 1
    while i < len(tok) and tok[i].startswith("-"):
        i += 1 if tok[i] not in TAKES_ARG else 2
    if i >= len(tok):
        return None
    sub, args = tok[i], tok[i + 1:]
    flags = {a.split("=", 1)[0] for a in args}
    if sub == "merge":
        if flags & MERGE_SAFE:
            return None
        if not [a for a in args if not a.startswith("-")] and "--squash" not in flags:
            return None                      # `git merge` alone just errors
        return "`git merge` rewrites the shared worktree"
    if sub == "pull":
        if flags & PULL_SAFE or any(a.startswith("--rebase") for a in args):
            return None
        return "`git pull` without --ff-only/--rebase is a merge"
    return None


def git_dir_arg(tok):
    """The -C directory on a git command, if any."""
    for j in range(1, len(tok) - 1):
        if tok[j] == "-C":
            return tok[j + 1]
        if not tok[j].startswith("-"):
            break
    return None


def main():
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get("tool_input", {}).get("command", "")
        cwd = payload.get("cwd") or os.getcwd()
    except Exception:
        return 0
    if not cmd or ("merge" not in cmd and "pull" not in cmd):
        return 0

    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        try:
            tok = shlex.split(seg.strip())
        except ValueError:
            continue
        if not tok:
            continue
        if tok[0] == "cd" and len(tok) > 1:  # `cd X && git merge` runs in X
            cwd = os.path.join(cwd, os.path.expanduser(tok[1]))
            continue
        if tok[0] != "git":
            continue
        why = offence(tok)
        if not why:
            continue
        where = git_dir_arg(tok)
        where = os.path.join(cwd, where) if where else cwd
        if not is_shared_tree(where):
            continue
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked by project house rule: %s, and this is the SHARED tree.\n\n"
                "Other windows have uncommitted work in it; a merge (or its abort/"
                "reset recovery) can erase it — it did, 2026-09-25 07:55.\n\n"
                "Merge in a private worktree and push from there:\n"
                "    git worktree add --detach /tmp/claude-1000/merge-x origin/main\n"
                "    cd /tmp/claude-1000/merge-x && git merge origin/<branch>\n"
                "    git push origin HEAD:main\n"
                "Then move the shared tree forward only:\n"
                "    git pull --ff-only     (or git pull --rebase)\n\n"
                "⚠️  NOTHING IN THAT COMMAND RAN — a compound "
                "command is refused whole." % why),
        }}))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
