#!/usr/bin/env python3
"""Commit named paths and land them with plain git — the thin wrapper agents already know.

    ./publish -m "subject" path/one path/two     commit those paths, rebase, push, print PUBLISHED <sha>
    ./publish -F msg.txt path/one                message from a file ('-' = stdin)
    ./publish                                    push local commits already made (no new commit)
    ./publish --ledger -m "subject" <shards>     land only these ledger shards' new lines (land_ledger: no clone lock, no
                                                 peer's commit); any other path takes the ordinary route

It is exactly: `git add --all -- <paths>` + `git commit -- <paths>` (pathspec on the commit, so
nothing else staged rides along) + a replay of the local commits onto origin/main by plumbing, moved
there with `git reset --keep` (never a stash; see rebase()) + push, retried up to MAX_TRIES times when origin
moved under it, never forced. It pushes a seat clone
(/home/mandrake/rm/<seat>) to HEAD:main. Each attempt's fetch, replay and push run under one machine-wide flock
(push_lock: RM_ROOT/.publish-push.lock), so this machine's publishers take turns at the push instead of racing.

A push that fails for any reason other than a clean non-fast-forward is AMBIGUOUS (the remote may
have accepted it before the client gave up): it fetches and checks `merge-base --is-ancestor HEAD
<target>` before retrying, and an ancestor means it landed. A rebase that stops on a real conflict
leaves your commit intact locally and names the conflicted paths; so does an uncommitted edit to a file
origin changed and that really overlaps it. Unrelated dirty files are never touched.

Live dirty files do not stop a landing (PUBLISH_SHARDS_FIX_APPENDS_BLOCK_LANDING). A peer's hunks or a shard being
appended to, in a file origin also moved, are merged in the working tree and the branch moves over them
(seat_sync.reset_merging). If a dirty file REALLY overlaps origin, the replayed commits are still pushed; only the
clone's branch stays where it is, the output says so, and the peer's file is left exactly as it was.

Committed mod DLLs are landed here, never by hand: a replay conflict on ONLY .dll/.dll.srchash pairs takes
origin's side and then rebuilds each such DLL from the source committed at the new HEAD, in a throwaway src-only
`git clone --shared` (never the worktree, so a peer's uncommitted C# cannot leak in), and commits the pair; a
pre-push DLL_SOURCE_STAMP_GUARD_1 refusal does the same rebuild and retries once (rebuild_dlls()).

It REFUSES in the /mnt/d tree: that tree becomes a read-only mirror of origin/main (§2.3), and the
old plumbing route that published from it (temp index, --catchup, --sync, --commit, --worktrees)
is deleted, not kept for emergencies. With no owned clone, make one on ext4.
"""
import argparse
import collections
import concurrent.futures
import contextlib
import fcntl
import fnmatch
import glob
import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

REMOTE, BRANCH = "origin", "main"
OWNER_SHARD = "infrastructure/state/ledger/events/OWNER.jsonl"
RM_ROOT = os.environ.get("PUBLISH_RM_ROOT", "/home/mandrake/rm")
# The race limit: lost push races in a row before a landing refuses. Danger it guards: a push that can never land would
# loop with no end (a remote that rejects for a reason the race test reads as a race, e.g. a protected branch's
# "[rejected]"), holding this clone's publish.lock. Measured need: 8 lost races in a row with ~13 writers landing at once
# (2026-11-24, 6:20 and 6:27 PM PST: the Conductor twice and a helper once refused at the old limit of 8); 10x that.
MAX_TRIES = 80
# A push that failed while origin did not move (not a race) is retried this many times, paused up to 20 s between.
# Danger: an origin that is down or refuses this machine would loop with no end. It is the value the race limit shared
# until 2026-11-24; its need is unmeasured (push_refusal_census.py counts the "push failed (...); retrying" lines).
PUSH_FAIL_TRIES = 8
# The pause after a lost race grows 0.5 s a try up to this top, the pause the old limit reached at its 8th try. Danger:
# uncapped, the pauses of 80 lost races sum to 27 min (0.5 s x 80 x 81 / 2).
# budget: danger=uncapped, the pauses of 80 lost races sum to 27 min; ends no work: a pause between two tries
RACE_PAUSE_MAX_S = 4.0
PUSH_LOCK_NAME = ".publish-push.lock"
# A waiter for the push lock names the holder this often. Not a limit: it waits while the holder lives (the kernel drops
# a flock when its holder exits or is killed), and a holder's own git calls are each bounded by GIT_TIMEOUT_S.
PUSH_LOCK_SAY_S = 30.0     # budget: ends no work: a waiting line on stderr; the wait goes on
GIT_TIMEOUT_S = float(os.environ.get("PUBLISH_GIT_TIMEOUT", "300"))   # one git call, push included; a hang is a loud TimeoutExpired, not a stall
# The tree checks' full clone and checkout write the whole tree: a hang guard only, far above a real run. 300 s was
# reached by that checkout twice at load 40 on 2026-11-24 and refused two publishes.
CHECKTREE_GIT_TIMEOUT_S = float(os.environ.get("PUBLISH_CHECKTREE_GIT_TIMEOUT", "1800"))
before_push = None          # selftest hook: called(attempt) between rebase and push
before_reset = None         # selftest hook: called() between the replay and the HEAD check
LOCK_TIMEOUT = float(os.environ.get("PUBLISH_LOCK_TIMEOUT", "600"))


class Refuse(Exception):
    pass


# A git call that finds .git/index.lock held retries until this many seconds have passed. Danger it guards: a lock a
# killed git left behind never goes away, so an unbounded wait would stall every landing in the clone (2026-11-12: a
# git killed at deploy_update's budget left index.lock and blocked every later pass). A live peer's hold is short: the
# 2026-11-18 failures (7:28 PM, 8:00 PM PST) passed on the next try by hand.
LOCK_WAIT_S = float(os.environ.get("PUBLISH_INDEX_LOCK_WAIT", "60"))
LOCK_HELD_EXIT = 75         # EX_TEMPFAIL: the index lock stayed held; nothing was published; try again


class IndexLockHeld(Refuse):
    """.git/index.lock stayed held past LOCK_WAIT_S. Its text names the holder (pid and command) or says none has it open."""


def lock_holders(top):
    """-> [(pid, command)] of the processes that have this clone's .git/index.lock open, read from /proc/*/fd; or a str
    naming why the lock's path could not be read (could not look is not "nobody holds it")."""
    try:
        r = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=top, capture_output=True, text=True,
                           timeout=30)  # budget: danger=a hung git holds the refusal; longest=1s (one rev-parse)
    except (OSError, subprocess.SubprocessError) as e:
        return "git rev-parse: %s" % e
    if r.returncode or not r.stdout.strip():
        return "git rev-parse: %s" % (r.stderr.strip() or "no git dir")
    lock = os.path.realpath(os.path.join(r.stdout.strip(), "index.lock"))
    out = []
    for d in glob.glob("/proc/[0-9]*/fd/*"):
        try:
            if os.readlink(d) != lock:
                continue
        except OSError:
            continue
        pid = int(d.split("/")[2])
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
        except OSError:
            cmd = "?"
        if (pid, cmd) not in out:
            out.append((pid, cmd))
    return out


def lock_wait(top, attempt, started):
    """After a git call failed on a held index.lock: sleep and return True to retry, or raise IndexLockHeld."""
    if time.monotonic() - started >= LOCK_WAIT_S:
        held = lock_holders(top)
        raise IndexLockHeld("%s/.git/index.lock stayed held for %d s; %s. Nothing was published. Run ./publish again "
                            "once it is free." % (
                                top, LOCK_WAIT_S,
                                "who holds it could not be read (%s)" % held if isinstance(held, str) else
                                "held by " + "; ".join("pid %d: %s" % h for h in held) if held else
                                "no process has it open: a git that was killed left it (remove it only when no git "
                                "runs in this clone)"))
    time.sleep(min(0.25 * (attempt + 1), 2.0))
    return True


class Stranded(Refuse):
    """The replay at `tip` is good but a dirty file really overlaps it, so this clone's branch cannot move yet."""
    def __init__(self, why, tip):
        super().__init__(why)
        self.tip = tip


HOOKED = ("commit", "push")                              # git calls that run this repo's hooks


def git_env(**extra):
    """os.environ plus GIT_LITERAL_PATHSPECS=1: every path publish hands git is a real repo path, never a pattern, so
    `./publish a[b].txt` must not also commit `ab.txt` (Codex, 2026-11-01; seat_sync has done this since 2026-10-26).
    🔴 Never for a call that runs hooks: they inherit the env, and a hook's own glob (game_art.py's `-- '*.html'`)
    would then match nothing and pass. commit() spells its paths `:(literal)` instead."""
    return dict(os.environ, GIT_LITERAL_PATHSPECS="1", **extra)


def literal(paths):
    return [":(literal)" + p for p in paths]


def run(top, *args, check=True):
    env = None if args[:1] and args[0] in HOOKED else git_env()
    started, i = time.monotonic(), 0
    while True:                                          # a plain-git peer may hold .git/index.lock (LOCK_WAIT_S)
        r = subprocess.run(["git", *args], cwd=top, capture_output=True, text=True, errors="surrogateescape",
                           timeout=GIT_TIMEOUT_S, env=env)
        if not (r.returncode and "index.lock" in r.stderr):
            break
        if not check and time.monotonic() - started >= LOCK_WAIT_S:
            break
        lock_wait(top, i, started)
        i += 1
    if check and r.returncode:
        raise Refuse("git %s failed: %s" % (" ".join(args[:3]), (r.stderr or r.stdout).strip()))
    return r


def out(top, *args):
    return run(top, *args).stdout.strip()


def lock_path(top):
    return os.path.join(out(top, "rev-parse", "--absolute-git-dir"), "publish.lock")


@contextlib.contextmanager
def clone_lock(top):
    """Clone-wide exclusive flock held across commit AND land, so two publishers in one clone never interleave
    (a peer's commit landing between rebase()'s read of HEAD and its reset used to vanish). The kernel drops a
    flock when its holder exits or is killed, so a crashed publisher cannot wedge the clone. Times out loudly."""
    fd = os.open(lock_path(top), os.O_CREAT | os.O_RDWR, 0o644)
    deadline = time.time() + LOCK_TIMEOUT
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.time() >= deadline:
                    raise Refuse("could not take the publish lock %s within %gs: another ./publish in this clone is "
                                 "still running. Nothing was committed. Re-run when it finishes."
                                 % (lock_path(top), LOCK_TIMEOUT))
                time.sleep(0.2)
        yield
    finally:
        os.close(fd)                                     # closing releases the flock


def push_lock_path():
    return os.path.join(RM_ROOT, PUSH_LOCK_NAME)


