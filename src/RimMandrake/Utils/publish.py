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
origin changed. Unrelated dirty files are never touched.

Committed mod DLLs are landed here, never by hand: a replay conflict on ONLY .dll/.dll.srchash pairs takes
origin's side and then rebuilds each such DLL from the source committed at the new HEAD, in a throwaway src-only
`git clone --shared` (never the worktree, so a peer's uncommitted C# cannot leak in), and commits the pair; a
pre-push DLL_SOURCE_STAMP_GUARD_1 refusal does the same rebuild and retries once (rebuild_dlls()).

It REFUSES in the /mnt/d tree: that tree becomes a read-only mirror of origin/main (§2.3), and the
old plumbing route that published from it (temp index, --catchup, --sync, --commit, --worktrees)
is deleted, not kept for emergencies. With no owned clone, make one on ext4.
"""
import argparse
import os
import re
import subprocess
import sys
import time

REMOTE, BRANCH = "origin", "main"
RM_ROOT = os.environ.get("PUBLISH_RM_ROOT", "/home/mandrake/rm")
MAX_TRIES = 8
before_push = None          # selftest hook: called(attempt) between rebase and push


class Refuse(Exception):
    pass


def run(top, *args, check=True):
    r = subprocess.run(["git", *args], cwd=top, capture_output=True, text=True)
    if check and r.returncode:
        raise Refuse("git %s failed: %s" % (" ".join(args[:3]), (r.stderr or r.stdout).strip()))
    return r


def out(top, *args):
    return run(top, *args).stdout.strip()


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
            "or /home/mandrake/rm/foundry (i.e. /home/mandrake/rm/<seat>) — or make an ext4 clone: "
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
    r = subprocess.run(["git", "commit", "-q", "-F", "-", "--", *paths], cwd=top,
                       input=msg, capture_output=True, text=True)
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
    a dirty one. Your commit is intact on HEAD after any refusal."""
    run(top, "fetch", "-q", REMOTE, check=False)
    _, track, _ = target_ref(top)
    rebuilt = set()
    if not ref_exists(top, track):
        return rebuilt
    up, head = out(top, "rev-parse", track), out(top, "rev-parse", "HEAD")
    if is_ancestor(top, up, head) or is_ancestor(top, head, up):
        return rebuilt                                   # already on top of origin, or nothing local
    todo = [ln[2:].strip() for ln in out(top, "cherry", up, head).splitlines() if ln.startswith("+")]
    tip = up
    for c in todo:
        if len(out(top, "rev-list", "--parents", "-n1", c).split()) != 2:
            raise Refuse("local commit %s is a merge; publish cannot replay it" % c[:12])
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
            if tree == out(top, "rev-parse", tip + "^{tree}"):
                continue                                 # the commit was only that DLL pair: nothing left of it
        meta = out(top, "show", "-s", "--format=%an%x00%ae%x00%aI", c).split("\0")
        env = dict(os.environ, GIT_AUTHOR_NAME=meta[0], GIT_AUTHOR_EMAIL=meta[1], GIT_AUTHOR_DATE=meta[2])
        body = out(top, "show", "-s", "--format=%B", c) + "\n"
        tip = subprocess.run(["git", "commit-tree", tree, "-p", tip, "-F", "-"], cwd=top, input=body, env=env,
                             capture_output=True, text=True, check=True).stdout.strip()
    # seat_sync.reset_keep: a plain --keep would DELETE every file upstream stopped tracking (Transient/,
    # 2026-10-18); it keeps them on disk and otherwise behaves exactly like `git reset --keep`.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seat_sync
    try:
        seat_sync.reset_keep(seat_sync.Git(top), head, tip)
    except seat_sync.Refused as e:
        raise Refuse("origin/main changed a file you have uncommitted edits to, so the branch was not moved "
                     "(git reset --keep refused). Your commit is intact on HEAD. Publish or move aside that edit, "
                     "then re-run ./publish.\n%s%s" % (blockers(top, head, tip), e))
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
    env = dict(os.environ, GIT_INDEX_FILE=idx)
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
        for q in pairs:                                  # whole-file replace, never a partial write
            shutil.copyfile(os.path.join(scratch, q), os.path.join(top, q) + ".publish-tmp")
            os.replace(os.path.join(top, q) + ".publish-tmp", os.path.join(top, q))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    sha = commit(top, pairs, "Rebuild %s from committed source at landing\n\nBuilt by ./publish in a src-only "
                 "scratch clone of %s.\n" % (", ".join(os.path.basename(d) for d in dlls), head[:12]))
    if sha:
        print("committed rebuilt %s as %s" % (", ".join(dlls), sha[:12]))
    return sha


def guard_dlls(err):
    """DLL paths a DLL_SOURCE_STAMP_GUARD_1 refusal names, or an empty set when it is not that refusal."""
    if GUARD_TAG not in err:
        return set()
    return {m.group(2) for m in re.finditer(r"^(?:remote: )?\s*(MISMATCH|STAMP_MISSING) (\S+\.dll)\s*$", err, re.M)}


def land(top):
    dest, track, label = target_ref(top)
    guard_retried = False
    for attempt in range(MAX_TRIES):
        rebuilt = rebase(top)
        if rebuilt:
            rebuild_dlls(top, rebuilt)
        head = out(top, "rev-parse", "HEAD")
        if label == BRANCH and is_ancestor(top, head, track):
            return head                                  # nothing local left to push
        if before_push:
            before_push(attempt)
        r = run(top, "push", "-q", REMOTE, "HEAD:" + dest, check=False)
        if not r.returncode:
            run(top, "fetch", "-q", REMOTE, check=False)
            return head
        err = (r.stderr or r.stdout).strip()
        # Ambiguity check before any retry: the remote may have taken it before we gave up.
        run(top, "fetch", "-q", REMOTE, check=False)
        if ref_exists(top, track) and is_ancestor(top, head, track):
            print("push reported failure but %s already contains %s — it landed" % (label, head[:12]))
            return head
        bad = guard_dlls(err)
        if bad:
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
    print("PUBLISHED %s%s" % (sha, "" if label == BRANCH else "  (on %s)" % label))
    return sha


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
