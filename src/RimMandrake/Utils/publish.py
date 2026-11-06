#!/usr/bin/env python3
"""Commit named paths and land them with plain git — the thin wrapper agents already know.

    ./publish -m "subject" path/one path/two     commit those paths, rebase, push, print PUBLISHED <sha>
    ./publish -F msg.txt path/one                message from a file ('-' = stdin)
    ./publish                                    push local commits already made (no new commit)

It is exactly: `git add --all -- <paths>` + `git commit -- <paths>` (pathspec on the commit, so
nothing else staged rides along) + a replay of the local commits onto origin/main by plumbing, moved
there with `git reset --keep` (never a stash; see rebase()) + push, retried up to 8 times when origin
moved under it, never forced. It pushes a seat clone
(/home/mandrake/rm/<seat>) to HEAD:main.

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
import contextlib
import fcntl
import os
import re
import subprocess
import sys
import time

REMOTE, BRANCH = "origin", "main"
RM_ROOT = os.environ.get("PUBLISH_RM_ROOT", "/home/mandrake/rm")
MAX_TRIES = 8
GIT_TIMEOUT_S = float(os.environ.get("PUBLISH_GIT_TIMEOUT", "300"))   # one git call, push included; a hang is a loud TimeoutExpired, not a stall
before_push = None          # selftest hook: called(attempt) between rebase and push
before_reset = None         # selftest hook: called() between the replay and the HEAD check
LOCK_TIMEOUT = float(os.environ.get("PUBLISH_LOCK_TIMEOUT", "600"))


class Refuse(Exception):
    pass


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
    for i in range(12):                                  # a plain-git peer may hold .git/index.lock for a moment
        r = subprocess.run(["git", *args], cwd=top, capture_output=True, text=True, timeout=GIT_TIMEOUT_S, env=env)
        if not (r.returncode and "index.lock" in r.stderr and i < 11):
            break
        time.sleep(0.25 * (i + 1))
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
    for i in range(12):
        r = subprocess.run(["git", "commit", "-q", "-F", "-", "--", *literal(paths)], cwd=top,
                           input=msg, capture_output=True, text=True)
        if not (r.returncode and "index.lock" in r.stderr and i < 11):
            break
        time.sleep(0.25 * (i + 1))
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
    if is_ancestor(top, up, head) or is_ancestor(top, head, up):
        return rebuilt                                   # already on top of origin, or nothing local
    # git cherry never lists a merge, so a resolution edited inside one would vanish at the reset: ask rev-list
    merges = out(top, "rev-list", "--merges", "%s..%s" % (up, head)).split()
    if merges:
        raise Refuse("local commit %s is a merge; publish cannot replay it" % merges[0][:12])
    todo = [ln[2:].strip() for ln in out(top, "cherry", up, head).splitlines() if ln.startswith("+")]
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
            print("replay of %s: DLL conflict in %s; took origin's side, will rebuild from committed source"
                  % (c[:12], ", ".join(sorted(set(paths)))))
        tree = dedupe_shards(top, tree, tip, c)
        if tree == out(top, "rev-parse", tip + "^{tree}"):
            continue                                     # nothing left of it: a DLL pair, or already on origin
        meta = out(top, "show", "-s", "--format=%an%x00%ae%x00%aI", c).split("\0")
        env = git_env(GIT_AUTHOR_NAME=meta[0], GIT_AUTHOR_EMAIL=meta[1], GIT_AUTHOR_DATE=meta[2])
        body = out(top, "show", "-s", "--format=%B", c) + "\n"
        tip = subprocess.run(["git", "commit-tree", tree, "-p", tip, "-F", "-"], cwd=top, input=body, env=env,
                             capture_output=True, text=True, check=True).stdout.strip()
    # seat_sync.reset_keep: a plain --keep would DELETE every file upstream stopped tracking (Transient/,
    # 2026-10-18); it keeps them on disk and otherwise behaves exactly like `git reset --keep`.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
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
            return subprocess.run(["git", *a], cwd=top, env=env, capture_output=True, text=True, check=True).stdout
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
    dest, track, label = target_ref(top)
    guard_retried = False
    for attempt in range(MAX_TRIES):
        stranded = None
        try:
            rebuilt = rebase(top)
            if rebuilt:
                rebuild_dlls(top, rebuilt)
            head = out(top, "rev-parse", "HEAD")
        except Stranded as s:
            stranded, head = s, s.tip                    # land the replay; only this clone's branch waits
        if label == BRANCH and is_ancestor(top, head, track):
            warn_stranded(stranded)
            return head                                  # nothing local left to push
        if before_push:
            before_push(attempt)
        r = run(top, "push", "-q", REMOTE, "%s:%s" % (head, dest), check=False)
        if not r.returncode:
            run(top, "fetch", "-q", REMOTE, check=False)
            warn_stranded(stranded)
            return head
        err = (r.stderr or r.stdout).strip()
        # Ambiguity check before any retry: the remote may have taken it before we gave up.
        run(top, "fetch", "-q", REMOTE, check=False)
        if ref_exists(top, track) and is_ancestor(top, head, track):
            print("push reported failure but %s already contains %s — it landed" % (label, head[:12]))
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
        nonff = re.search(r"non-fast-forward|fetch first|\[rejected\]|failed to update ref", err)
        if not nonff:
            if attempt + 1 < MAX_TRIES:
                print("push failed (%s); retrying" % err.splitlines()[-1] if err else "push failed")
                time.sleep(min(2 ** attempt, 20))
                continue
            raise Refuse("push failed: %s" % err)
        if label != BRANCH:
            raise Refuse("%s already holds a submission this one does not contain — the seat has not "
                         "landed it yet (it deletes the submit ref when it does). Not forcing.\n%s"
                         % (label, err))
        print("origin moved (attempt %d); rebasing and retrying" % (attempt + 1))
        time.sleep(0.5 * (attempt + 1))
    raise Refuse("origin kept moving: %d non-fast-forward rejections in a row" % MAX_TRIES)


def publish(top, paths, msg, cwd=None):
    """Paths are relative to `cwd` (the caller's directory; defaults to the repo top)."""
    guard_mnt(top)
    with clone_lock(top):
        return _publish(top, paths, msg, cwd)


def _publish(top, paths, msg, cwd=None):
    if paths:
        if not msg or not msg.strip():
            raise Refuse("a message is required (-m or -F)")
        made = commit(top, rel_paths(top, paths, cwd or top), msg if msg.endswith("\n") else msg + "\n")
        if not made:
            print("no change in the named paths; pushing any local commits")
    run(top, "fetch", "-q", REMOTE)
    _, track, label = target_ref(top)
    head = out(top, "rev-parse", "HEAD")
    if label == BRANCH and is_ancestor(top, head, track):
        raise Refuse("nothing to publish: HEAD is already on origin/main")
    sha = land(top)
    if label == BRANCH:
        wake_relentless(top, sha)
    print("PUBLISHED %s%s" % (sha, "" if label == BRANCH else "  (on %s)" % label))
    return sha


def wake_relentless(top, sha):
    """A landed commit may close a blocker: Relentless acts on it now, not at its next heartbeat
    (rimflow/relentless_wake.py, RELENTLESS_WIRE_WAKE_ON_STATE_CHANGE). Only a RimMandrake clone pokes (a test repo has
    no relentless_wake.py and wakes nobody). Never fails the publish."""
    w = os.path.join(top, "src", "RimMandrake", "rimflow", "relentless_wake.py")
    if not os.path.isfile(w):
        return
    try:
        subprocess.run([sys.executable, w, "poke", "publish", sha], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("-m", "--message")
    ap.add_argument("-F", "--file", help="read the message from a file ('-' = stdin)")
    a = ap.parse_args(argv)
    msg = a.message
    if a.file:
        msg = sys.stdin.read() if a.file == "-" else open(a.file).read()
    try:
        sha = publish(toplevel(), a.paths, msg, os.getcwd())
        if sha:
            print("close with: rimflow close <ID> --sha %s" % sha[:12])
        return 0
    except Refuse as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