class PushLock:
    """The machine-wide exclusive flock one attempt holds across its fetch, replay and push (2026-11-24: ./publish lost
    the race 8 times in a row and refused, with ~13 runs on this machine landing at once). Never across the tree or
    pipeline checks: those take minutes and stay parallel. The wait is a guard on progress, not a fixed wait: it waits
    while the holder lives, and the kernel drops the flock when the holder exits or is killed. A lock file that cannot be
    opened (a read-only or missing RM_ROOT) is said on stderr in one line and the push goes on without it: could not
    look is not a refusal."""

    def __init__(self):
        self.path, self.fd = push_lock_path(), None

    def take(self):
        fd, whys = None, []
        for flags in (os.O_CREAT | os.O_RDWR, os.O_RDONLY):      # read-only still locks: flock needs no write access
            try:
                fd = os.open(self.path, flags, 0o644)
                break
            except OSError as e:
                if (e.strerror or str(e)) not in whys:
                    whys.append(e.strerror or str(e))
        if fd is None:
            print("publish: could not open the push lock %s (%s); pushing without it" % (self.path, "; ".join(whys)),
                  file=sys.stderr, flush=True)
            return
        began, said = time.monotonic(), 0
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() - began >= said + PUSH_LOCK_SAY_S:
                    said += PUSH_LOCK_SAY_S
                    print("publish: waiting %d s for the push lock %s, held by %s" % (
                        time.monotonic() - began, self.path, self._holder() or "a publisher"), file=sys.stderr, flush=True)
                time.sleep(0.05)
            except OSError as e:                                   # a filesystem with no flock
                os.close(fd)
                print("publish: could not lock the push lock %s (%s); pushing without it" % (self.path, e.strerror or e),
                      file=sys.stderr, flush=True)
                return
        self.fd = fd
        try:
            os.ftruncate(fd, 0)
            os.write(fd, ("%d %s\n" % (os.getpid(), " ".join(sys.argv)[:200])).encode())
        except OSError:
            pass                                                   # opened read-only: the lock holds all the same

    def _holder(self):
        try:
            with open(self.path) as f:
                return f.read().strip()
        except OSError:
            return ""

    def drop(self):
        if self.fd is not None:
            os.close(self.fd)                                      # closing releases the flock
            self.fd = None

    @contextlib.contextmanager
    def released(self):
        """Let the machine's other publishers push while this one does something slow (a DLL rebuild)."""
        self.drop()
        try:
            yield
        finally:
            self.take()


@contextlib.contextmanager
def push_lock():
    lk = PushLock()
    lk.take()
    try:
        yield lk
    finally:
        lk.drop()


def toplevel(cwd="."):
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd,
                       capture_output=True, text=True)
    if r.returncode:
        raise Refuse("not inside a git repository")
    return r.stdout.strip()


def guard_mnt(top):
    real = os.path.realpath(top)
    if real.startswith("/mnt/"):
        raise Refuse(
            "%s is on the Windows drive. That tree is becoming a read-only mirror of origin/main and "
            "nothing publishes from it any more. Work in your seat clone — /home/mandrake/rm/bench "
            "(i.e. /home/mandrake/rm/<seat>) — or make an ext4 clone: "
            "git clone git@github.com:Lmandrake/RimMandrake.git /home/mandrake/rm/<seat>" % real)


def target_ref(top):
    """(refspec destination, remote-tracking ref to check ancestry against, label)."""
    return "refs/heads/" + BRANCH, "refs/remotes/%s/%s" % (REMOTE, BRANCH), BRANCH


def rel_paths(top, paths, cwd):
    root = os.path.realpath(top)
    res = []
    for p in paths:
        ap = os.path.abspath(os.path.join(cwd, p))
        full = os.path.join(os.path.realpath(os.path.dirname(ap)), os.path.basename(ap))
        rp = os.path.relpath(full, root)
        if rp.startswith(".."):
            raise Refuse("outside this repo: %s" % p)
        res.append(rp)
    return sorted(set(res))


def commit(top, paths, msg):
    """Commit exactly these paths. Returns the new sha, or None when they carry no change."""
    run(top, "add", "--all", "--", *paths)
    if not run(top, "diff", "--cached", "--quiet", "--", *paths, check=False).returncode:
        return None
    started, i = time.monotonic(), 0
    while True:
        r = subprocess.run(["git", "commit", "-q", "-F", "-", "--", *literal(paths)], cwd=top,
                           input=msg, capture_output=True, text=True)
        if not (r.returncode and "index.lock" in r.stderr):
            break
        lock_wait(top, i, started)
        i += 1
    if r.returncode:
        raise Refuse("git commit failed: %s" % (r.stderr or r.stdout).strip())
    return out(top, "rev-parse", "HEAD")


