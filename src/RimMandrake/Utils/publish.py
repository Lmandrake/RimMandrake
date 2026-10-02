#!/usr/bin/env python3
"""Commit named paths and land them with plain git — the thin wrapper agents already know.

    ./publish -m "subject" path/one path/two     commit those paths, rebase, push, print PUBLISHED <sha>
    ./publish -F msg.txt path/one                message from a file ('-' = stdin)
    ./publish                                    push local commits already made (no new commit)

It is exactly: `git add --all -- <paths>` + `git commit -- <paths>` (pathspec on the commit, so
nothing else staged rides along) + `git pull --rebase --autostash origin main` + push, retried up
to 8 times when origin moved under it, never forced. It pushes a seat clone
(/home/mandrake/rm/<seat>) to HEAD:main.

A push that fails for any reason other than a clean non-fast-forward is AMBIGUOUS (the remote may
have accepted it before the client gave up): it fetches and checks `merge-base --is-ancestor HEAD
<target>` before retrying, and an ancestor means it landed. A rebase that stops on a real conflict
is aborted (your commit stays intact locally) and the conflicted paths are named.

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
    r = run(top, "pull", "-q", "--rebase", "--autostash", REMOTE, BRANCH, check=False)
    if not r.returncode:
        return
    conflicted = out(top, "diff", "--name-only", "--diff-filter=U").split()
    gd = out(top, "rev-parse", "--absolute-git-dir")
    if any(os.path.isdir(os.path.join(gd, d)) for d in ("rebase-merge", "rebase-apply")):
        run(top, "rebase", "--abort", check=False)
    raise Refuse("`git pull --rebase` stopped%s. Rebase aborted; your commit is intact on HEAD. "
                 "This clone has one owner, so resolve it by hand (git pull --rebase origin main), "
                 "then re-run ./publish.\n%s" % (
                     (" on a conflict in: " + ", ".join(conflicted)) if conflicted else "",
                     "\n".join(l for l in (r.stderr or r.stdout).strip().splitlines()
                               if not l.startswith("hint:"))))


def land(top):
    dest, track, label = target_ref(top)
    for attempt in range(MAX_TRIES):
        rebase(top)
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
