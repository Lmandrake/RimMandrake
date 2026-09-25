#!/usr/bin/env python3
"""Selftest for block_shared_tree_merge.py — run after ANY change to it.

Builds a throwaway repo with a linked worktree, so "shared" (main worktree) and
"private" (linked worktree) are both real, then feeds the hook each command.

    python3 .claude/hooks/selftest_block_shared_tree_merge.py
"""
import json
import os
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "block_shared_tree_merge.py")
DENY, ALLOW = "deny", "allow"


def verdict(cmd, cwd):
    out = subprocess.run([sys.executable, HOOK], capture_output=True, text=True,
                         input=json.dumps({"tool_input": {"command": cmd},
                                           "cwd": cwd})).stdout
    return DENY if '"deny"' in out else ALLOW


def main():
    tmp = tempfile.mkdtemp()
    main_wt, linked = os.path.join(tmp, "main"), os.path.join(tmp, "linked")
    g = lambda *a: subprocess.run(["git", *a], cwd=main_wt, check=True,
                                  capture_output=True)
    os.makedirs(main_wt)
    g("init", "-q"); g("-c", "user.name=t", "-c", "user.email=t@t",
                       "commit", "-q", "--allow-empty", "-m", "x")
    g("worktree", "add", "-q", "--detach", linked)
    sub = os.path.join(main_wt, "sub"); os.makedirs(sub)

    S, P = main_wt, linked
    cases = [
        (DENY,  "git merge origin/foundry/x --no-edit", S),
        (DENY,  "git merge --no-ff feature", S),
        (DENY,  "git merge --squash feature", S),
        (DENY,  "git pull", S),
        (DENY,  "git pull origin main", S),
        (DENY,  "git fetch origin && git merge origin/main", S),
        (DENY,  "git merge feature", sub),                 # subdir of shared
        (DENY,  "git -C %s merge feature" % S, P),         # -C into shared
        (DENY,  "cd %s && git merge feature" % S, P),      # cd into shared
        (DENY,  "git pull --rebase --autostash", S),
        (DENY,  "git rebase --autostash origin/main", S),
        (DENY,  "git reset --hard HEAD", S),
        (DENY,  "git reset --merge", S),
        (DENY,  "git checkout -- .", S),
        (DENY,  "git checkout .", S),
        (DENY,  "git checkout -f main", S),
        (DENY,  "git restore .", S),
        (DENY,  "git restore --worktree --staged .", S),
        (DENY,  "git stash", S),
        (DENY,  "git stash push -m wip", S),
        (DENY,  "git stash -u", S),
        (DENY,  "git clean -fd", S),
        (DENY,  "git checkout-index -f -a", S),
        (ALLOW, "git reset --hard HEAD", P),
        (ALLOW, "git reset HEAD -- f.txt", S),
        (ALLOW, "git reset --soft HEAD~1", S),
        (ALLOW, "git checkout -- src/a.xml", S),
        (ALLOW, "git restore --staged .", S),
        (ALLOW, "git restore src/a.xml", S),
        (ALLOW, "git stash push -m mine -- src/a.xml", S),
        (ALLOW, "git stash list", S),
        (ALLOW, "git stash show -p stash@{0}", S),
        (ALLOW, "git clean -n", S),
        (ALLOW, "git checkout-index -f -- infrastructure/state/ledger/events/BENCH.jsonl", S),
        (ALLOW, "git merge --ff-only origin/main", S),
        (ALLOW, "git merge --abort", S),
        (ALLOW, "git merge --continue", S),
        (ALLOW, "git pull --ff-only", S),
        (ALLOW, "git pull --rebase", S),
        (ALLOW, "git pull -r origin main", S),
        (ALLOW, "git merge-base HEAD origin/main", S),
        (ALLOW, "git merge feature", P),                   # private worktree
        (ALLOW, "cd %s && git merge feature" % P, S),      # cd into private
        (ALLOW, "git -C %s pull" % P, S),
        (ALLOW, "echo 'git merge is banned here'", S),
        (ALLOW, "git log --merges", S),
    ]
    bad = 0
    for want, cmd, cwd in cases:
        got = verdict(cmd, cwd)
        if got != want:
            bad += 1
            print("FAIL want=%s got=%s  %s  (cwd=%s)" % (want, got, cmd, cwd))
    print("%d/%d passed" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