def is_ancestor(top, a, b):
    return run(top, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def ref_exists(top, ref):
    return run(top, "rev-parse", "-q", "--verify", ref, check=False).returncode == 0


def rebase(top):
    """Replay the local commits onto origin/main WITHOUT touching the working tree's dirty files.

    `git pull --rebase` refuses on any unstaged change, and `--autostash` re-applies it afterwards, which in a dirty
    seat clone conflicted and stranded peers' work in stash@{0} (53 files, 2026-10-10). Instead each local commit
    that is not already upstream (git cherry) is re-created on the new tip by `git merge-tree` + `commit-tree`
    (plumbing: no index, no worktree), and the branch moves there with `git reset --keep`, which rewrites only
    files that differ between the old HEAD and the new tip (upstream's changes) and refuses rather than overwrite
    a dirty one. reset_merging first carries dirty files and shards past that refusal. Your commit is intact on HEAD
    after any refusal."""
    run(top, "fetch", "-q", REMOTE, check=False)
    _, track, _ = target_ref(top)
    rebuilt = set()
    if not ref_exists(top, track):
        return rebuilt
    up, head = out(top, "rev-parse", track), out(top, "rev-parse", "HEAD")
    if is_ancestor(top, up, head):
        return rebuilt                                   # already on top of origin
    tip, rebuilt = replay(top, up, head)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
    # seat_sync.reset_keep: a plain --keep would DELETE every file upstream stopped tracking (Transient/,
    # 2026-10-18); it keeps them on disk and otherwise behaves exactly like `git reset --keep`.
    if before_reset:
        before_reset()
    now = out(top, "rev-parse", "HEAD")
    if now != head:
        raise Refuse("HEAD moved from %s to %s while the replay ran (a commit landed in this clone from outside "
                     "this publish). Not resetting: that would discard it. Nothing was lost; re-run ./publish."
                     % (head[:12], now[:12]))
    try:
        note = seat_sync.reset_merging(seat_sync.Git(top), head, tip)
    except seat_sync.DirtyConflict as e:
        msg = ("origin/main changed a file with uncommitted edits, and they really overlap, so this clone's branch was "
               "not moved. Your commit is intact on HEAD and the edit was not touched. Commit or move that edit, then "
               "re-run ./publish or ./sync.\n%s%s" % (blockers(top, head, tip), e))
        if rebuilt:                                      # the DLL rebuild needs the branch moved; do not land half of it
            raise Refuse(msg)
        raise Stranded(msg, tip)
    except seat_sync.Refused as e:
        raise Refuse("the branch was not moved. Your commit is intact on HEAD and nothing was lost; re-run ./publish.\n"
                     "%s%s" % (blockers(top, head, tip), e))
    if note:
        print("moved the branch: %s" % note)
    return rebuilt


def replay(top, up, head, say=print):
    """-> (tip, rebuilt): HEAD's local commits re-created on `up` by plumbing only (merge-tree + commit-tree; no index,
    no worktree, no ref moved), and the DLLs whose pairs took origin's side. rebase() moves the branch to `tip`;
    landing_rev() judges `tip` at the door. Raises Refuse on a merge or a real conflict."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
    rebuilt = set()
    # Nothing local but behind: still move, carrying dirty files, or an unattended clone (the dispatch clone) whose
    # publishes find nothing to commit stays behind for good and lints its stale HEAD
    # (RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD).
    behind_only = is_ancestor(top, head, up)
    # git cherry never lists a merge, so a resolution edited inside one would vanish at the reset: ask rev-list
    merges = [] if behind_only else out(top, "rev-list", "--merges", "%s..%s" % (up, head)).split()
    if merges:
        raise Refuse("local commit %s is a merge; publish cannot replay it" % merges[0][:12])
    todo = [] if behind_only else [ln[2:].strip() for ln in out(top, "cherry", up, head).splitlines()
                                   if ln.startswith("+")]
    # git cherry calls a landed commit unlanded when it touches a union shard (the patch-id context differs), and its
    # replay re-adds files origin has since moved or deleted (RIMMANDRAKE_SKIP_LANDED_TWINS_PUBLISH_REPLAY_RESURRECTS_FILES)
    if todo:
        sg, base = seat_sync.Git(top), out(top, "merge-base", up, head)
        kept = []
        for c in todo:
            try:
                twin = seat_sync.landed_twin(sg, up, c, base)
            except seat_sync.Refused:                    # a git error proves nothing: replay it as before
                twin = None
            if twin is None:
                kept.append(c)
            else:
                say("%s is already on origin%s; not replaying it" % (c[:12], " as " + twin[:12] if twin else ""))
        todo = kept
    tip = up
    for c in todo:
        r = run(top, "merge-tree", "--write-tree", "--name-only", "--merge-base=%s^" % c, tip, c, check=False)
        tree = r.stdout.split("\n", 1)[0].strip()
        if r.returncode:
            paths = r.stdout.split("\n\n", 1)[0].splitlines()[1:]
            if not paths or not all(is_dll_pair_path(p) for p in paths):
                raise Refuse("replaying %s onto origin/main stopped on a conflict in: %s. Your commit is intact on "
                             "HEAD; this clone has one owner, so merge it by hand, then re-run ./publish"
                             % (c[:12], ", ".join(paths) or "(see git merge-tree)"))
            # Only committed DLL/.srchash pairs conflict: take origin's side; land() rebuilds them from the
            # committed source once the branch has moved, so neither side's binary is trusted.
            tree = take_side(top, tree, tip, c, paths)
            rebuilt.update(dll_of(p) for p in paths)
            say("replay of %s: DLL conflict in %s; took origin's side, will rebuild from committed source"
                  % (c[:12], ", ".join(sorted(set(paths)))))
        tree = dedupe_shards(top, tree, tip, c)
        if tree == out(top, "rev-parse", tip + "^{tree}"):
            continue                                     # nothing left of it: a DLL pair, or already on origin
        meta = out(top, "show", "-s", "--format=%an%x00%ae%x00%aI", c).split("\0")
        env = git_env(GIT_AUTHOR_NAME=meta[0], GIT_AUTHOR_EMAIL=meta[1], GIT_AUTHOR_DATE=meta[2])
        body = out(top, "show", "-s", "--format=%B", c) + "\n"
        tip = subprocess.run(["git", "commit-tree", tree, "-p", tip, "-F", "-"], cwd=top, input=body, env=env,
                             capture_output=True, text=True, check=True, timeout=GIT_TIMEOUT_S).stdout.strip()
    return tip, rebuilt


# ---- committed mod DLLs at landing -------------------------------------------------------------------------
# A DLL cannot merge, and a rebuilt one depends on every commit under it, so publish (the one place a commit is
# landed) owns it: a replay conflict on DLL/.srchash pairs alone takes origin's side and rebuilds; a
# DLL_SOURCE_STAMP_GUARD_1 refusal rebuilds and retries once. The build runs in a throwaway src-only clone at the
# COMMITTED HEAD, never the seat's worktree, so peers' uncommitted C# cannot leak into it (2026-10-22).
SCRATCH_ROOT = os.environ.get("PUBLISH_SCRATCH_ROOT")      # default: <RM_ROOT>/scratch/<SEAT>
GUARD_TAG = "DLL_SOURCE_STAMP_GUARD_1"


def is_dll_pair_path(p):
    return p.endswith(".dll.srchash") or (p.endswith(".dll") and "/Assemblies/" in p)


def dll_of(p):
    return p[:-len(".srchash")] if p.endswith(".srchash") else p


def take_side(top, tree, tip, c, paths):
    """`tree` with every path in `paths` set to origin's (`tip`) blob, or the commit's when origin has none."""
    import tempfile
    fd, idx = tempfile.mkstemp(prefix="publish-idx-", dir=out(top, "rev-parse", "--absolute-git-dir"))
    os.close(fd)
    env = git_env(GIT_INDEX_FILE=idx)
    try:
        def g(*a):
            return subprocess.run(["git", *a], cwd=top, env=env, capture_output=True, text=True, errors="surrogateescape",
                                  check=True).stdout
        g("read-tree", tree)
        for p in paths:
            ent = out(top, "ls-tree", tip, "--", p) or out(top, "ls-tree", c, "--", p)
            if ent:
                mode, _, blob = ent.split("\t", 1)[0].split()
                g("update-index", "--add", "--cacheinfo", "%s,%s,%s" % (mode, blob, p))
            else:
                g("update-index", "--force-remove", "--", p)
        return g("write-tree").strip()
    finally:
        os.unlink(idx)


def _blob(top, rev, path):
    """`path` at `rev` as bytes, or None where it does not exist."""
    r = subprocess.run(["git", "cat-file", "blob", "%s:%s" % (rev, path)], cwd=top, capture_output=True,
                       env=git_env(), timeout=GIT_TIMEOUT_S)
    return r.stdout if r.returncode == 0 else None


def dedupe_shards(top, tree, tip, c):
    """`tree` with each append-only (merge=union) shard `c` touched rebuilt as origin's bytes plus only the lines `c`
    appended that origin does not already hold (LEDGER_UNION_DEDUPE_PUBLISH_DOUBLED_LINES). git's union keeps BOTH
    sides of a hunk, so a line origin already landed under other lines (another clone, the belt) was written again
    on every replay: 268 byte-identical twins in BENCH.jsonl. seat_sync.union_delta is the rule the clone's own move
    uses; where it says these are not plain appends (None), merge-tree's result stands untouched."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
    touched = out(top, "diff", "--name-only", "%s^" % c, c).splitlines()
    shards = sorted(seat_sync.union_paths(seat_sync.Git(top), touched)) if touched else []
    fixed = {}
    for p in shards:
        mine, base, theirs = _blob(top, c, p), _blob(top, c + "^", p), _blob(top, tip, p)
        if mine is None or (base is None and theirs is None):
            continue                                     # deleted, or new/renamed by c: not an append, merge-tree's
        theirs, base = theirs or b"", base or b""
        delta = seat_sync.union_delta(theirs, base, mine)
        if delta is None:
            continue
        want = theirs + delta
        if want != _blob(top, tree, p):
            fixed[p] = want
    if not fixed:
        return tree
    import tempfile
    fd, idx = tempfile.mkstemp(prefix="publish-idx-", dir=out(top, "rev-parse", "--absolute-git-dir"))
    os.close(fd)
    env = git_env(GIT_INDEX_FILE=idx)
    try:
        def g(*a, inp=None):
            return subprocess.run(["git", *a], cwd=top, env=env, input=inp, capture_output=True, check=True,
                                  timeout=GIT_TIMEOUT_S).stdout
        g("read-tree", tree)
        for p, data in fixed.items():
            blob = g("hash-object", "-w", "--stdin", inp=data).decode().strip()
            mode = (out(top, "ls-tree", tree, "--", p).split() or ["100644"])[0]
            g("update-index", "--add", "--cacheinfo", "%s,%s,%s" % (mode, blob, p))
        return g("write-tree").decode().strip()
    finally:
        os.unlink(idx)


def blockers(top, head, tip):
    """Which uncommitted paths stopped `reset --keep`, with their mtimes (git cannot say whose they are)."""
    moved = set(out(top, "diff", "--name-only", head, tip).splitlines())
    dirty = [ln[3:] for ln in run(top, "status", "--porcelain", "--untracked-files=no").stdout.splitlines()]
    hit = sorted(p for p in dirty if p in moved)
    if not hit:
        return ""
    stamp = lambda p: time.strftime("%H:%M", time.localtime(os.path.getmtime(os.path.join(top, p)))) \
        if os.path.exists(os.path.join(top, p)) else "deleted"
    return ("Blocking uncommitted paths (owner unknown to git; edited at): %s\n"
            % ", ".join("%s (%s)" % (p, stamp(p)) for p in hit))


def winbuild(scratch, csproj):
    """Build `csproj` (absolute, inside `scratch`) with scratch's own winbuild.py. Selftest hook."""
    r = subprocess.run([sys.executable or "python3", os.path.join(scratch, "src/RimMandrake/Utils/winbuild.py"),
                        csproj, "--", "--no-incremental"],          # obj/ cache built a stale DLL once (lesson 22:36Z)
                       # budget: danger=a hung winbuild holds a landing; never reached in the 14 days to 2026-11-24; no record
                       # budget: of its run
                       cwd=scratch, capture_output=True, text=True, timeout=1200)
    return r.returncode, (r.stdout + r.stderr).strip()


def rebuild_dlls(top, dlls):
    """Rebuild each DLL from the source committed at HEAD and commit the .dll+.srchash pairs. Returns the sha."""
    import shutil
    import tempfile
    dlls = sorted(dlls)
    pairs = [q for d in dlls for q in (d, d + ".srchash")]
    dirty = [ln[3:] for ln in run(top, "status", "--porcelain", "--", *pairs).stdout.splitlines()]
    if dirty:
        raise Refuse("a DLL needs rebuilding from committed source, but this clone has uncommitted edits to: %s "
                     "(not mine to overwrite). Your commit is intact on HEAD." % ", ".join(dirty))
    head = out(top, "rev-parse", "HEAD")
    root = SCRATCH_ROOT or os.path.join(RM_ROOT, "scratch", os.path.basename(top).upper())
    os.makedirs(root, exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="publish-dll-", dir=root)
    try:
        for a in (["clone", "-q", "--shared", "--no-checkout", top, scratch],
                  ["-C", scratch, "sparse-checkout", "set", "src"],
                  ["-C", scratch, "checkout", "-q", "--detach", head]):
            r = subprocess.run(["git", *a], capture_output=True, text=True)
            if r.returncode:
                raise Refuse("scratch clone for the DLL rebuild failed: git %s: %s" % (a[0], r.stderr.strip()))
        projects = {}
        for d in dlls:
            first = out(top, "show", "%s:%s.srchash" % (head, d)).splitlines()[:1]
            if not first or not first[0].startswith("# project:"):
                raise Refuse("%s.srchash at HEAD names no '# project:'; cannot tell what to rebuild" % d)
            projects.setdefault("src/" + first[0][len("# project:"):].strip(), []).append(d)
        for proj, ds in sorted(projects.items()):
            print("rebuilding %s from committed source %s (scratch clone)" % (proj, head[:12]), flush=True)
            rc, log = winbuild(scratch, os.path.join(scratch, proj))
            if rc:
                raise Refuse("rebuild of %s failed (rc %d); your commit is intact on HEAD:\n%s"
                             % (proj, rc, "\n".join(log.splitlines()[-15:])))
            for d in ds:
                for q in (d, d + ".srchash"):
                    if not os.path.exists(os.path.join(scratch, q)):
                        raise Refuse("rebuild of %s wrote no %s" % (proj, q))
        install_pairs(top, head, scratch, pairs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    sha = commit(top, pairs, "Rebuild %s from committed source at landing\n\nBuilt by ./publish in a src-only "
                 "scratch clone of %s.\n" % (", ".join(os.path.basename(d) for d in dlls), head[:12]))
    if sha:
        print("committed rebuilt %s as %s" % (", ".join(dlls), sha[:12]))
    return sha


def install_pairs(top, head, scratch, pairs):
    """Put the rebuilt files into the worktree only where each still holds HEAD's bytes. The build takes minutes and the
    dirty check ran before it, so a peer's save in between was overwritten by a blind replace (Codex, 2026-11-01). Each
    file goes in by atomic swap (seat_sync._exchange) and the displaced bytes are checked: anything but HEAD's goes
    straight back, every file already swapped is swapped back too, and the landing refuses naming the path. The undo
    displaces atomically too and checks what it displaced (PUBLISH_ROLLBACK_FIX_RACE_STILL_AJAR): a compare-then-swap
    or compare-then-unlink lost a save landing in between. No side file is deleted unless it holds bytes this call
    owns (HEAD's or the rebuild's); any other is kept and named on stderr."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
    def at_head(q):
        r = subprocess.run(["git", "cat-file", "blob", "%s:%s" % (head, q)], cwd=top, capture_output=True,
                           timeout=GIT_TIMEOUT_S)
        return r.stdout if r.returncode == 0 else None
    def read(path):
        return open(path, "rb").read() if os.path.isfile(path) and not os.path.islink(path) else None
    def settle(side, *ours):                             # delete a side file only when it holds bytes we own
        if not os.path.lexists(side):
            return
        b = read(side)
        if b is not None and any(b == o for o in ours if o is not None):
            os.unlink(side)
        else:
            print("KEPT %s: it holds bytes publish did not write (a save landing during the DLL install); "
                  "nothing was deleted" % side, file=sys.stderr, flush=True)
    def undo(dst, tmp, want, new):
        """Take one installed file back out. Displace first (atomic), then prove the displaced bytes were ours."""
        if tmp is None:                                  # absent at HEAD: move it aside, never unlink blind
            hold = "%s.publish-undo-%d" % (dst, os.getpid())
            try:
                os.rename(dst, hold)
            except FileNotFoundError:
                return
            if read(hold) == new:
                os.unlink(hold)
                return
            try:                                         # a peer saved over ours: put it back, never clobbering
                os.link(hold, dst)
            except FileExistsError:
                pass
            else:
                os.unlink(hold)
                return
            settle(hold)
            return
        seat_sync._exchange(tmp, dst)                    # tmp held HEAD's bytes; now it holds what dst held
        if read(tmp) == new:
            settle(tmp, new)
            return
        seat_sync._exchange(tmp, dst)                    # a peer's save was displaced: it goes back to dst
        settle(tmp, want, new)
    done = []                                            # (worktree path, tmp holding HEAD's bytes, HEAD's, new)
    try:
        for q in pairs:
            dst, tmp, want = os.path.join(top, q), os.path.join(top, q) + ".publish-tmp", at_head(q)
            new = open(os.path.join(scratch, q), "rb").read()
            if read(dst) != want:
                raise Refuse("%s changed in the worktree while the DLL rebuilt (a save that is not mine to overwrite); "
                             "left as it is, nothing installed. Your commit is intact on HEAD." % q)
            with open(tmp, "wb") as f:
                f.write(new)
            if want is None:                             # absent at HEAD and still absent: link never clobbers
                try:
                    os.link(tmp, dst)
                except FileExistsError:
                    raise Refuse("%s appeared in the worktree while the DLL rebuilt; left as it is." % q)
                finally:
                    os.unlink(tmp)
                done.append((dst, None, None, new))
                continue
            seat_sync._exchange(tmp, dst)
            if read(tmp) != want:                        # a save landed between the compare and the swap
                seat_sync._exchange(tmp, dst)
                settle(tmp, new)
                raise Refuse("%s changed in the worktree while the DLL rebuilt (a save that is not mine to "
                             "overwrite); left as it is, nothing installed. Your commit is intact on HEAD." % q)
            done.append((dst, tmp, want, new))
    except BaseException:
        for dst, tmp, want, new in reversed(done):       # put HEAD's bytes back, unless someone wrote since
            undo(dst, tmp, want, new)
        raise
    else:
        for _, tmp, want, _ in done:
            if tmp:
                settle(tmp, want)


def guard_dlls(err):
    """DLL paths a DLL_SOURCE_STAMP_GUARD_1 refusal names, or an empty set when it is not that refusal."""
    if GUARD_TAG not in err:
        return set()
    return {m.group(2) for m in re.finditer(r"^(?:remote: )?\s*(MISMATCH|STAMP_MISSING) (\S+\.dll)\s*$", err, re.M)}


def warn_stranded(stranded):
    if stranded:
        print("LANDED, CLONE NOT MOVED: %s" % stranded)


def land(top):
    """Replay onto origin and push, retried while origin moves under it. Each try's fetch, replay and push hold the
    machine-wide push lock (push_lock); the classification and the pause between tries do not. A retry repeats only
    what the moved origin can change (the replay, a DLL rebuild when DLL pairs conflict, the pre-push hook): the tree
    and pipeline checks ran once before, in _publish."""
    dest, track, label = target_ref(top)
    guard_retried, fails, races = False, 0, 0
    for attempt in range(MAX_TRIES):
        stranded = landed = None
        with push_lock() as lk:
            try:
                rebuilt = rebase(top)
                if rebuilt:
                    with lk.released():                  # minutes of msbuild: the machine's other publishers push
                        rebuild_dlls(top, rebuilt)
                head = out(top, "rev-parse", "HEAD")
            except Stranded as s:
                stranded, head = s, s.tip                # land the replay; only this clone's branch waits
            up = out(top, "rev-parse", track) if ref_exists(top, track) else None
            if label == BRANCH and is_ancestor(top, head, track):
                landed = "nothing local left to push"
            else:
                if before_push:
                    before_push(attempt)
                r = run(top, "push", "-q", REMOTE, "%s:%s" % (head, dest), check=False)
                # On success the fetch levels the tracking ref; on failure it is the ambiguity check before any retry:
                # the remote may have taken it before we gave up.
                run(top, "fetch", "-q", REMOTE, check=False)
                if not r.returncode:
                    landed = "pushed"
                elif ref_exists(top, track) and is_ancestor(top, head, track):
                    print("push reported failure but %s already contains %s — it landed" % (label, head[:12]))
                    landed = "taken"
                err = (r.stderr or r.stdout).strip()
                # origin moved since this try's fetch: the failure is the race, whatever words it took (two pushes at
                # once read "[remote rejected] ... cannot lock ref", "failed to push some refs"), as land_ledger reads it
                moved = ref_exists(top, track) and out(top, "rev-parse", track) != up
        if landed:
            warn_stranded(stranded)
            return head
        bad = guard_dlls(err)
        if bad:
            if stranded:
                raise Refuse("the DLL/source-stamp guard refused, and this clone's branch cannot move to rebuild:\n"
                             "%s\n%s" % (stranded, err))
            if guard_retried:
                raise Refuse("the DLL/source-stamp guard refused again after a rebuild from committed source:\n%s"
                             % err)
            guard_retried = True
            print("pre-push %s refused %s; rebuilding from committed source and retrying once"
                  % (GUARD_TAG, ", ".join(sorted(bad))))
            rebuild_dlls(top, bad)
            continue
        race = moved or re.search(r"non-fast-forward|fetch first|\[rejected\]|failed to update ref", err)
        if not race and re.search(r"^pre-push REFUSED", err, re.M):
            # RIMMANDRAKE_STOP_RETRYING_A_PRE_PUSH_REFUSAL: a hook's verdict, not a race; retrying hid its reason
            raise Refuse("push refused by the pre-push hook (nothing pushed):\n%s" % err)
        if not race:
            fails += 1
            if fails < PUSH_FAIL_TRIES:
                print("push failed (%s); retrying" % err.splitlines()[-1] if err else "push failed")
                time.sleep(min(2 ** (fails - 1), 20))
                continue
            raise Refuse("push failed: %s" % err)
        if label != BRANCH:
            raise Refuse("%s already holds a submission this one does not contain — the seat has not "
                         "landed it yet (it deletes the submit ref when it does). Not forcing.\n%s"
                         % (label, err))
        races += 1
        print("origin moved (attempt %d); rebasing and retrying" % (attempt + 1))
        time.sleep(min(0.5 * (attempt + 1), RACE_PAUSE_MAX_S))
    raise Refuse("origin kept moving: could not land after %d tries, %d of them lost push races (the limit MAX_TRIES = "
                 "%d is 10x the 8 lost races in a row measured on 2026-11-24). Nothing is wrong with the commit: it "
                 "stays on HEAD; run ./publish again" % (MAX_TRIES, races, MAX_TRIES))


def _owed_lines(ours, base, theirs):
    """-> the bytes this clone appended to a shard that origin does not hold, each line once, in our order; None when they
    cannot be told (a torn last line). A base line that origin removed is not an append, so it is not put back."""
    if (ours and not ours.endswith(b"\n")) or (theirs and not theirs.endswith(b"\n")):
        return None
    held = collections.Counter(base.splitlines(True))
    up = set(theirs.splitlines(True))
    new = []
    for ln in ours.splitlines(True):
        if held[ln]:
            held[ln] -= 1
        elif ln not in up:
            up.add(ln)
            new.append(ln)
    return b"".join(new)


def land_ledger(top, named, msg):
    """Land ONLY these ledger shards' new lines on origin/main by plumbing: no clone lock, no local commit, no peer's
    commit, no whole-tree check (the list skips ledger shards anyway). Then level the clone when no publish holds it.
    -> the landed sha, or None when this cannot be done here (the caller takes the ordinary route).
    Why: 1,146 ledger landings of 2026-11-22/23 waited 17 s at p50, 96 s at p90 and 677 s at p99 behind a peer's publish
    and its tests (boundary design/specs/2026-11-22-ledger-write-lands-its-shard/boundary.md)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
    g = seat_sync.Git(top)
    dest, track, _ = target_ref(top)

    def blob(rev, p):
        r = subprocess.run(["git", "cat-file", "blob", "%s:%s" % (rev, p)], cwd=top, capture_output=True,
                           timeout=GIT_TIMEOUT_S)
        return r.stdout if not r.returncode else b""

    def one(attempt):
        """One try, under the push lock: fetch, replay the lines, push. -> ("landed"|"held", sha), ("race", None) or
        ("route", None) when the ordinary route must take it."""
        if run(top, "fetch", "-q", REMOTE, check=False).returncode or not ref_exists(top, track):
            return "route", None
        up = out(top, "rev-parse", track)
        base = run(top, "merge-base", "HEAD", up, check=False).stdout.strip()
        if not base:
            return "route", None
        idx = os.path.join(out(top, "rev-parse", "--absolute-git-dir"), "ledger-landing.%d.idx" % os.getpid())
        env = git_env(GIT_INDEX_FILE=idx)

        def plumb(*a, inp=None):
            r = subprocess.run(["git", *a], cwd=top, env=env, input=inp, capture_output=True, timeout=GIT_TIMEOUT_S)
            if r.returncode:
                raise Refuse("git %s failed: %s" % (a[0], r.stderr.decode("utf-8", "replace").strip()))
            return r.stdout.decode().strip()
        try:
            plumb("read-tree", up)
            changed, taken_out = False, False
            for p in named:
                ours, theirs, was = seat_sync._read_shard(g, p), blob(up, p), blob(base, p)
                new = None if ours is None else _owed_lines(ours, was, theirs)
                if new is None:
                    return "route", None
                taken_out |= bool(collections.Counter(was.splitlines(True)) - collections.Counter(ours.splitlines(True)))
                if new:
                    changed = True
                    sha = plumb("hash-object", "-w", "--stdin", inp=theirs + new)
                    plumb("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, p))
            if not changed:
                if taken_out:                            # a line removed here is no append: the ordinary route commits it
                    return "route", None
                # another writer's landing in this clone carried our lines: they are on origin, in the commit that says so
                held = out(top, "log", "-1", "--format=%H", up, "--", *named)
                if held:
                    print("already on %s/%s: another landing carried these lines" % (REMOTE, BRANCH))
                    return "held", held
                return "route", None
            tip = plumb("commit-tree", plumb("write-tree"), "-p", up, "-F", "-", inp=msg.encode())
        finally:
            for f in (idx, idx + ".lock"):
                if os.path.exists(f):
                    os.unlink(f)
        if before_push:
            before_push(attempt)
        r = run(top, "push", "-q", REMOTE, "%s:%s" % (tip, dest), check=False)
        run(top, "fetch", "-q", REMOTE, check=False)
        if not r.returncode or (ref_exists(top, track) and is_ancestor(top, tip, track)):
            return "landed", tip
        err = (r.stderr or r.stdout).strip()
        # origin moved since this try's fetch: the failure is the race, whatever words it took (git's "[remote rejected]
        # cannot lock ref", or the lint's NOT_APPEND against the newer tip). A verdict on the lines repeats on the next try.
        moved = ref_exists(top, track) and out(top, "rev-parse", track) != up
        if not moved and re.search(r"^pre-push REFUSED", err, re.M):
            raise Refuse("push refused by the pre-push hook (nothing pushed):\n%s" % err)
        if not moved and not re.search(r"non-fast-forward|fetch first|\[rejected\]|failed to update ref", err):
            return "route", None                         # the ordinary route retries it and names the cause
        return "race", None
    for attempt in range(MAX_TRIES):
        with push_lock():
            how, sha = one(attempt)
        if how in ("landed", "held"):
            _level_if_free(top)                          # outside the push lock: a sync is this clone's business
            return sha
        if how == "route":
            return None
        time.sleep(min(0.5 * (attempt + 1), RACE_PAUSE_MAX_S))
    return None


def _level_if_free(top):
    """After land_ledger: move this clone onto origin/main as ./sync does, unless a publish holds the clone (it moves the
    branch itself). What cannot move stays as it is; the next publish or ./sync carries it. Never a refusal."""
    import seat_sync
    fd = os.open(lock_path(top), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            seat_sync.main(["--repo", top, "--no-fetch"])
    except Exception as e:  # noqa: BLE001  the landing is done
        print("LANDED, CLONE NOT MOVED: %s: %s" % (type(e).__name__, e))
    finally:
        os.close(fd)


def publish(top, paths, msg, cwd=None, ledger=False):
    """Paths are relative to `cwd` (the caller's directory; defaults to the repo top). `ledger`: when every path is a
    ledger shard, land only their new lines, past the clone lock (land_ledger); anything else goes the ordinary way."""
    guard_mnt(top)
    if ledger and paths and msg and msg.strip() and not door_skips():
        named = rel_paths(top, paths, cwd or top)
        if all(p.startswith(LEDGER_SHARDS) and p.endswith(".jsonl") for p in named) and not carried_prose_moves(top, named):
            sha = land_ledger(top, named, msg if msg.endswith("\n") else msg + "\n")
            if sha:
                warn_owner_shard(top, named)
                print("PUBLISHED %s" % sha)
                return sha
    with clone_lock(top):
        return _publish(top, paths, msg, cwd)


def warn_owner_shard(top, named):
    """`--owner-said`, `--by-card`, `ack` and an OWNER-seat `file` write OWNER.jsonl, not the seat's shard, so a landing that names
    only the seat's shard ends green with his ruling still unpublished. Loud, not refused: a helper may rightly not own those lines."""
    if OWNER_SHARD not in named and run(top, "status", "--porcelain", "--", OWNER_SHARD).stdout.strip():
        print("WARNING: %s has unpublished events and you did not name it. His rulings stay on this clone until it lands: name it." % OWNER_SHARD)


TREE_CHECKS = os.path.join("src", "RimMandrake", "Utils", "publish_tree_checks.json")


def tree_checks(top, changed, gate=None):
    """Owner by card 2026-11-12 ~8:25 PM PST: publish runs the fast whole-tree checks and refuses on red, naming it
    (validation_map_and_rules.md rule 10). The list is TREE_CHECKS; a repo without it (a test fixture) runs nothing.
    `changed`: the paths the local commits touch; only skip_when_only paths -> nothing runs. A check that times out
    warns: it measured nothing, so it refuses nothing. A clone runs them on a full checkout (full_head_tree) of the
    tree that lands (landing_rev: HEAD, or HEAD replayed onto a fresh origin/main when HEAD is behind it). -> None, or raises Refuse naming each red check and its fix."""
    cfg_path = os.path.join(top, TREE_CHECKS)
    if not os.path.isfile(cfg_path):
        return None
    skip = os.environ.get("RM_PUBLISH_SKIP_TREE_CHECKS", "").strip()
    if skip:
        print("tree checks SKIPPED by RM_PUBLISH_SKIP_TREE_CHECKS: %s" % skip)
        return None
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    if changed and all(any(fnmatch.fnmatch(p, g) for g in cfg.get("skip_when_only", ())) for p in changed):
        return None
    if gate is not None:
        gate.take("tree checks")                         # the full checkout and the checks wait for a machine slot
    if is_clone_top(top):
        rev, what = landing_rev(top)
        with full_head_tree(top, rev=rev, what=what, lands=True) as full:
            cfg = _committed(full, TREE_CHECKS)         # the landing tree's own list: its tests are the ones checked out
            return _run_tree_checks(full, cfg) if cfg else None
    return _run_tree_checks(top, cfg)


def landing_rev(top):
    """-> (rev, what): the commit the whole-tree checks judge. When HEAD is behind a fresh origin/main, HEAD's local
    commits replayed onto it (replay(), the same plumbing land() uses; nothing moves), so a red origin has since
    repaired does not refuse sound work, and a red origin brings in is seen before it lands
    (RIMMANDRAKE_CHECK_PUBLISH_TREE_ON_REBASED_HEAD_NOT_STALE: a clone 19 behind was refused twice for ledger lines
    origin had restored; the whole-tree checks take no pre-existing excuse). Otherwise HEAD, as before, also when the
    replay cannot be made (land() then refuses on that conflict itself)."""
    run(top, "fetch", "-q", REMOTE, check=False)         # unreachable: the last tracking ref is the best known origin
    _, track, _label = target_ref(top)
    if not ref_exists(top, track):
        return "HEAD", "HEAD"
    up, head = out(top, "rev-parse", track), out(top, "rev-parse", "HEAD")
    if is_ancestor(top, up, head):
        return "HEAD", "HEAD"
    try:
        tip, _rebuilt = replay(top, up, head, say=lambda *_a: None)
    except (Refuse, subprocess.SubprocessError) as e:
        print("tree checks: HEAD cannot be replayed onto origin/main %s (%s); judging HEAD" % (up[:12], e))
        return "HEAD", "HEAD"
    return tip, "HEAD replayed onto origin/main %s" % up[:12]


PIPELINE_TESTS = os.path.join("src", "RimMandrake", "Utils", "pipeline_tests.json")
TREECHECK_GATE = ".treecheck-slots"      # under RM_ROOT: one line per machine (treecheck_slots.py)


def door_checks(top, changed):
    """The whole-tree checks, then the pipeline checks, under one per-machine slot (treecheck_slots.SLOTS run at once,
    the rest wait first come first served; RIMMANDRAKE_THROTTLE_TREECHECKS_WHEN_DISK_SATURATES_HANG_GUARDS_FIRE: six at
    once saturated SteveDesktop's disk, 2026-11-24). A change that runs no door check takes no slot. Page:
    design/specs/2026-11-24-treecheck-slots/boundary.md. Raises Refuse as tree_checks and pipeline_checks do."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import treecheck_slots
    with treecheck_slots.Gate(os.path.join(RM_ROOT, TREECHECK_GATE)) as gate:
        tree_checks(top, changed, gate)
        pipeline_checks(top, changed, gate)


def polish_door_check(top):
    """A helper run's new polish.md line about a file it changed, with no `risk:` part, is returned to the run with the
    rule (polish_door.py; CLAUDE.md §Touching code has a cost). Raises Refuse; the caller takes the commit off HEAD."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import polish_door
    _, track, _label = target_ref(top)
    msg = polish_door.check(top, track)
    if msg:
        raise Refuse(msg)


def door_inputs(top, test):
    """-> repo-relative paths a pipeline test's verdict is taken to depend on: the test, the repo .py files it imports or
    names (transitively; run_selftests' reader, without its whole-directory sweep, which would tie every rimflow test to
    every rimflow file), and each one's same-stem .json beside it (red_dispatch.json, maturation_dispatch.json)."""
    from pathlib import Path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import run_selftests as RS
    root = Path(top).resolve()
    t = (root / test).resolve()
    seen, todo = set(), [t]
    while todo:
        f = todo.pop()
        if f in seen or not f.is_file():
            continue
        seen.add(f)
        todo += [c for c in RS._direct_deps(f, root) if c not in seen]
    out = set()
    for f in seen:
        out.add(f.relative_to(root).as_posix())
        j = f.with_suffix(".json")
        if j.is_file():
            out.add(j.relative_to(root).as_posix())
    return out


def pipeline_selection(top, changed, cfg):
    """-> the pipeline tests (not live_excluded) whose door_inputs, or `inputs` globs (a page a test reads that no import
    names), the change touches; [] when it touches no pipeline file; every one when the change set is unknown (None: no
    origin/main to diff against)."""
    live = set(cfg.get("live_excluded", {}))
    if changed is None:
        return [c for c in cfg.get("tests", ()) if c["test"] not in live]
    if not any(fnmatch.fnmatch(p, g) for p in changed for g in cfg.get("pipeline_files", ())):
        return []
    ch = set(changed)
    return [c for c in cfg.get("tests", ()) if c["test"] not in live and (door_inputs(top, c["test"]) & ch or any(
        fnmatch.fnmatch(p, g) for p in ch for g in c.get("inputs", ())))]


def pipeline_checks(top, changed, gate=None):
    """The Maturation Pipeline's tests at the door (pipeline_tests.json; owner by card 2026-11-15, nightly is the wrong
    phase for fluid code): a change touching a pipeline file runs the pipeline tests whose inputs it touches and
    refuses on a red. -> seconds added (0.0 when nothing ran), or raises Refuse."""
    cfg_path = os.path.join(top, PIPELINE_TESTS)
    if not os.path.isfile(cfg_path) or changed == []:
        return 0.0
    skip = os.environ.get("RM_PUBLISH_SKIP_PIPELINE_CHECKS", "").strip()
    if skip:
        print("pipeline checks SKIPPED by RM_PUBLISH_SKIP_PIPELINE_CHECKS: %s" % skip)
        return 0.0
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    if changed is None:     # no origin/main to diff against: what the change touches is unknown, so nothing is skipped
        print("pipeline checks: the change set is unknown (no origin/main here), so every pipeline test runs")
    elif not any(fnmatch.fnmatch(p, g) for p in changed for g in cfg.get("pipeline_files", ())):
        return 0.0
    if gate is not None:
        gate.take("pipeline checks")                     # a no-op when this publish's tree checks hold a slot already
    base = door_base(top)
    if is_clone_top(top):
        with full_head_tree(top) as full:
            cfg = _committed(full, PIPELINE_TESTS)
            return _run_pipeline_checks(full, changed, cfg, base, committed=True) if cfg else 0.0
    return _run_pipeline_checks(top, changed, cfg, base)


def _run_pipeline_checks(top, changed, cfg, base=(None, "not asked"), committed=False):
    sel = pipeline_selection(top, changed, cfg)
    if not sel:
        print("pipeline checks: a pipeline file changed, no pipeline test reads it")
        return 0.0
    wall = _run_tree_checks(top, {"checks": sel, "timeout_s": cfg.get("timeout_s", CHECK_CAP_S)}, what="pipeline check",
                            base=base, committed=committed)
    return wall


def door_base(top):
    """-> (sha, None): the commit this change sits on (HEAD's merge base with origin/main), which a red pipeline test is
    re-run on; or (None, why) when there is none to read."""
    _, track, _label = target_ref(top)
    if not ref_exists(top, track):
        return None, "no %s in this clone" % track
    r = run(top, "merge-base", "HEAD", track, check=False)
    sha = (r.stdout or "").strip()
    if r.returncode or not sha:
        return None, "git merge-base HEAD %s: %s" % (track, (r.stderr or "").strip() or "no common commit")
    return sha, None


FAIL_RX = re.compile(r"\s*(FAIL|RED|BROKEN|STALE)")
TMP_RX = re.compile(r"(?:/private)?(?:/tmp|/var/folders|%s)/\S*" % re.escape(tempfile.gettempdir()))


# A measured reading moves between two runs of the same code: a quoted number in a list (['581', '742']) or a number
# with a unit of time, size or share (629 ms, 1.5 s, 38 MB, 12%), or the machine's load average ("load 14.5"). A bare
# count ("unit 2", "3 of 9") is kept.
READING_RX = re.compile(r"'\d+(?:\.\d+)?'|\b\d+(?:\.\d+)?\s?(?:ms|s|MB|GB|KB|%)(?![A-Za-z])|\bload \d+(?:\.\d+)?")


# 2026-11-24 on SteveDesktop: a Windows python's traceback spells the check tree \\wsl.localhost\Ubuntu\...\rm-treecheck-<random>,
# which the tree's own path does not match, and a FAIL line can name a commit sha; both move between the two runs
# a check tree, or a run of check trees nested in each other (HEAD's re-run sits inside the door's tree), in any spelling
TREE_NAME_RX = re.compile(r"rm-treecheck-[A-Za-z0-9_]+(?:[\\/]+\.git[\\/]+rm-treecheck-[A-Za-z0-9_]+)*")
SHA_RX = re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")


def _norm(ln, tree):
    """What moves between two runs of the same code, blanked: the tree's own path, temp paths, measured readings
    (READING_RX) and numbers of four or more digits (pids, timestamps, unit names). A short number (a count, a case number) is kept, so "unit 2" is not "unit 1"."""
    ln = ln.strip().replace(os.path.realpath(tree), "<TOP>").replace(tree, "<TOP>")
    ln = READING_RX.sub("R", ln)
    ln = TREE_NAME_RX.sub(CHECKTREE_PREFIX + "X", ln)     # the check tree's random name, in any spelling of its path
    ln = SHA_RX.sub("SHA", ln)
    return re.sub(r"\d{4,}", "N", TMP_RX.sub("<TMP>", ln))


def red_signature(o, tree, rc):
    """-> (Counter of a red run's normalised FAIL lines and crash, {key: one raw line}), or (None, why) when the run gives
    nothing to compare by (no FAIL line and no traceback): such a red is never proved pre-existing. A traceback counts
    by its last 20 lines, so a crash after the same FAIL lines, or at another place, is a difference."""
    import collections
    lines = o.splitlines()
    fails = [ln for ln in lines if FAIL_RX.match(ln)]
    crash = "Traceback (most recent call last)" in o
    if not fails and not crash:
        return None, "it prints no FAIL line and no traceback to compare by"
    keys = collections.Counter(_norm(ln, tree) for ln in fails)
    raw = {_norm(ln, tree): ln.strip() for ln in fails}
    if crash:
        tail = [ln for ln in lines if ln.strip()][-20:]
        k = "CRASH: " + " / ".join(_norm(ln, tree) for ln in tail)
        keys[k] += 1
        raw[k] = "crash: " + (tail[-1].strip() if tail else "")
    keys["exit %s" % rc] += 1
    raw["exit %s" % rc] = "exit %s" % rc
    return keys, raw


def _short_head(tree):
    r = subprocess.run(["git", "-C", tree, "rev-parse", "--short=10", "HEAD"], capture_output=True, text=True,
                       timeout=GIT_TIMEOUT_S)
    return r.stdout.strip() or "unknown"


def split_pre_existing(top, base, red, run_one, committed=False, flaky=None):
    """RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH (A3, A4): re-run each red test on the base commit, in a
    throwaway shared clone, beside a run on HEAD's commit in another (the door's own run read the working tree; the
    comparison is commit to commit). red: [(c, output, rc)]. -> (still_red [(c, o, note)], pre_existing [(c, o, note)]).
    Pre-existing only when red at both, with every FAIL line, crash and exit code of HEAD's run also in the base's
    (red_signature); green there, anything new, absent there, green at HEAD's commit, past its time, nothing to compare
    by, or no base to read stays red, its note saying which (a reading that could not be taken proves nothing). Known
    limit: numbers of four or more digits are blanked (pids, timestamps), so a FAIL line that differs only in one reads
    as the same line.
    committed: the door's run was on a full checkout of HEAD's commit (is_clone_top), so a red there that is green on the
    re-run of HEAD's commit is a flaky reading of the commit that lands: it goes into `flaky` (a list the caller
    passes), warned, not refused. A plain folder's run read the working tree, and the same reading stays red.
    RIMMANDRAKE_FIX_VISIT_WAIT_MISSES_FAILURE_CITED_ON_OLD_ITEM: selftest_game_lock's timing rows, red at load 14-18 on
    14 cores and green on the re-run, were refused three times as "uncommitted edits make it red"."""
    flaky = [] if flaky is None else flaky
    sha, why = base
    if not sha:
        return [(c, o, "origin/main's reading UNMEASURED (%s): not proved pre-existing" % why) for c, o, _rc in red], []
    still, pre = [], []
    try:
        with full_head_tree(top, rev="HEAD", what="HEAD's commit") as htree, \
                full_head_tree(top, rev=sha, what="the base") as tree:
            here = [x for x in red if os.path.isfile(os.path.join(tree, x[0]["test"]))]
            hsha = _short_head(htree)
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
                got = list(ex.map(lambda x: (run_one(x[0], htree), run_one(x[0], tree)), here))
    except (Refuse, OSError, subprocess.SubprocessError) as e:
        return [(c, o, "origin/main's reading UNMEASURED (%s: %s): not proved pre-existing" % (
            type(e).__name__, e)) for c, o, _rc in red], []
    for c, o, _rc in red:
        if not any(c is x[0] for x in here):
            still.append((c, o, "absent on origin/main %s: a test this change adds" % sha[:10]))
    for (c, o, _rc), ((_h, hrc, ho, _ht), (_b, rc, bo, _t)) in zip(here, got):
        if hrc is None or rc is None:
            still.append((c, o, "%s reading UNMEASURED (ran past its time there): not proved pre-existing" % (
                "HEAD's commit" if hrc is None else "origin/main %s" % sha[:10])))
            continue
        if hrc == 0:
            if committed:   # the door's run was on HEAD's commit too: the same commit read red, then green
                flaky.append((c, o, "red at the door, green on a re-run of the same commit (HEAD %s): a flaky "
                                    "reading; the commit that lands read green" % hsha))
            else:
                still.append((c, o, "red in this working tree but green at HEAD's commit: uncommitted edits make it "
                                    "red, so the commit cannot be compared; not proved pre-existing"))
            continue
        if rc == 0:
            still.append((c, o, "green on origin/main %s: this change turned it red" % sha[:10]))
            continue
        now, raw = red_signature(ho, htree, hrc)
        was, wraw = red_signature(bo, tree, rc)
        if now is None or was is None:
            still.append((c, o, "red on origin/main %s too, but %s %s: not proved pre-existing" % (
                sha[:10], "at HEAD's commit" if now is None else "there", raw if now is None else wraw)))
            continue
        new = [raw[k] for k in now if now[k] > was.get(k, 0)]
        if new:
            still.append((c, o, "red on origin/main %s too, but these FAIL lines are new in this change: %s"
                          % (sha[:10], " | ".join(new[:3]))))
        else:
            pre.append((c, o, "red the same way on origin/main %s before this change" % sha[:10]))
    return still, pre
    try:
        with full_head_tree(top, rev=sha, what="the base") as tree:
            here = [x for x in red if os.path.isfile(os.path.join(tree, x[0]["test"]))]
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
                got = list(ex.map(lambda x: run_one(x[0], tree), here))
    except (Refuse, OSError, subprocess.SubprocessError) as e:
        return still + [(c, o, "origin/main's reading UNMEASURED (%s: %s): not proved pre-existing" % (
            type(e).__name__, e)) for c, o, _rc in red], []
    for c, o, _rc in red:
        if not any(c is x[0] for x in here):
            still.append((c, o, "absent on origin/main %s: a test this change adds" % sha[:10]))
    for (c, o, arc), (_c, rc, bo, _t) in zip(here, got):
        if rc is None:
            still.append((c, o, "origin/main %s reading UNMEASURED (ran past its time there): not proved pre-existing"
                          % sha[:10]))
            continue
        if rc == 0:
            still.append((c, o, "green on origin/main %s: this change turned it red" % sha[:10]))
            continue
        now, raw = red_signature(o, top, arc)
        was, wraw = red_signature(bo, tree, rc)
        if now is None or was is None:
            still.append((c, o, "red on origin/main %s too, but %s %s: not proved pre-existing" % (
                sha[:10], "here" if now is None else "there", raw if now is None else wraw)))
            continue
        new = [raw[k] for k in now if now[k] > was.get(k, 0)]
        if new:
            still.append((c, o, "red on origin/main %s too, but these FAIL lines are new in this change: %s"
                          % (sha[:10], " | ".join(new[:3]))))
        else:
            pre.append((c, o, "red the same way on origin/main %s before this change" % sha[:10]))
    return still, pre


def _committed(full, rel):
    """The check list as HEAD's commit holds it, or None when the commit has none (an uncommitted list names tests the
    checkout does not hold)."""
    p = os.path.join(full, rel)
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


def is_clone_top(top):
    """True when `top` is the top of a git work tree with a commit at HEAD: the door then judges that commit, on a full
    checkout of it (full_head_tree), never the working tree, where a file edited but not named in this publish (or a
    peer's half-done edit) turned a red commit green (RIMMANDRAKE_CHECK_COMMITTED_TREE_NOT_DIRTY_WORKTREE_AT_DOOR).
    A plain folder (a test fixture) is judged where it stands."""
    r = run(top, "rev-parse", "--show-toplevel", check=False)
    return (not r.returncode and os.path.realpath(r.stdout.strip()) == os.path.realpath(top)
            and ref_exists(top, "HEAD"))


def is_sparse(top):
    """True when some tracked file is not checked out (skip-worktree: a sparse clone, scratch_clone.py's default)."""
    r = run(top, "ls-files", "-t", check=False)
    return any(ln.startswith("S ") for ln in (r.stdout or "").splitlines())


CHECKTREE_PREFIX = "rm-treecheck-"
# RIMMANDRAKE_REUSE_TREECHECK_TREE_EACH_PUBLISH_WRITES_THREE_GIG: one check tree per clone is kept and reused; a reuse
# rewrites only the files that differ (page: design/specs/2026-11-25-treecheck-kept-tree/boundary.md)
CHECKTREE_KEPT = CHECKTREE_PREFIX + "kept"
CHECKTREE_KEPT_LOCK = CHECKTREE_KEPT + ".lock"
PRISTINE_CONFIG = "rm-pristine-config"       # in the kept tree's .git: its config as the clone made it
# budget: danger=the sweep deletes the check tree of a live landing; longest=584s (the longest door-check wall of 636 publishes,
# budget: 14 days to 2026-11-24; one check may now take 6000 s)
CHECKTREE_STALE_S = 21600


def _io_written():
    """-> bytes this process and its reaped children have written so far (/proc/self/io write_bytes), or None."""
    try:
        with open("/proc/self/io") as f:
            for ln in f:
                if ln.startswith("write_bytes:"):
                    return int(ln.split()[1])
    except (OSError, ValueError):
        pass
    return None


def _treegit(tree, *a):
    """One git call on a check tree, its git dir named outright: a tree with no .git of its own must never reach the
    clone around it (the kept tree lives inside the clone's git dir, where git would find that repo instead)."""
    return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.trustctime=true",
                           "-c", "core.checkStat=default", "--git-dir", os.path.join(tree, ".git"),
                           "--work-tree", tree, *a], capture_output=True, text=True, timeout=CHECKTREE_GIT_TIMEOUT_S)


def _sync_kept_refs(top, tree):
    """Give the tree the refs a fresh `git clone --shared` of `top` has: refs/remotes/origin/<b> for each of top's
    branches, top's tags, top's current branch, origin/HEAD naming it; every other ref (a stale origin/main, a branch or
    stash a check run made) is deleted. -> None, or why it could not."""
    r = run(top, "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads", "refs/tags", check=False)
    if r.returncode:
        return "git for-each-ref in the clone: %s" % r.stderr.strip()
    want, heads = {}, {}
    for ln in r.stdout.splitlines():
        sha, ref = ln.split(" ", 1)
        if ref.startswith("refs/heads/"):
            heads[ref] = sha
            want["refs/remotes/origin/" + ref[len("refs/heads/"):]] = sha
        else:
            want[ref] = sha
    cur = run(top, "symbolic-ref", "-q", "HEAD", check=False).stdout.strip()
    if cur in heads:
        want[cur] = heads[cur]
    r = _treegit(tree, "for-each-ref", "--format=%(objectname) %(refname) %(symref)")
    if r.returncode:
        return "git for-each-ref in the kept tree: %s" % r.stderr.strip()
    have = {}
    for ln in r.stdout.splitlines():
        sha, ref, sym = (ln.split(" ") + [""])[:3]
        if not sym:
            have[ref] = sha
    todo = ["delete %s\n" % ref for ref in sorted(have) if ref not in want]
    todo += ["update %s %s\n" % (ref, sha) for ref, sha in sorted(want.items()) if have.get(ref) != sha]
    if todo:
        r = subprocess.run(["git", "--git-dir", os.path.join(tree, ".git"), "update-ref", "--no-deref", "--stdin"],
                           input="".join(todo), capture_output=True, text=True, timeout=CHECKTREE_GIT_TIMEOUT_S)
        if r.returncode:
            return "git update-ref: %s" % r.stderr.strip()
    oh = ["symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/" + cur[len("refs/heads/"):]] \
        if cur in heads else ["symbolic-ref", "-q", "--delete", "refs/remotes/origin/HEAD"]
    r = _treegit(tree, *oh)
    if r.returncode and cur in heads:
        return "git symbolic-ref origin/HEAD: %s" % r.stderr.strip()
    return None


def _reuse_kept(top, tree, head):
    """Make the kept tree exactly `head`: no file a check run left, no edit, the refs of a fresh clone. git rewrites
    only the paths that differ from what the tree holds. -> None when it is exact now, else why it is not."""
    gd = os.path.join(tree, ".git")
    if not os.path.isdir(gd):
        return "it has no .git"
    for n in os.listdir(gd):            # a red re-run's tree inside it, left by a killed run: the lock says nobody is in it
        if n.startswith(CHECKTREE_PREFIX):
            _rmtree_hard(os.path.join(gd, n))
    r = _treegit(tree, "rev-parse", "--absolute-git-dir")
    if r.returncode or os.path.realpath(r.stdout.strip()) != os.path.realpath(gd):
        return "git cannot read it: %s" % (r.stderr.strip() or r.stdout.strip())
    try:
        shutil.copyfile(os.path.join(gd, PRISTINE_CONFIG), os.path.join(gd, "config"))   # a check may have set config
    except OSError as e:
        return "its pristine config: %s" % e
    for a in (["clean", "-q", "-ffdx"], ["checkout", "-q", "-f", "--detach", head]):
        r = _treegit(tree, *a)
        if r.returncode:
            return "git %s: %s" % (a[0], (r.stderr.strip().splitlines() or [""])[-1])
    why = _sync_kept_refs(top, tree)
    if why:
        return why
    r = _treegit(tree, "rev-parse", "HEAD")
    if r.returncode or r.stdout.strip() != head:
        return "its HEAD reads %r, not %s" % (r.stdout.strip() or r.stderr.strip(), head[:12])
    r = _treegit(tree, "status", "--porcelain=v1", "--ignored", "-uall", "--no-renames")
    if r.returncode or r.stdout.strip():
        return "git status after the reset: %s" % ((r.stderr or r.stdout).strip().splitlines() or [""])[0]
    r = _treegit(tree, "ls-files", "-v")
    odd = [ln for ln in r.stdout.splitlines() if not ln.startswith("H ")]
    if r.returncode or odd:
        return "a path marked assume-unchanged or skip-worktree: %s" % (odd[:1] or [r.stderr.strip()])[0]
    return None


def _fresh_tree(top, tree, head, what):
    """A `git clone --shared` (no objects copied) of `top` at `tree`, checked out at `head`; raises Refuse."""
    for a in (["clone", "-q", "--shared", "--no-checkout", top, tree],
              ["-C", tree, "checkout", "-q", "--detach", head]):
        r = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *a], capture_output=True, text=True,
                           timeout=CHECKTREE_GIT_TIMEOUT_S)
        if r.returncode:
            raise Refuse("the full checkout of %s for the checks failed: git %s: %s"
                         % (what, a[0] if a[0] != "-C" else a[2], r.stderr.strip()))
    shutil.copyfile(os.path.join(tree, ".git", "config"), os.path.join(tree, ".git", PRISTINE_CONFIG))


