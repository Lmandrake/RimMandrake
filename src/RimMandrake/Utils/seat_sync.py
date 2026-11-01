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
  * every dirty tracked path that upstream also changes either holds upstream's bytes already (it is then
    staged, so --keep accepts it) or merges cleanly with upstream (reset_merging: a peer's live hunks and ledger
    appends stay in the working tree, on top of upstream's); only a real overlap is named and the sync refused;
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
import collections
import ctypes
import fcntl
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


class Refused(Exception):
    pass


def _git_env() -> dict:
    """os.environ as of THIS call plus GIT_LITERAL_PATHSPECS=1: every path this tool hands git is a real repo path,
    never a pattern, so `a[b].txt` must not also match `ab.txt` (review 2026-10-26, SEAT_SYNC_HARDEN_LITERAL_PATHSPECS)."""
    return {**os.environ, "GIT_LITERAL_PATHSPECS": "1"}


class Git:
    def __init__(self, repo: str):
        self.repo = repo

    def run(self, *a, check=True, inp: str | None = None) -> str:
        r = subprocess.run(["git", "-C", self.repo, *a], capture_output=True, text=True, input=inp, env=_git_env())
        if check and r.returncode:
            raise Refused(f"git {' '.join(a[:3])} failed: {(r.stderr or r.stdout).strip()[-600:]}")
        return r.stdout

    def ok(self, *a) -> bool:
        return subprocess.run(["git", "-C", self.repo, *a], capture_output=True, env=_git_env()).returncode == 0

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
        # 0 = some ignored, 1 = none; anything else means the check never ran, and treating that as
        # "nothing to keep" would let reset --keep delete every file upstream merely stopped tracking.
        if r.returncode not in (0, 1):
            raise Refused(f"check-ignore against upstream's .gitignore failed (exit {r.returncode}): "
                          f"{(r.stderr or '').strip()[-300:]}; cannot tell which files upstream stopped tracking")
        return sorted(x for x in r.stdout.split("\0") if x)


def _check_displaced(g: Git, head: str, target: str) -> None:
    """After `reset --keep`: proof it replaced the commit we meant to replace. A peer's bare `git commit` can land between
    any check and git reading HEAD, and no lock here covers it, so the branch would silently lose that commit. ORIG_HEAD
    says what was really replaced: pin it, so it can never be pruned, and say so."""
    orig = g.run("rev-parse", "-q", "--verify", "ORIG_HEAD", check=False).strip()
    if orig and orig != head and orig != target:
        g.run("update-ref", f"refs/rm-rescued/{orig}", orig)
        raise Refused(f"a commit landed during the move: {orig[:12]} is no longer on the branch but is kept at "
                      f"refs/rm-rescued/{orig}. Run `git cherry-pick {orig[:12]}`, then re-run.")


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
        _check_displaced(g, head, target)
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
    _check_displaced(g, head, target)
    notes.append(f"{len(keep)} file(s) upstream stopped tracking kept on disk")
    return "; ".join(notes)


# ---- moving main under live dirty files -------------------------------------------------------------------------
# PUBLISH_SHARDS_FIX_APPENDS_BLOCK_LANDING. A bare `reset --keep` refuses on any dirty file the move would rewrite, and
# in a live clone there always is one: a shard a helper is appending to, or a peer's half-done hunks. One such file
# held bench 19 behind origin. And for a CLEAN shard --keep is not safe either: git unlinks and rewrites the file, so
# an append that opened the old inode vanishes.
# The move below never lets git touch these files. The merged bytes go into the working tree first, in place or by
# compare-and-swap; only then is each path's INDEX entry set to the target blob. `reset --keep` then keeps it without
# looking at the working tree (two-way merge cases 18/19: index already equals the target), so the file keeps its inode.
# The order is the safety. If we die anywhere, the working tree already holds everything (the peer's bytes plus
# upstream's), a later run merges to the same result, and nothing has to be replayed.
PARK_DIR = "rm-dirty-parked"


class DirtyConflict(Refused):
    """A dirty file really overlaps upstream. Nothing was changed. `paths` names them."""
    def __init__(self, paths: list[str]):
        super().__init__("dirty file(s) that really overlap upstream's change: " + ", ".join(paths[:8])
                         + ("" if len(paths) <= 8 else " ..."))
        self.paths = paths


def union_paths(g: Git, paths: list[str]) -> set[str]:
    """The paths .gitattributes marks merge=union (the append-only shards)."""
    if not paths:
        return set()
    f = g.run("check-attr", "-z", "--stdin", "merge", inp="\0".join(paths) + "\0").split("\0")
    return {f[i] for i in range(0, len(f) - 2, 3) if f[i + 2] == "union"}


def union_delta(ours: bytes, base: bytes, theirs: bytes) -> bytes | None:
    """The bytes to APPEND so `ours` also holds everything in `theirs`, or None if these are not plain appends (a base
    line gone from either side, or a torn last line that no line of `theirs` finishes). Counted, not collapsed, but a
    line both sides appended is held once, as git's own union merge does: every event carries seat and timestamp, so
    equal bytes are the same record. A tail `theirs` finishes is a carry that died mid-write: this run completes it."""
    if theirs and not theirs.endswith(b"\n"):
        return None
    tail, rest = ours[ours.rfind(b"\n") + 1:], b""
    if tail:
        whole = next((ln for ln in theirs.splitlines(True) if ln.startswith(tail)), None)
        if whole is None:
            return None
        rest = whole[len(tail):]
        ours += rest
    co, ct = (collections.Counter(b.splitlines(True)) for b in (ours, theirs))
    if any(co[ln] < n or ct[ln] < n for ln, n in collections.Counter(base.splitlines(True)).items()):
        return None
    owed = ct - co
    out = []
    for ln in theirs.splitlines(True):
        if owed[ln]:
            owed[ln] -= 1
            out.append(ln)
    return rest + b"".join(out)


def merge3(ours: bytes, base: bytes, theirs: bytes) -> bytes | None:
    """git merge-file on bytes: the clean result, or None on any overlap, binary file or error."""
    with tempfile.TemporaryDirectory() as td:
        names = []
        for n, b in (("ours", ours), ("base", base), ("theirs", theirs)):
            names.append(os.path.join(td, n))
            Path(names[-1]).write_bytes(b)
        r = subprocess.run(["git", "merge-file", "-p", *names], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _read_wt(g: Git, p: str) -> bytes | None:
    full = os.path.join(g.repo, p)
    if os.path.islink(full) or not os.path.isfile(full):
        return None
    return Path(full).read_bytes()


def _read_shard(g: Git, p: str) -> bytes | None:
    """A shard as of no append in flight: the lock model.append takes, so the preview never sees half a line."""
    full = os.path.join(g.repo, p)
    if os.path.islink(full) or not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        return f.read()


def _blob(g: Git, sha: str) -> bytes:
    return subprocess.run(["git", "-C", g.repo, "cat-file", "blob", sha], capture_output=True, check=True).stdout


def dirty_merges(g: Git, head: str, target: str, keep: list[str]) -> tuple[list[dict], list[str]]:
    """(items the move must carry itself, the paths that cannot be carried). Reads only; changes nothing. Items are
    every dirty path the move would rewrite, plus every shard it would rewrite, because a clean shard can gain an
    append at any moment and must keep its inode."""
    changing = set(g.lines("diff", "--name-only", "-z", "--no-renames", head, target)) - set(keep)
    if not changing:
        return [], []
    dirty = set(g.lines("diff", "--name-only", "-z", "--no-renames", "HEAD")) & changing
    union = union_paths(g, sorted(changing))
    paths = sorted(dirty | union)
    if not paths:
        return [], []
    a, b = {}, {}
    for side, rev in ((a, head), (b, target)):
        for i in range(0, len(paths), 500):
            for rec in g.lines("ls-tree", "-r", "-z", rev, "--", *paths[i:i + 500]):
                meta, q = rec.split("\t", 1)
                mode, _, sha = meta.split()
                side[q] = (mode, sha)
    idx = {}
    for i in range(0, len(paths), 500):
        for rec in g.lines("ls-files", "-s", "-z", "--", *paths[i:i + 500]):
            meta, q = rec.split("\t", 1)
            idx[q] = meta
    items, stuck = [], []
    for p in paths:
        here, there, ours = a.get(p), b.get(p), (_read_shard if p in union else _read_wt)(g, p)
        wt_sha = g.wt_hashes([p]).get(p)
        staged = idx[p].split()[1] if p in idx else None
        if p in idx and idx[p].split()[2] != "0":
            stuck.append(p)                             # unmerged: the index holds stages no single entry can restore
            continue
        if p not in dirty and (not here or not there):
            continue                                    # a clean shard added or deleted upstream: plain reset is right
        if staged not in (wt_sha, here and here[1], there and there[1]) and not (
                # `git commit -- path` reads the file twice, so a live shard leaves an older snapshot in the index
                ours is not None and p in union and union_delta(ours, b"", _blob(g, staged)) == b""):
            stuck.append(p)                             # a third version sits in the index: not ours to drop
            continue
        it = {"path": p, "mode": there and there[0], "blob": there and there[1], "base": here and here[1],
              "index": idx.get(p), "union": p in union, "dirty": p in dirty}
        if there and wt_sha == there[1] and there[0].startswith("100") and (not here or here[0] == there[0]):
            items.append(it)                            # already upstream's bytes: only the index moves
            continue
        if not here or not there or ours is None or here[0] != there[0] or not here[0].startswith("100"):
            stuck.append(p)                             # added, deleted, symlink, mode change: no merge is defined
            continue
        base, theirs = _blob(g, here[1]), _blob(g, there[1])
        if union_delta(ours, base, theirs) is not None if p in union else merge3(ours, base, theirs) is not None:
            items.append(it)
        elif p in dirty:
            stuck.append(p)
        # else a clean shard rewritten upstream, not appended to: plain reset is right (shards are append-only by
        # contract, so this and the added/deleted case above are a retirement, not traffic)
    return items, stuck


def _exchange(a: Path | str, b: Path | str) -> None:
    """Swap two paths atomically (renameat2 RENAME_EXCHANGE), so what `b` held at that instant survives in `a`. A plain
    rename would destroy a save landing after the last compare. No fallback: the clones are on ext4, and a filesystem
    without it refuses rather than races."""
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.renameat2(-100, os.fsencode(a), -100, os.fsencode(b), 2):   # AT_FDCWD, AT_FDCWD, RENAME_EXCHANGE
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(b))


def _carry(g: Git, it: dict, park: Path) -> None:
    """Put upstream's change into the working file, keeping whatever is there NOW. Shards: one O_APPEND write under the
    lock model.append takes on the same file, so a live append can land before or after but never lost; the inode
    stays, always: an appender may hold it open. Others: an atomic swap, then proof of what the swap displaced, and a
    save that slipped in goes back and is merged again. A real overlap raises DirtyConflict before the branch moves."""
    p, full = it["path"], os.path.join(g.repo, it["path"])
    if it["base"] is None:                              # no base means the preview found upstream's bytes already here
        return
    base, theirs = _blob(g, it["base"]), _blob(g, it["blob"])
    if it["union"]:
        fd = os.open(full, os.O_RDWR | os.O_APPEND)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            ours = b""
            while chunk := os.read(fd, 1 << 20):
                ours += chunk
            delta = union_delta(ours, base, theirs)
            if delta is not None:
                view = memoryview(delta)
                while view:
                    view = view[os.write(fd, view):]
                return
        finally:
            os.close(fd)                                # closing releases the flock
        raise DirtyConflict([p])
    tmp = park / f"swap-{hashlib.sha1(p.encode()).hexdigest()}.tmp"   # per path: two files can share a target blob
    for _ in range(5):
        cur = _read_wt(g, p)
        merged = None if cur is None else (cur if cur == theirs else merge3(cur, base, theirs))
        if merged is None:
            raise DirtyConflict([p])
        if merged == cur:
            return
        tmp.write_bytes(merged)
        shutil.copymode(full, tmp)
        if _read_wt(g, p) != cur:
            continue
        _exchange(tmp, full)
        if tmp.read_bytes() == cur:
            it["displaced"] = (tmp, cur)                # read again before the park goes: see reset_merging
            return
        _exchange(tmp, full)                            # a save landed in the gap: it goes back, and we merge again
        if tmp.read_bytes() != merged:                  # and a second one landed: tmp holds it, the park keeps it
            tmp.rename(park / f"late-{it['blob']}.save")
            raise DirtyConflict([p])
    raise DirtyConflict([p])


def reset_merging(g: Git, head: str, target: str, keep: list[str] | None = None) -> str:
    """reset_keep that carries live dirty files across the move instead of refusing on them (see the block above).
    Raises DirtyConflict, with nothing changed, only on a real overlap. Each dirty file's bytes are parked under
    .git/rm-dirty-parked/ first and stay there if anything fails after the first write."""
    if keep is None:
        keep = untracked_upstream(g, head, target)
    items, stuck = dirty_merges(g, head, target, keep)
    if stuck:
        raise DirtyConflict(stuck)
    if not items:
        return reset_keep(g, head, target, keep)
    parks = Path(g.run("rev-parse", "--absolute-git-dir").strip()) / PARK_DIR
    left = sorted(d.name for d in parks.iterdir()) if parks.is_dir() else []    # a run that died: its originals stay
    park = parks / f"{time.strftime('%Y%m%d_%H%M%S')}-{os.getpid()}-{os.urandom(3).hex()}"
    for it in items:
        if it["dirty"] and os.path.isfile(os.path.join(g.repo, it["path"])):
            dst = park / it["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(os.path.join(g.repo, it["path"]), dst)
    park.mkdir(parents=True, exist_ok=True)
    for it in items:
        _carry(g, it, park)
    if g.run("rev-parse", "HEAD").strip() != head:
        raise Refused(f"HEAD moved under the merge of {len(items)} dirty file(s); not resetting. Their merged bytes are "
                      f"in the working tree, originals in {park}. Nothing was lost; re-run.")
    g.run("update-index", "-z", "--index-info",
          inp="".join(f"{it['mode']} {it['blob']}\t{it['path']}\0" for it in items))
    try:
        note = reset_keep(g, head, target, keep)
    except Refused as e:
        back = "".join((f"{it['index'].split()[0]} {it['index'].split()[1]}\t{it['path']}\0" if it["index"]
                        else f"0 {'0' * 40}\t{it['path']}\0") for it in items)
        g.run("update-index", "-z", "--index-info", inp=back)
        raise Refused(f"{e} (the {len(items)} carried file(s) already hold upstream's change, originals in {park})")
    # An editor that held the old file open writes to the displaced inode, not the path: keep that, like any late save.
    late = [i["path"] for i in items if "displaced" in i and i["displaced"][0].read_bytes() != i["displaced"][1]]
    if not late:
        shutil.rmtree(park, ignore_errors=True)
    done = f"{sum(1 for i in items if i['dirty'])} dirty file(s) merged in place, {len(items)} carried past git"
    if late:
        done += f"; WRITE LANDED ON THE OLD FILE, {', '.join(late)}: it is in {park}, merge it by hand"
    if left:
        done += f"; {len(left)} older set(s) of parked originals still in {parks}, read them before deleting"
    return f"{note}; {done}" if note else done


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
    p = {"head": head, "up": up, "local": [], "stage": [], "move": [], "keep": [], "merge": [], "already": head == up}
    if head == up:
        return p
    # 1. local commits must already be upstream
    cherry = {ln[2:].split()[0]: ln[0] for ln in g.lines("cherry", up, head)}
    for c in g.lines("rev-list", "--reverse", f"{up}..{head}"):
        subj = g.run("show", "-s", "--format=%h %s", c).strip()
        if cherry.get(c) == "-":
            p["local"].append((subj, "patch-equivalent"))
            continue
        parents = g.run("rev-list", "--parents", "-n1", c).split()[1:]
        touched = (g.lines("diff", "--name-only", "-z", "--no-renames", parents[0], c) if len(parents) > 1
                   else g.lines("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root", c))
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
        p["stage"] = [d for d in dl if d not in bad]
        stuck = set(dirty_merges(g, head, up, p["keep"])[1])
        if stuck:
            bl = sorted(stuck)
            raise Refused(f"{len(bl)} dirty file(s) really overlap upstream's change: "
                          + ", ".join(bl[:8]) + ("" if len(bl) <= 8 else " ...")
                          + ". Publish or move aside YOUR edit to those paths, then sync")
        p["merge"] = [d for d in bad]
    # 4. untracked files where upstream adds a file
    added = set(g.lines("diff", "--name-only", "-z", "--no-renames", "--diff-filter=A", head, up))
    al, untracked = sorted(added), set()
    for i in range(0, len(al), 500):    # chunked like blobs(): a big landing would overflow one argv (E2BIG)
        untracked.update(g.lines("ls-files", "-z", "--others", "--", *al[i:i + 500]))
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
    try:
        note = reset_merging(g, p["head"], p["up"], p["keep"])
    except Refused as e:   # say what already happened (moved files, backup branch) before the refusal
        raise Refused(f"{e}" + (f" (already done: {'; '.join(notes)})" if notes else ""))
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
        if p["merge"]:
            print(f"  {len(p['merge'])} dirty path(s) merge cleanly with upstream (will be carried in place)")
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
