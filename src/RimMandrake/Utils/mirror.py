#!/usr/bin/env python3
"""Keep D:\\Luke\\dev\\RimMandrake as a plain, writer-free export of origin/main.

    ./mirror sync                 fetch + check out origin/main into the mirror (waits for the lock)
    ./mirror sync --timer         same, but skip at once if another sync holds the lock (systemd)
    ./mirror status               what the mirror holds, and whether it is stale

Plan: design/RimMandrake/git_workflow_plan_2026-10-01.md §2.3. No index or lock lives on drvfs:
the git dir is a bare, fetch-only repo on ext4 (/home/mandrake/rm/mirror.git) and the tree is
written with

    git --git-dir=/home/mandrake/rm/mirror.git --work-tree=<target> checkout -f --detach origin/main

so only changed files are rewritten on D:, with the same core.autocrlf as the seat clones (so the
export carries identical bytes). The index lives on ext4, one per target
(mirror.git/index.<target-hash>), so a test target never poisons the real one.

Both the timer and the on-demand run take flock /home/mandrake/rm/mirror.lock. A failed run leaves
the previous tree plus a MIRROR_STALE marker in the target (cleared by the next good run);
MIRROR_HEAD records the sha the tree holds.

Safety: it REFUSES a target that still contains a `.git` — the live shared tree keeps its .git
until the drain renames it (§5), so this cannot be run against it by accident before then.
"""
import argparse
import datetime
import fcntl
import hashlib
import os
import subprocess
import sys

RM = "/home/mandrake/rm"
GIT_DIR = os.environ.get("MIRROR_GIT_DIR", os.path.join(RM, "mirror.git"))
LOCK = os.environ.get("MIRROR_LOCK", os.path.join(RM, "mirror.lock"))
TARGET = os.environ.get("MIRROR_TARGET", "/mnt/d/Luke/dev/RimMandrake")
ORIGIN = os.environ.get("MIRROR_ORIGIN", "git@github.com:Lmandrake/RimMandrake.git")
SEAT_CLONES = (os.path.join(RM, "foundry"), os.path.join(RM, "bench"))
REF = "refs/remotes/origin/main"
STALE, HEAD_FILE = "MIRROR_STALE", "MIRROR_HEAD"


class Fail(Exception):
    pass


def autocrlf():
    """The seat clones' core.autocrlf (unset there means false), so the export matches them."""
    for c in SEAT_CLONES:
        if os.path.isdir(c):
            r = subprocess.run(["git", "-C", c, "config", "--get", "core.autocrlf"],
                               capture_output=True, text=True)
            return r.stdout.strip() or "false"
    return "false"