def _rmtree_hard(p):
    """shutil.rmtree that first gives back the write bit a check run took off a folder (git clean cannot remove what is
    in a read-only folder, and neither can a plain rmtree, so the kept tree would never be made fresh again)."""
    def fix(func, path, _exc):
        try:
            os.chmod(os.path.dirname(path), 0o700)
            if os.path.isdir(path) and not os.path.islink(path):
                os.chmod(path, 0o700)
            func(path)
        except OSError:
            pass
    shutil.rmtree(p, **({"onexc": fix} if sys.version_info >= (3, 12) else {"onerror": fix}))


def _take_kept_lock(gitdir):
    """-> (fd, None) holding the kept tree's flock, or (None, why) when another user holds it or it cannot be opened."""
    try:
        fd = os.open(os.path.join(gitdir, CHECKTREE_KEPT_LOCK), os.O_CREAT | os.O_RDWR, 0o644)
    except OSError as e:
        return None, "its lock could not be opened: %s" % e
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return None, "another check of this clone holds the kept tree"
    return fd, None


@contextlib.contextmanager
def full_head_tree(top, rev="HEAD", what="HEAD", lands=None):
    """The checks judge the commit, not the working tree: a sparse clone lacks the files they read (they went red or
    green blind, lessons 2026-11-15 194926Z/195130Z) and a full one holds edits the commit does not (is_clone_top).
    Yield a full checkout of `rev`: the clone's kept check tree (CHECKTREE_KEPT, a `git clone --shared` inside this
    clone's git dir, no objects copied), made exactly that commit by _reuse_kept, which rewrites only the files that
    differ; one checkout wrote 3.36 GB on SteveDesktop when every publish made a new tree (2026-11-25). A kept tree that
    cannot be made exact is made fresh. While another user holds the kept tree (a nested call, split_pre_existing), the
    call makes a fresh tree of its own and removes it after. A random-named leftover of a killed run (older than
    CHECKTREE_STALE_S) is removed first. Page: design/specs/2026-11-25-treecheck-kept-tree/boundary.md."""
    gitdir = out(top, "rev-parse", "--absolute-git-dir")
    for n in os.listdir(gitdir):
        p = os.path.join(gitdir, n)
        if n.startswith(CHECKTREE_PREFIX) and n not in (CHECKTREE_KEPT, CHECKTREE_KEPT_LOCK) \
                and time.time() - os.path.getmtime(p) > CHECKTREE_STALE_S:
            shutil.rmtree(p, ignore_errors=True)
    head = out(top, "rev-parse", rev)
    kept = os.path.join(gitdir, CHECKTREE_KEPT)
    t0, w0 = time.monotonic(), _io_written()
    # a check tree's own red re-runs (split_pre_existing is handed the kept tree as top) keep nothing inside it
    fd, busy = (None, "a check tree keeps no tree of its own") \
        if os.path.basename(os.path.realpath(top)).startswith(CHECKTREE_PREFIX) else _take_kept_lock(gitdir)
    tree = None
    try:
        if fd is not None:
            why = _reuse_kept(top, kept, head) if os.path.lexists(kept) else "none kept yet"
            if why is None:
                how = "the kept tree, reused"
                tree = kept
            else:
                if os.path.lexists(kept):
                    print("tree checks: the kept check tree cannot be made exact (%s): making it fresh" % why, flush=True)
                    _rmtree_hard(kept)
                if os.path.lexists(kept):
                    busy = "the kept tree could not be removed"
                else:
                    tree = kept
                    try:
                        _fresh_tree(top, kept, head, what)
                    except BaseException:
                        shutil.rmtree(kept, ignore_errors=True)
                        raise
                    how = "the kept tree, made fresh (%s)" % why
        if tree is None:
            tree = tempfile.mkdtemp(prefix=CHECKTREE_PREFIX, dir=gitdir)
            _fresh_tree(top, tree, head, what)
            how = "a fresh tree of its own (%s)" % busy
        # lands: the checkout is the tree as it lands, so its origin/main is that commit. The clone's own origin/main
        # there is this clone's local main, and a landing replayed onto a newer origin read every sha origin gained
        # since as "not on origin/main" (selftest_modledger_tree SHA_NOT_ON_BASE, 2026-11-22)
        if lands:
            r = _treegit(tree, "update-ref", "refs/remotes/origin/main", head)
            if r.returncode:
                raise Refuse("the full checkout of %s for the checks failed: git update-ref: %s"
                             % (what, r.stderr.strip()))
        w1 = _io_written()
        print("tree checks: %s, running them on a full checkout of %s %s: %s (%.1f s, wrote %s)"
              % ("the commit is what lands" if (rev == "HEAD" if lands is None else lands) else "a red test re-run",
                 what, head[:12], how, time.monotonic() - t0,
                 "%.0f MB" % ((w1 - w0) / 1e6) if w0 is not None and w1 is not None else "UNMEASURED bytes"),
              flush=True)
        yield tree
    finally:
        if tree is not None and tree != kept:
            shutil.rmtree(tree, ignore_errors=True)
        if fd is not None:
            os.close(fd)                                 # closing releases the flock


