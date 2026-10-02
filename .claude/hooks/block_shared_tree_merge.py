#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse a real merge in the SHARED working tree.

WHY
===
Several windows edit /mnt/d/Luke/dev/RimMandrake (symlinked as .../Rimworld) at once, so at any moment its
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
    cd /home/mandrake/rm/<seat> && git pull --rebase origin main   # ext4 clone, never D:\\

WHAT IS BLOCKED (only in the main worktree — linked worktrees are free)
=============================================
  git merge <branch>             unless --ff-only
  git merge --squash <branch>    it still rewrites the shared worktree
  git pull                       unless --ff-only / --rebase / -r (pull.rebase is
                                 unset here, so a bare pull IS a merge)
  git reset --hard/--merge, git checkout -f / . / -- .,
  git restore . (worktree), git stash with no pathspec, git clean -f,
  git checkout-index -a          whole-tree discards

ADDED 2026-10-02 (git_workflow_plan_2026-10-01.md Phase 1) -- the D:\\ tree is guarded by PATH,
not only by "main worktree": when the command's target tree (cwd, `cd X &&`, `git -C X`)
is /mnt/d/Luke/dev/RimMandrake or /mnt/d/Luke/dev/Rimworld it ALSO refuses
  git checkout <ref> -- <path>     (rewrites files from another commit under peers)
  git restore --source/-s ...      (same)
and, wherever the command runs, `git worktree add <path under /mnt/d>` (a drvfs
worktree repeats the 9p index-corruption class). Every whole-tree refusal above also
applies by path, so a missing/renamed .git on D:\\ cannot make the guard fail open.
ext4 clones (/home/mandrake/rm/*) are unaffected.

WHAT IS NOT BLOCKED
===================
  git merge --ff-only / --abort / --continue / --quit
  git reset --keep                  aborts rather than touch a dirty file; it is how
                                    how a tree that keeps local edits moves forward
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


D_ROOTS = ("/mnt/d/Luke/dev/RimMandrake", "/mnt/d/Luke/dev/Rimworld")


def _real(p):
    return os.path.realpath(os.path.expanduser(p))


def is_d_path(path):
    """True when `path` is the D:\\ shared tree or inside it (symlink-resolved)."""
    try:
        rp = _real(path)
        return any(rp == _real(r) or rp.startswith(_real(r) + os.sep) for r in D_ROOTS)
    except Exception:
        return False


def is_under_mnt_d(path):
    try:
        rp = _real(path)
        return rp == "/mnt/d" or rp.startswith("/mnt/d/")
    except Exception:
        return False


def sub_and_args(tok):
    i = 1
    while i < len(tok) and tok[i].startswith("-"):
        i += 1 if tok[i] not in TAKES_ARG else 2
    return (tok[i], tok[i + 1:]) if i < len(tok) else (None, [])


def d_offence(tok):
    """Reason for verbs refused on the D:\\ tree specifically, else None."""
    sub, args = sub_and_args(tok)
    if sub == "checkout" and "--" in args:
        before = args[:args.index("--")]
        if [a for a in before if not a.startswith("-")]:
            return "`git checkout <ref> -- <path>` overwrites files from another commit"
    if sub == "restore" and any(a == "-s" or a.startswith("--source")
                                or (a.startswith("-s") and not a.startswith("--"))
                                for a in args):
        return "`git restore --source` overwrites files from another commit"
    return None


def worktree_add_target(tok, cwd):
    """Absolute target path of `git worktree add`, else None."""
    sub, args = sub_and_args(tok)
    if sub != "worktree" or not args or args[0] != "add":
        return None
    skip = False
    for a in args[1:]:
        if skip:
            skip = False
        elif a in ("-b", "-B", "--reason"):
            skip = True
        elif not a.startswith("-"):
            return os.path.join(cwd, os.path.expanduser(a))
    return None


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
    if sub == "reset" and flags & {"--hard", "--merge"}:
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
        where = git_dir_arg(tok)
        where = os.path.join(cwd, where) if where else cwd
        wt = worktree_add_target(tok, where)
        if wt is not None:
            if is_under_mnt_d(wt):
                print(deny("`git worktree add` under /mnt/d: drvfs worktrees are slow "
                           "and corruption-prone"))
                return 0
            continue
        on_d = is_d_path(where)
        why = offence(tok) or (d_offence(tok) if on_d else None)
        if not why or not (on_d or is_shared_tree(where)):
            continue
        print(deny(why))
        return 0
    return 0


def deny(why):
    return json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Blocked by project house rule: %s, and this is the SHARED D:\\ tree "
            "(or a worktree under /mnt/d).\n\n"
            "Other windows have uncommitted work in it. A failed merge "
            "hard-resets the tree internally — it erased 215 files' edits "
            "2026-09-25 07:54 — and a whole-tree reset/checkout/restore/stash/"
            "clean, or a checkout/restore from another ref, does the same directly.\n\n"
            "Work in your ext4 clone instead: /home/mandrake/rm/<seat> "
            "(bench, foundry; git status there is ~0.06 s vs ~15 s on D:\\), "
            "or a private worktree under /home/mandrake/wt/. Publish with "
            "`git pull --rebase origin main && git push origin HEAD:main`.\n"
            "Discard only YOUR paths here (`git checkout -- <file>`, "
            "`git stash push -- <file>`).\n\n"
            "NOTHING IN THAT COMMAND RAN — a compound command is refused whole." % why),
    }})


if __name__ == "__main__":
    sys.exit(main())