def git(*args, target=None, check=True):
    env = dict(os.environ)
    cmd = ["git", "--git-dir=" + GIT_DIR, "-c", "core.autocrlf=" + autocrlf(),
           "-c", "gc.autoDetach=false"]   # a detached auto-gc is killed at unit exit, leaking tmp_pack_*
    if target:
        env["GIT_INDEX_FILE"] = index_for(target)
        cmd.append("--work-tree=" + target)
    r = subprocess.run(cmd + list(args), capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise Fail("git %s: %s" % (" ".join(args[:2]), (r.stderr or r.stdout).strip()))
    return r.stdout.strip()


def index_for(target):
    h = hashlib.sha1(os.path.realpath(target).encode()).hexdigest()[:12]
    return os.path.join(GIT_DIR, "index." + h)


def ensure_bare(seed=None):
    if not os.path.isdir(GIT_DIR):
        os.makedirs(os.path.dirname(GIT_DIR), exist_ok=True)
        subprocess.run(["git", "init", "-q", "--bare", GIT_DIR], check=True)
        git("remote", "add", "origin", ORIGIN)
        git("config", "remote.origin.fetch", "+refs/heads/main:" + REF)
        git("config", "gc.auto", "256")
        if seed:                                   # borrow objects from a local clone: no 3 GB download
            git("fetch", "-q", "--no-tags", seed, "+refs/remotes/origin/main:" + REF)
    elif git("config", "--get", "remote.origin.url", check=False) != ORIGIN:
        git("remote", "set-url", "origin", ORIGIN)
    # drvfs reports every file as 0755: without this every entry reads as a mode change, so the
    # index never comes clean and `checkout -f` rewrites the whole ~4 GB tree on every run.
    if git("config", "--get", "core.fileMode", check=False) != "false":
        git("config", "core.fileMode", "false")


def stamp(target, name, text):
    with open(os.path.join(target, name), "w", newline="\n") as f:
        f.write(text)


def sync(target, timer=False, seed=None):
    if os.path.lexists(os.path.join(target, ".git")):
        raise Fail("%s still has a .git — it is a working repo, not the mirror. The drain renames it "
                   "first (git_workflow_plan_2026-10-01.md §5); refusing." % target)
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    lock = open(LOCK, "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | (fcntl.LOCK_NB if timer else 0))
    except BlockingIOError:
        print("mirror: another sync holds %s — skipping" % LOCK)
        return 0
    try:
        os.makedirs(target, exist_ok=True)
        ensure_bare(seed)
        git("fetch", "-q", "--prune", "--no-tags", "origin")
        new = git("rev-parse", REF)
        try:
            old = open(os.path.join(target, HEAD_FILE)).read().split()[0]
        except (OSError, IndexError):
            old = None
        if old == new and not os.path.exists(os.path.join(target, STALE)) \
                and os.path.exists(index_for(target)):
            print("mirror: %s already at %s" % (target, new[:12]))
            return 0
        if not os.path.exists(index_for(target)) and any(
                n not in (HEAD_FILE, STALE) for n in os.listdir(target)):
            # Adopting an existing tree (the drain's first run): build the index from the target
            # commit and let git stat/hash what is already on disk, so checkout rewrites only the
            # files that differ instead of all ~4 GB.
            print("mirror: adopting existing tree at %s (first run; hashing what is there)" % target)
            git("read-tree", REF, target=target)
            git("update-index", "-q", "--refresh", target=target, check=False)
        git("checkout", "-q", "-f", "--detach", REF, target=target)
        stamp(target, HEAD_FILE, "%s %s\n" % (new, datetime.datetime.now().astimezone().isoformat(
            timespec="seconds")))
        try:
            os.remove(os.path.join(target, STALE))
        except FileNotFoundError:
            pass
        print("mirror: %s -> %s%s" % (target, new[:12], "" if not old else " (was %s)" % old[:12]))
        return 0
    except Exception as e:  # noqa: BLE001 — any failure leaves the old tree + a marker
        try:
            stamp(target, STALE, "%s\n%s\n" % (datetime.datetime.now().astimezone().isoformat(
                timespec="seconds"), e))
        except OSError:
            pass
        print("mirror: FAILED, %s left as it was and marked %s: %s" % (target, STALE, e),
              file=sys.stderr)
        return 1
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def status(target):
    head = os.path.join(target, HEAD_FILE)
    print("target : %s" % target)
    print("holds  : %s" % (open(head).read().strip() if os.path.exists(head) else "(never synced)"))
    if os.path.isdir(GIT_DIR):
        print("origin : %s" % (git("rev-parse", "--short=12", REF, check=False) or "(not fetched)"))
    stale = os.path.join(target, STALE)
    if os.path.exists(stale):
        print("STALE  : %s" % open(stale).read().strip().replace("\n", " — "))
        return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("sync", "status"))
    ap.add_argument("--timer", action="store_true", help="non-blocking lock: skip if a sync is running")
    ap.add_argument("--target", default=TARGET, help="tree to write (default %(default)s)")
    ap.add_argument("--seed", help="first run only: take objects from this local clone")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "status":
            return status(a.target)
        return sync(a.target, a.timer, a.seed)
    except Fail as e:
        print("mirror: REFUSED: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