def _kill_own_sessions():
    """SIGKILL every process group this process started as its own session (progress_guard runs each check so), so a
    check does not live on, writing into the kept tree, after its publish ended."""
    me = os.getpid()
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open("/proc/%s/stat" % d) as f:
                st = f.read().rsplit(")", 1)[1].split()
            if int(st[1]) == me and int(st[3]) == int(d):        # ppid is this process, and it leads its own session
                os.killpg(int(d), 9)
        except (OSError, ValueError, IndexError):
            pass


def _on_term(signum, _frame):
    """SIGTERM (`timeout N ./publish`, a unit stop) ends publish through its clean-up: the check children die and every
    `finally` runs, so no random-named check tree is left (bench's rm-treecheck-rqp5014m, 4.6 GB, was left by
    `timeout 530 ./publish` on 2026-11-24 7:45 PM PST, when the default action skipped them)."""
    _kill_own_sessions()
    raise SystemExit(128 + signum)


# RIMMANDRAKE_STRIP_HOLDER_WRITER_FROM_DOOR_TESTS: a pilot holder's unit writes the mod ledger as HOLDER.<lease>; a door
# test is about the tree, not the publisher, and one that writes a DISPATCH or BACKFILL shard was refused under it.
LEDGER_IDENTITY = ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN")
# RIMMANDRAKE_MEASURE_FLOWWORKS_DIG_CALL_QUARTER_SECOND_ON_SITTING_MAP: the same for the publisher's GAME. A game-b run's
# unit carries `game_instance.py env b`, and door tests that read the caller's game (selftest_game_lock,
# selftest_conductor_acts and three more) read red under it, red on the base too, so every game-b publish showed them
# as PRE-EXISTING reds that hid real ones (measured 2026-11-21).
GAME_CHOICE = ("RM_GAME_INSTANCE", "RM_GAME_USERDATA", "RM_GAME_LOGDIR", "GABP_SERVER_PORT", "GABP_TOKEN",
               "RIMFLOW_DRIVER_LOCK")


