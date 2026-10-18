#!/usr/bin/env python3
"""seat_sync.py — bring a seat clone's local main level with origin/main, losing nothing.   (./sync)

    ./sync                 fetch, then realign main to origin/main when it is provably safe
    ./sync --dry-run       say what it would do, change nothing
    ./sync --no-fetch      use the origin/main ref already present (land.sh calls it this way after a push)
    ./sync --repo DIR      a clone other than the one the cwd is in

Why: land.sh publishes by plumbing, so the clone's main still carries the unpublished originals and reads
"ahead N, behind M" with patch-equivalent duplicates; and `git pull --rebase` refuses on ANY dirty file,
which a seat clone always has. This replaces the manual realign ritual and reconcile_clone.py.

The primitive is `git reset --keep origin/main`: it moves main and the index, rewrites only files that
differ between HEAD and origin/main, and REFUSES (changing nothing) rather than touch a dirty one.
Before it runs, every precondition is checked and the whole plan is refused if one fails:
  * on branch main, no rebase/merge/cherry-pick in progress;
  * every local commit (origin/main..HEAD) is already upstream: patch-equivalent per `git cherry`, or
    content-equivalent (every path it touches has the same bytes at HEAD and origin/main);
  * every dirty tracked path that upstream also changes already holds upstream's bytes (it is then staged,
    so --keep accepts it); a dirty path with OTHER bytes is named and the sync refused;
  * an untracked file at a path upstream adds is moved aside only when byte-identical to upstream's copy;
  * a file upstream STOPPED TRACKING (deleted from the tree and ignored by upstream's .gitignore files, e.g.
    Transient/ since 2026-10-18) is KEPT on disk with its local bytes: it is renamed aside inside .git,
    dropped from the index, and renamed back after the reset. A plain `reset --keep` would delete it.
Local commits are kept on a backup branch `backup/<seat>-pre-sync-<stamp>-<sha>`; moved files go to
~/.seat-tmp/<SEAT>/sync_<stamp>/. Never stashes, never --hard, never touches an unrelated dirty file.
Prints `SYNCED <old> -> <new>`, `IN SYNC <sha>`, or `REFUSED: <why>` (exit 1).

    python3 src/RimMandrake/Utils/selftest_seat_sync.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


class Refused(Exception):
    pass


class Git:
    def __init__(self, repo: str):
        self.repo = repo

    def run(self, *a, check=True, inp: str | None = None) -> str:
        r = subprocess.run(["git", "-C", self.repo, *a], capture_output=True, text=True, input=inp)
        if check and r.returncode:
            raise Refused(f"git {' '.join(a[:3])} failed: {(r.stderr or r.stdout).strip()[-600:]}")
        return r.stdout

    def ok(self, *a) -> bool:
        return subprocess.run(["git", "-C", self.repo, *a], capture_output=True).returncode == 0

    def lines(self, *a) -> list[str]:
        return [x for x in self.run(*a).split("\0" if "-z" in a else "\n") if x]

    def blobs(self, rev: str, paths: list[str]) -> dict[str, str]:
        """path -> blob sha at rev (absent paths omitted)."""
        out: dict[str, str] = {}
        for i in range(0, len(paths), 500):
            for rec in self.lines("ls-tree", "-r", "-z", rev, "--", *paths[i:i + 500]):
                meta, p = rec.split("\t", 1)
                out[p] = meta.split()[2]
        return out

    def wt_hashes(self, paths: list[str]) -> dict[str, str]:
        """path -> blob sha of the working-tree file (absent / non-file paths omitted)."""
        files = [p for p in paths if os.path.isfile(os.path.join(self.repo, p)) and not os.path.islink(os.path.join(self.repo, p))]
        if not files:
            return {}
        hs = self.run("hash-object", "--stdin-paths", inp="\n".join(files) + "\n").split()
        return dict(zip(files, hs))


def untracked_upstream(g: Git, head: str, up: str) -> list[str]:
    """Paths upstream deleted from the tree that its own .gitignore files now ignore and that still
    exist here: the files a stop-tracking commit (`git rm --cached` + ignore) means to leave on disk.
    Judged against UPSTREAM's .gitignore blobs, written into a throwaway dir, because the worktree's
    .gitignore is still the old one until the reset runs."""
    gone = g.lines("diff", "--name-only", "-z", "--no-renames", "--diff-filter=D", head, up)
    here = [p for p in gone if os.path.lexists(os.path.join(g.repo, p))]
    if not here:
        return []
    igs = [p for p in g.lines("ls-tree", "-r", "-z", "--name-only", up)
           if p == ".gitignore" or p.endswith("/.gitignore")]
    if not igs:
        return []
    with tempfile.TemporaryDirectory() as td:
        for ig in igs:
            dst = Path(td) / ig
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(subprocess.run(["git", "-C", g.repo, "cat-file", "blob", f"{up}:{ig}"],
                                           capture_output=True, check=True).stdout)
        subprocess.run(["git", "-C", td, "init", "-q"], capture_output=True, check=True)
        r = subprocess.run(["git", "-C", td, "check-ignore", "--no-index", "-z", "--stdin"],
                           input="\0".join(here) + "\0", capture_output=True, text=True)
        return sorted(x for x in r.stdout.split("\0") if x)


def reset_keep(g: Git, head: str, target: str, keep: list[str] | None = None) -> str:
    """`git reset --keep <target>` that never deletes a file upstream merely STOPPED TRACKING.

    Each such file (see untracked_upstream) is renamed aside inside .git (same filesystem, so instant even
    for 25k files), dropped from the index so --keep sees index == target, the reset runs, and every file
    is renamed back. Raises Refused (with index and files restored) if the reset itself refuses.
    publish.py calls this too, so both ways a seat clone moves main keep the files."""
    if keep is None:
        keep = untracked_upstream(g, head, target)
    if not keep:
        g.run("reset", "-q", "--keep", target)
        return ""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    aside = Path(g.run("rev-parse", "--absolute-git-dir").strip()) / f"rm-untrack-keep-{stamp}"
    moved, notes = [], []
    nul = "\0".join(keep) + "\0"
    try:
        for k in keep:
            dst = aside / k
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.rename(os.path.join(g.repo, k), dst)
            moved.append(k)
        g.run("rm", "-q", "--cached", "--ignore-unmatch", "--pathspec-from-file=-", "--pathspec-file-nul", inp=nul)
        try:
            g.run("reset", "-q", "--keep", target)
        except Refused:
            g.run("reset", "-q", "--pathspec-from-file=-", "--pathspec-file-nul", inp=nul)
            raise
    finally:
        stuck = []
        for k in moved:
            src, dst = aside / k, Path(g.repo) / k
            if os.path.lexists(dst):
                stuck.append(k)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.rename(src, dst)
        if not stuck:
            shutil.rmtree(aside, ignore_errors=True)
        else:
            notes.append(f"{len(stuck)} kept file(s) could not go back (path re-created); copies in {aside}")
    notes.append(f"{len(keep)} file(s) upstream stopped tracking kept on disk")
    return "; ".join(notes)


def plan(g: Git) -> dict:
    gd = Path(g.run("rev-parse", "--absolute-git-dir").strip())
    for marker in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
        if (gd / marker).exists():
            raise Refused(f"a {marker} is in progress in {g.repo}; finish or abort it first")
    branch = g.run("symbolic-ref", "-q", "--short", "HEAD", check=False).strip()
    if branch != "main":
        raise Refused(f"HEAD is on '{branch or 'detached'}', not main")
    head = g.run("rev-parse", "HEAD").strip()
    up = g.run("rev-parse", "refs/remotes/origin/main").strip()
    p = {"head": head, "up": up, "local": [], "stage": [], "move": [], "keep": [], "already": head == up}
    if head == up:
        return p
    # 1. local commits must already be upstream
    cherry = {ln[2:].split()[0]: ln[0] for ln in g.lines("cherry", up, head)}
    for c in g.lines("rev-list", "--reverse", f"{up}..{head}"):
        subj = g.run("show", "-s", "--format=%h %s", c).strip()
        if cherry.get(c) == "-":
            p["local"].append((subj, "patch-equivalent"))
            continue
        touched = g.lines("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root", c)
        a, b = g.blobs(head, touched), g.blobs(up, touched)
        if all(a.get(t) == b.get(t) for t in touched):
            p["local"].append((subj, "content-equivalent"))
            continue
        diff = [t for t in touched if a.get(t) != b.get(t)]
        raise Refused(f"local commit {subj} is NOT on origin/main ({len(diff)} path(s) differ, e.g. {diff[0]}). "
                      f"Land it first (land.sh <sha> <paths>), then sync")
    # 2. files upstream stopped tracking stay on disk (with any local edit), so they never block the move
    p["keep"] = untracked_upstream(g, head, up)
    # 3. dirty tracked paths that the move would rewrite
    changing = set(g.lines("diff", "--name-only", "-z", "--no-renames", head, up)) - set(p["keep"])
    dirty = set(g.lines("diff", "--name-only", "-z", "--no-renames", "HEAD")) & changing
    if dirty:
        dl = sorted(dirty)
        ub, wt = g.blobs(up, dl), g.wt_hashes(dl)
        bad = [d for d in dl if ub.get(d) != wt.get(d)]
        if bad:
            raise Refused(f"{len(bad)} dirty file(s) that upstream also changes hold other bytes: "
                          + ", ".join(bad[:8]) + ("" if len(bad) <= 8 else " ...")
                          + ". Publish or move aside YOUR edit to those paths, then sync")
        p["stage"] = dl
    # 4. untracked files where upstream adds a file
    added = set(g.lines("diff", "--name-only", "-z", "--no-renames", "--diff-filter=A", head, up))
    untracked = set(g.lines("ls-files", "-z", "--others", "--", *sorted(added))) if added else set()
    if untracked:
        ul = sorted(untracked)
        ub, wt = g.blobs(up, ul), g.wt_hashes(ul)
        bad = [u for u in ul if ub.get(u) != wt.get(u)]
        if bad:
            raise Refused(f"{len(bad)} untracked file(s) sit where upstream adds a DIFFERENT file: "
                          + ", ".join(bad[:8]) + ". Move them aside yourself, then sync")
        p["move"] = ul
    return p


def apply(g: Git, p: dict, seat: str) -> str:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    notes = []
    if p["local"]:
        br = f"backup/{seat}-pre-sync-{stamp}-{p['head'][:7]}"
        if not g.ok("rev-parse", "-q", "--verify", f"refs/heads/{br}"):
            g.run("branch", br, p["head"])
        notes.append(f"backup branch {br}")
    if p["move"]:
        dest = Path.home() / ".seat-tmp" / seat.upper() / f"sync_{stamp}"
        for u in p["move"]:
            (dest / u).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(os.path.join(g.repo, u), dest / u)
        notes.append(f"{len(p['move'])} identical untracked file(s) moved to {dest}")
    for i in range(0, len(p["stage"]), 500):
        g.run("add", "-A", "--", *p["stage"][i:i + 500])
    note = reset_keep(g, p["head"], p["up"], p["keep"])
    if note:
        notes.append(note)
    return "; ".join(notes)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    start = a.repo or os.getcwd()
    r = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode:
        print(f"REFUSED: {start} is not inside a git clone")
        return 1
    g = Git(r.stdout.strip())
    seat = os.path.basename(g.repo)
    try:
        if not a.no_fetch:
            g.run("fetch", "-q", "origin")
        p = plan(g)
        if p["already"]:
            print(f"IN SYNC {p['head'][:9]}")
            return 0
        for subj, how in p["local"]:
            print(f"  local {subj}  [{how}]")
        if p["stage"]:
            print(f"  {len(p['stage'])} dirty path(s) already hold upstream's bytes (will be staged)")
        if p["move"]:
            print(f"  {len(p['move'])} untracked file(s) identical to upstream's (will be moved aside)")
        if p["keep"]:
            print(f"  {len(p['keep'])} file(s) upstream stopped tracking (will stay on disk, now ignored)")
        if a.dry_run:
            print(f"WOULD SYNC {p['head'][:9]} -> {p['up'][:9]}")
            return 0
        note = apply(g, p, seat)
    except Refused as e:
        print(f"REFUSED: {e}")
        return 1
    print(f"SYNCED {p['head'][:9]} -> {p['up'][:9]}" + (f"  ({note})" if note else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
