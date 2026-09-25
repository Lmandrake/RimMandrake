#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse a real merge in the SHARED working tree.

WHY
===
Several windows edit /mnt/d/Luke/dev/Rimworld at once, so at any moment its
worktree holds other threads' uncommitted work. A merge rewrites files in that
worktree; a merge that stops half-way leaves conflict markers or a MERGE_HEAD in
files nobody in the merging window owns; and the recovery reflex (abort, reset,
checkout) is exactly the move that erases a peer's edits.

MEASURED 2026-09-25 (forensics from transcripts): a FOUNDRY `git merge` at 07:54
refused ("local changes would be overwritten"), and git's merge then ran its
internal restore_state(): stash, reset --hard to HEAD, `stash apply --index`. A
concurrent BENCH commit held .git/index.lock, the apply failed, and every tracked
edit in the tree (215 files) stayed reverted. None of it appears in the reflog; the
stash survived only as dangling commit e931feba0. Lost: BENCH's Scald defs
(re-landed `860b9e0f9`) and the Rot move's deletions (re-landed `7d8c229ef`).
A refused merge is NOT harmless here.

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
  git reset --hard/--merge/--keep, git checkout -f / . / -- .,
  git restore . (worktree), git stash with no pathspec, git clean -f,
  git checkout-index -a          whole-tree discards

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
    if "--autostash" in flags:               # a whole-tree stash, then a reapply
        return "`--autostash` stashes every peer's edits"
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
    # Whole-tree discards: each erases every peer's uncommitted edit at once.
    paths = [a for a in args if not a.startswith("-")]
    whole = not paths or any(p in (".", ":/", "*") for p in paths)
    if sub == "reset" and flags & {"--hard", "--merge", "--keep"}:
        return "`git reset %s` discards the shared worktree" % " ".join(args)
    if sub == "checkout" and ("-f" in flags or "--force" in flags
                              or ("--" in args and whole)
                              or paths == ["."]):
        return "`git checkout %s` discards the shared worktree" % " ".join(args)
    if sub == "restore" and whole and not ({"--staged", "-S"} & flags
                                           and not {"--worktree", "-W"} & flags):
        return "`git restore %s` discards the shared worktree" % " ".join(args)
    if sub == "stash" and (not args or args[0] in ("push", "save")
                           or args[0].startswith("-")):
        rest = args[1:] if args and args[0] in ("push", "save") else args
        if "--" not in rest:
            return "`git stash` without a pathspec pockets every peer's edits"
    if sub == "clean" and any(a == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a)
                              for a in args):
        return "`git clean -f` deletes peers' untracked files"
    if sub == "checkout-index" and flags & {"-a", "--all"}:
        return "`git checkout-index -a` overwrites the whole shared worktree"
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
    if not cmd or "git" not in cmd:
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
                "Other windows have uncommitted work in it. A failed merge "
                "hard-resets the tree internally — it erased 215 files' edits "
                "2026-09-25 07:54 — and a whole-tree reset/checkout/restore/stash/"
                "clean does the same directly. Discard only YOUR paths "
                "(`git checkout -- <file>`, `git stash push -- <file>`).\n\n"
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