# RIMMANDRAKE_RERUN_DOOR_CHECK_DEAD_ON_ENOMEM_NOT_RED: a check killed by the machine's memory measured nothing, and one
# refused a sound landing (2026-11-23). Only a traceback's last line counts: a check's own FAIL text is a red.
ENOMEM_RX = re.compile(r"^OSError: \[Errno 12\]|^MemoryError\b")


# The backstop of one door check that spins; a check that does nothing ends sooner (progress_guard.SILENCE_S).
# budget: danger=a test in an endless loop holds a landing with no end; evidence=none measured, the loop of any new test;
# budget: longest=599s (selftest_maturation_autonomy.py PASS at load 45, 2026-11-24; 36 s alone)
CHECK_CAP_S = 6000


def died_on_enomem(rc, output):
    last = (output.strip().splitlines() or [""])[-1]
    return rc not in (0, None) and bool(ENOMEM_RX.match(last))


def _run_tree_checks(top, cfg, what="tree check", base=None, committed=False):
    """base: (sha, why) from door_base for the pipeline checks, whose reds are re-run on it (split_pre_existing); None
    for the whole-tree checks, which refuse on any red."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import progress_guard       # a hung check ends on no progress; a slow one on a loaded machine does not
    limit = cfg.get("timeout_s", CHECK_CAP_S)
    env = {k: v for k, v in os.environ.items() if k not in LEDGER_IDENTITY + GAME_CHOICE}

    def one(c, tree=top):
        t0 = time.monotonic()
        # a TMPDIR of the check's own, gone after: every publish ran selftest_alpha_biomes_census.py in ours, and its
        # five git repos a run were 2,236 of the scratch cleaner's 3,836 waiting clones (2026-11-18)
        tdir = tempfile.mkdtemp(prefix="publish_check_")
        try:
            argv = [sys.executable, os.path.join(tree, c["test"])] + [str(x) for x in c.get("args") or []]
            r = progress_guard.run(argv, cwd=tree, cap_s=limit, env=dict(env, TMPDIR=tdir))
            return c, r.returncode, (r.stdout or "") + (r.stderr or ""), time.monotonic() - t0
        except subprocess.TimeoutExpired as e:      # a Hung of the guard: it names which bound ended the check
            return c, None, str(e), time.monotonic() - t0
        finally:
            shutil.rmtree(tdir, ignore_errors=True)
    t0 = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(one, cfg["checks"]))
    for i, (c, rc, o, _t) in enumerate(res):   # again once, alone (the six at a time are over); its second reading stands
        if died_on_enomem(rc, o):
            print("%s %s died on out of memory (it measured nothing): ran again, alone" % (what, c["test"]))
            res[i] = one(c)
    wall = time.monotonic() - t0
    slow = [(c["test"], o) for c, rc, o, _t in res if rc is None]
    for c, _rc, o, _t in res:   # a shadow check is shown, never refused
        if c.get("shadow"):
            print("shadow %s %s: %s" % (what, c["test"], (o.strip().splitlines() or ["(no output)"])[-1]))
    red = [(c, o, rc) for c, rc, o, _t in res if rc not in (0, None) and not c.get("shadow")]
    for t, why in slow:
        print("WARNING: %s %s was ended (%s): UNMEASURED, not refused" % (what, t, why))
    notes, pre, flaky = {}, [], []
    if red and base is not None:
        red, pre = split_pre_existing(top, base, red, one, committed=committed, flaky=flaky)
        for c, o, note in flaky:
            fails = [ln.strip() for ln in o.splitlines() if FAIL_RX.match(ln)][:3]
            print("WARNING: FLAKY, not refused: %s %s is %s (%s). A defect of its own to fix and file. rerun: python3 %s"
                  % (what, c["test"], note, "; ".join(fails) or "no FAIL line", c["test"]))
        for c, o, note in pre:
            fails = [ln.strip() for ln in o.splitlines() if FAIL_RX.match(ln)][:3]
            print("WARNING: PRE-EXISTING RED, not refused: %s %s is %s (%s). Your change did not make it; it is a defect "
                  "of its own to fix and file. rerun: python3 %s" % (what, c["test"], note,
                                                                   "; ".join(fails) or "no FAIL line", c["test"]))
        notes = {c["test"]: note for c, _o, note in red}
        red = [(c, o) for c, o, _note in red]
    else:
        red = [(c, o) for c, o, _rc in red]
    if red:
        lines = []
        for c, o in red:
            fails = [ln.strip() for ln in o.splitlines() if FAIL_RX.match(ln)][:3]
            lines.append("  %s\n    %s\n%s    fix: %s\n    rerun: python3 %s"
                         % (c["test"], "\n    ".join(fails) or (o.strip().splitlines() or ["(no output)"])[-1],
                            "    %s\n" % notes[c["test"]] if c["test"] in notes else "",
                            c.get("fix", "see the test's FAIL line"), c["test"]))
        raise Refuse("%d %s(s) red after your commit (it stays on HEAD; fix, then publish again):\n%s"
                     % (len(red), "whole-tree check" if what == "tree check" else what, "\n".join(lines)))
    print("%ss: %d green%s%s in %.1f s" % (what, len(res) - len(slow) - len(pre) - len(flaky),
                                           ", %d PRE-EXISTING red (not refused)" % len(pre) if pre else "",
                                           ", %d FLAKY (not refused)" % len(flaky) if flaky else "", wall))
    return wall


def _changed_since_origin(top):
    """-> the paths HEAD's local commits touch, or None when there is no origin/main to diff against (unknown, which the
    checks treat as 'run everything', never as 'nothing changed')."""
    _, track, _label = target_ref(top)
    if not ref_exists(top, track):
        return None
    r = run(top, "diff", "--name-only", "%s...HEAD" % track, check=False)
    return [p for p in (r.stdout or "").splitlines() if p]


SKIP_VARS = ("RM_PUBLISH_SKIP_TREE_CHECKS", "RM_PUBLISH_SKIP_PIPELINE_CHECKS")
SKIP_TRAILER = "Door-skipped"


def door_skips():
    """-> [(variable, reason)] for each door skip set in the environment, the reason on one line."""
    return [(v, " ".join(os.environ[v].split())) for v in SKIP_VARS if os.environ.get(v, "").strip()]


def with_skip_trailers(top, msg, skips):
    """The message with one `Door-skipped: <VAR>: <why>` trailer per skip, merged into any trailer block it has
    (RIMMANDRAKE_RECORD_DOOR_SKIP_FOUR_LANDINGS_LEFT_NO_TRACE: a skip only printed a line, so an audit could not
    tell which landings skipped the door)."""
    if not skips:
        return msg
    args = [a for v, why in skips for a in ("--trailer", "%s: %s: %s" % (SKIP_TRAILER, v, why))]
    # explicit policy: a trailer.ifexists=replace in config kept only the last skip's reason
    r = subprocess.run(["git", "interpret-trailers", "--where", "end", "--if-exists", "add", "--if-missing", "add", *args],
                       cwd=top, input=msg, capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise Refuse("cannot write the door-skip trailer: %s" % (r.stderr or r.stdout).strip())
    return r.stdout


def _undo(top, made, named):
    """Take this run's refused commit back off HEAD, only if HEAD is still that commit: the publish lock does not cover
    a peer's plain `git commit`, and a bare `reset --soft <made>~1` took one made on top of ours during the checks off
    the branch too (RIMMANDRAKE_GUARD_PUBLISH_ROLLBACK_AGAINST_PEER_COMMIT). -> what was done, for the refusal."""
    if run(top, "update-ref", "-m", "publish: undo a refused commit", "HEAD", made + "~1", made, check=False).returncode:
        return ("HEAD moved past this run's commit %s during the checks (a commit made meanwhile), so HEAD was left as "
                "it is: both commits are still on the branch, unpublished" % made[:12])
    run(top, "reset", "-q", "--", *named)
    return "this run's commit was undone: your files are as you left them"


LEDGER_SHARDS = "infrastructure/state/ledger/events/"
ITEMS_DIR = "infrastructure/state/items/"


def carried_prose_moves(top, named):
    """-> the prose-move paths `rimflow close` left on disk, carried with a ledger shard. close renames
    items/<ID>.md to items/closed/<ID>.md and leaves the commit to the caller; a helper publishes only its shard, so
    the move never landed (six items drifted by 2026-11-20, RIMMANDRAKE_LAND_CLOSED_PROSE_MOVE_HELPERS_PUBLISH_SHARD_ONLY).
    Only the exact pair counts: a tracked items/<ID>.md deleted from the tree whose items/closed/<ID>.md exists. A
    publish that names no ledger shard carries nothing."""
    if not any(p.startswith(LEDGER_SHARDS) for p in named):
        return []
    r = run(top, "ls-files", "--deleted", "-z", "--", ITEMS_DIR)     # unreadable: a Refuse, never "none"
    out_ = []
    for p in (r.stdout or "").split("\0"):
        rest = p[len(ITEMS_DIR):] if p.startswith(ITEMS_DIR) else ""
        if not rest.endswith(".md") or "/" in rest:
            continue
        closed = ITEMS_DIR + "closed/" + rest
        if os.path.isfile(os.path.join(top, closed)):
            out_ += [x for x in (p, closed) if x not in named]
    return out_


PROSE_RANGE = []        # [base, local head, landed sha] of this run's landing, for the prose check that main() runs after it


def prose_after(top):
    """The faults of the guiding prose that this run landed, for the same writer (guiding_prose.py; page
    design/specs/2026-11-23-guiding-prose-check/boundary.md). Run by main() after the landing, outside the clone lock: it
    refuses nothing and never changes the exit code."""
    if not PROSE_RANGE:
        return
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import guiding_prose
        text = guiding_prose.after_publish(top, *PROSE_RANGE)
    except Exception as e:  # noqa: BLE001  the landing is done
        text = "GUIDING PROSE: UNMEASURED, the check did not load (%s: %s). The landing is complete." % (type(e).__name__, e)
    if text:
        print(text)


def _publish(top, paths, msg, cwd=None):
    skips = door_skips()
    if paths:
        if not msg or not msg.strip():
            raise Refuse("a message is required (-m or -F)")
        named = rel_paths(top, paths, cwd or top)
        carried = carried_prose_moves(top, named)
        if carried:
            print("carried with the ledger shard (rimflow close moved the prose): %s" % ", ".join(carried))
            named = sorted(set(named) | set(carried))
        made = commit(top, named, with_skip_trailers(top, msg if msg.endswith("\n") else msg + "\n", skips))
        if not made:
            print("no change in the named paths; pushing any local commits")
        warn_owner_shard(top, named)
    else:
        named, made = [], None
    if skips and not made:
        raise Refuse("%s is set, but this landing makes no commit of its own to carry the reason (no paths named, or "
                     "nothing changed in them): name the paths, so the skip is recorded on the landed commit"
                     % ", ".join(v for v, _ in skips))
    if skips:
        # only this run's commit carries the reason: an earlier local commit would pass the door unrecorded. Read a
        # fresh origin (a stale tracking ref called an already-pushed commit unpublished); unreadable is a refusal.
        # (If the replay drops ours as already upstream, nothing lands under the skip, so no record is owed.)
        _, track, _label = target_ref(top)
        fetched = run(top, "fetch", "-q", REMOTE, check=False).returncode == 0 and ref_exists(top, track)
        if not fetched or not is_ancestor(top, made + "~1", track):
            raise Refuse("%s is set, but %s (%s)"
                         % (", ".join(v for v, _ in skips),
                            "earlier local commits sit under this run's commit and would land past the door with no "
                            "record: publish them first, without the skip" if fetched else
                            "%s could not be fetched, so whether earlier local commits would land past the door with no "
                            "record cannot be told" % track, _undo(top, made, named)))
    changed = _changed_since_origin(top)
    try:
        polish_door_check(top)
        door_checks(top, changed)
    except Refuse as e:
        if not made:
            raise
        # RIMMANDRAKE_UNDO_REFUSED_PUBLISH_COMMIT_NEXT_RUN_LANDED_IT: a refused commit left on HEAD was pushed by the next
        # publish ("no change in the named paths; pushing any local commits"), the refused file in it (2026-11-17): undo it,
        # so HEAD, the index and the working tree are as they were before this run
        raise Refuse("%s\n    (%s; fix, then publish again)" % (e, _undo(top, made, named)))
    run(top, "fetch", "-q", REMOTE)
    _, track, label = target_ref(top)
    head = out(top, "rev-parse", "HEAD")
    if label == BRANCH and is_ancestor(top, head, track):
        raise Refuse("nothing to publish: HEAD is already on origin/main")
    base = run(top, "merge-base", head, track, check=False).stdout.strip() if ref_exists(top, track) else ""
    sha = land(top)
    PROSE_RANGE[:] = [base, head, sha] if base else []
    print("PUBLISHED %s%s" % (sha, "" if label == BRANCH else "  (on %s)" % label))
    return sha


def build_parser():
    """The parser of main(), apart so that brief_commands.py fills a run's command lines from it."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("-m", "--message")
    ap.add_argument("--ledger", action="store_true", help="land only the named ledger shards' new lines")
    ap.add_argument("-F", "--file", help="read the message from a file ('-' = stdin)")
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    # Progress goes to stdout and REFUSED to stderr. Under a pipe stdout is block-buffered, so `2>&1 | tail` printed the
    # progress AFTER the refusal and hid it (RIMMANDRAKE_FLUSH_PUBLISH_OUTPUT_SO_TAIL_SHOWS_REFUSAL): line-buffer it.
    sys.stdout.reconfigure(line_buffering=True)
    signal.signal(signal.SIGTERM, _on_term)
    msg = a.message
    if a.file:
        msg = sys.stdin.read() if a.file == "-" else open(a.file).read()
    try:
        sha = publish(toplevel(), a.paths, msg, os.getcwd(), ledger=a.ledger)
        if sha:
            print("close with: rimflow close <ID> --sha %s" % sha[:12])
            prose_after(toplevel())
        return 0
    except IndexLockHeld as e:
        print("REFUSED (index lock held): %s" % e, file=sys.stderr)
        return LOCK_HELD_EXIT
    except Refuse as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
