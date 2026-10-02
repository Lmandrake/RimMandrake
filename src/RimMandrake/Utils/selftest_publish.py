#!/usr/bin/env python3
"""Selftest for publish.py (the thin plain-git wrapper) against a throwaway bare repo + clones
on ext4 (never /tmp).

    python3 src/RimMandrake/Utils/selftest_publish.py
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publish as P  # noqa: E402

ROOT = os.path.expanduser("~/.cache/publish-selftest")
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}
os.environ.update(ENV)
LINES = "".join("line %d\n" % i for i in range(1, 11))


def sh(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def show(repo, path, ref="origin/main"):
    sh(repo, "fetch", "-q")
    return sh(repo, "show", "%s:%s" % (ref, path)) + "\n"


def world():
    os.makedirs(ROOT, exist_ok=True)
    d = tempfile.mkdtemp(dir=ROOT)
    bare, a, b = (os.path.join(d, n) for n in ("bare.git", "a", "b"))
    sh(d, "init", "-q", "--bare", "-b", "main", bare)
    sh(d, "clone", "-q", bare, a)
    write(a, "f.txt", LINES)
    write(a, "g.txt", "g\n")
    sh(a, "add", "f.txt", "g.txt")
    sh(a, "commit", "-q", "-m", "seed")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(d, "clone", "-q", bare, b)
    P.POOL_ROOT = os.path.join(d, "pool")
    return d, a, b


def peer_push(b, path, text, msg="peer"):
    sh(b, "pull", "-q", "--rebase")
    write(b, path, text)
    sh(b, "add", path)
    sh(b, "commit", "-q", "-m", msg, "--", path)
    sh(b, "push", "-q", "origin", "HEAD:main")
    return sh(b, "rev-parse", "HEAD")


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a)
    return r, buf.getvalue()


def refused(fn, *a):
    try:
        quiet(fn, *a)
    except P.Refuse as e:
        return str(e)
    return None


def t_commits_only_named_paths(a, b):
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    write(a, "g.txt", "dirty, not mine to publish\n")
    write(a, "junk.txt", "untracked\n")
    sh(a, "add", "g.txt")                                     # a staged peer file must not ride along
    sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    assert "PUBLISHED %s" % sha in log, log
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert "LINE 3" in show(a, "f.txt") and show(a, "g.txt") == "g\n"
    assert sh(a, "show", "--name-only", "--format=", "HEAD") == "f.txt"


def t_new_file_and_delete(a, b):
    write(a, "dir/new.sh", "#!/bin/sh\n")
    os.remove(os.path.join(a, "g.txt"))
    quiet(P.publish, a, ["dir/new.sh", "g.txt"], "add+rm")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert "dir/new.sh" in names and "g.txt" not in names, names


def t_rebases_onto_moved_origin(a, b):
    peer = peer_push(b, "g.txt", "peer g\n")
    write(a, "f.txt", LINES.replace("line 9", "LINE 9"))
    sha, _ = quiet(P.publish, a, ["f.txt"], "mine")
    assert sh(a, "rev-parse", sha + "^") == peer
    assert "LINE 9" in show(a, "f.txt") and show(a, "g.txt") == "peer g\n"


def t_push_race_retries(a, b):
    write(a, "f.txt", LINES.replace("line 5", "LINE 5"))
    seen = {}

    def race(attempt):
        if attempt == 0:
            seen["peer"] = peer_push(b, "g.txt", "raced\n")
    P.before_push = race
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    finally:
        P.before_push = None
    assert "origin moved" in log, log
    assert sh(a, "rev-parse", sha + "^") == seen["peer"]


def t_dirty_tree_survives_rebase(a, b):
    peer_push(b, "g.txt", "peer\n")
    write(a, "f.txt", LINES.replace("line 1\n", "LINE 1\n"))
    write(a, "h.txt", "untracked\n")
    sh(a, "add", "h.txt")
    sh(a, "commit", "-q", "-m", "h", "--", "h.txt")
    write(a, "h.txt", "uncommitted edit\n")                     # autostash must keep it
    quiet(P.publish, a, ["f.txt"], "mine")
    assert open(os.path.join(a, "h.txt")).read() == "uncommitted edit\n"
    assert show(a, "h.txt") == "untracked\n"


def t_conflict_aborts_rebase(a, b):
    peer_push(b, "g.txt", "peer says x\n")
    write(a, "g.txt", "i say y\n")
    why = refused(P.publish, a, ["g.txt"], "clash")
    assert why and "g.txt" in why, why
    assert not os.path.isdir(os.path.join(a, ".git", "rebase-merge"))
    assert sh(a, "log", "-1", "--format=%s") == "clash"         # commit intact locally


def t_ambiguous_push_detected_as_landed(a, b):
    write(a, "f.txt", LINES.replace("line 2", "LINE 2"))
    real = P.run

    def flaky(top, *args, check=True):
        if args[:1] == ("push",):
            real(top, *args, check=check)                       # remote accepts...
            return subprocess.CompletedProcess(args, 128, "", "fatal: the remote end hung up")
        return real(top, *args, check=check)
    P.run = flaky
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    finally:
        P.run = real
    assert "it landed" in log, log
    assert sha == sh(a, "rev-parse", "origin/main")


def t_nothing_to_publish(a, b):
    why = refused(P.publish, a, ["f.txt"], "noop")
    assert why and "nothing to publish" in why, why


def t_pushes_existing_local_commits(a, b):
    write(a, "x.txt", "x\n")
    sh(a, "add", "x.txt")
    sh(a, "commit", "-q", "-m", "x", "--", "x.txt")
    sha, _ = quiet(P.publish, a, [], None)
    assert sha == sh(a, "rev-parse", "origin/main")


def t_pool_slot_pushes_submit_ref(a, b):
    slot = os.path.join(P.POOL_ROOT, "bench", "slot1")
    os.makedirs(os.path.dirname(slot))
    sh(a, "worktree", "add", "-q", "-b", "agent/fixit", slot, "origin/main")
    main_before = sh(a, "rev-parse", "origin/main")
    write(slot, "f.txt", LINES.replace("line 4", "LINE 4"))
    sha, log = quiet(P.publish, slot, ["f.txt"], "slot work")
    assert "submit/bench/fixit" in log, log
    sh(a, "fetch", "-q")
    assert sh(a, "rev-parse", "origin/main") == main_before          # main untouched
    assert sh(a, "rev-parse", "origin/submit/bench/fixit") == sha


def t_refuses_on_mnt(a, b):
    real = os.path.realpath
    P.os.path.realpath = lambda p: "/mnt/d/Luke/dev/RimMandrake" if p == a else real(p)
    try:
        why = refused(P.publish, a, ["f.txt"], "x")
    finally:
        P.os.path.realpath = real
    assert why and "/home/mandrake/rm/<seat>" in why, why


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_")]


def main():
    ok = 0
    for t in TESTS:
        d, a, b = world()
        try:
            t(a, b)
            ok += 1
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print("%d/%d passed" % (ok, len(TESTS)))
    return 0 if ok == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
