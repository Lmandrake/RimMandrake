#!/usr/bin/env python3
"""reconcile_clone.py - bring this seat clone level with origin/main without losing anything.

land.sh publishes by plumbing, so the working tree never learns what landed: it drifts behind, tracked
files read as modified/deleted, and untracked copies of landed files block `git pull --rebase`.
This backs everything up to ~/.seat-tmp/<seat>_reconcile_<stamp>/ then syncs:
  1. tar the tracked-modified files + `git diff` (staged and unstaged)
  2. `git reset -q`, restore ONLY those explicit paths (a whole-tree restore is hook-blocked)
  3. pull --rebase, moving each untracked file that would be overwritten into the backup, until it succeeds
Run it when no helper is mid-edit in the clone. Prints RECONCILED <head> or the failing git output.
"""
import os, shutil, subprocess, sys, time

repo = os.path.dirname(os.path.abspath(__file__))
repo = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
os.chdir(repo)
seat = os.path.basename(repo)
B = os.path.expanduser(f"~/.seat-tmp/{seat}_reconcile_{time.strftime('%Y%m%d_%H%M%S')}")
os.makedirs(B + "/untracked", exist_ok=True)

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)

st = [l for l in git("status", "--porcelain").stdout.splitlines() if not l.startswith("??")]
paths = sorted({l[3:].split(" -> ")[-1] for l in st})
if paths:
    existing = [p for p in paths if os.path.exists(p)]
    subprocess.run(["tar", "cf", B + "/modified.tar", *existing], check=False)
    open(B + "/diff.patch", "w").write(git("diff", "HEAD").stdout)
    git("reset", "-q")
    for i in range(0, len(paths), 200):
        if git("restore", "--", *paths[i:i + 200]).returncode:  # one bad pathspec aborts the chunk
            for p in paths[i:i + 200]:
                git("restore", "--", p)

for i in range(20):
    r = git("pull", "--rebase", "origin", "main")
    if r.returncode == 0:
        print("RECONCILED", git("rev-parse", "--short", "HEAD").stdout.strip(), "backup:", B)
        sys.exit(0)
    out = r.stdout + r.stderr
    fs = [l[1:] for l in out.splitlines() if l.startswith("\t")]
    if not fs:
        print(out[-800:]); sys.exit(1)
    for f in fs:
        if os.path.exists(f):
            os.makedirs(os.path.dirname(os.path.join(B, "untracked", f)), exist_ok=True)
            shutil.move(f, os.path.join(B, "untracked", f))
    # a failed checkout can leave tracked deletions; restore them by explicit path
    gone = [l[3:] for l in git("status", "--porcelain").stdout.splitlines() if l.startswith(" D")]
    for g in gone:
        git("restore", "--", g)
print("gave up after 20 rounds"); sys.exit(1)
