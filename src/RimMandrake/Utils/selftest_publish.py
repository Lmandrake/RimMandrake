#!/usr/bin/env python3
"""Selftest for publish.py against a throwaway bare repo + clones on ext4 (never /tmp).

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
SHARD = "infrastructure/state/ledger/events/FOUNDRY.jsonl"
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


def read(repo, path):
    with open(os.path.join(repo, path)) as f:
        return f.read()


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
    write(a, SHARD, '{"id":"s1"}\n{"id":"s2"}\n')
    sh(a, "add", "f.txt", "g.txt", SHARD)
    sh(a, "commit", "-q", "-m", "seed")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(d, "clone", "-q", bare, b)
    return d, a, b


def peer_push(b, path, text, msg="peer"):
    sh(b, "pull", "-q", "--ff-only")
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


def t_publish_paths_leaves_everything_else(a, b):
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    write(a, "g.txt", "dirty, not mine to publish\n")
    write(a, "junk.txt", "untracked\n")
    head = sh(a, "rev-parse", "HEAD")
    sha, log = quiet(P.publish_paths, a, ["f.txt"], "mine\n")
    assert "PUBLISHED %s" % sha in log, log
    assert sha == sh(a, "rev-parse", "origin/main") and sha != head   # close with THIS, not HEAD
    assert "LINE 3" in show(a, "f.txt") and show(a, "g.txt") == "g\n"
    assert sh(a, "rev-parse", "HEAD") == head and read(a, "junk.txt") == "untracked\n"
    assert sh(a, "diff", "--cached", "--name-only") == ""            # shared index untouched


def t_second_publish_before_catchup(a, b):
    write(a, "new.sh", "#!/bin/sh\necho 1\n")
    quiet(P.publish_paths, a, ["new.sh"], "one\n")
    write(a, "new.sh", "#!/bin/sh\necho 2\n")
    quiet(P.publish_paths, a, ["new.sh"], "two\n")                # must not conflict with itself
    assert show(a, "new.sh").endswith("echo 2\n")
    assert sh(a, "ls-tree", "origin/main", "new.sh").startswith("100755")


def t_push_race_rebuilds_on_new_tip(a, b):
    write(a, "f.txt", LINES.replace("line 9", "LINE 9"))
    seen = {}
    def race(attempt):
        if attempt == 0:
            seen["peer"] = peer_push(b, "g.txt", "peer g\n")
    P.before_push = race
    try:
        sha, log = quiet(P.publish_paths, a, ["f.txt"], "mine\n")
    finally:
        P.before_push = None
    assert "origin moved" in log, log
    assert sh(a, "rev-parse", sha + "^") == seen["peer"]
    assert "LINE 9" in show(a, "f.txt") and show(a, "g.txt") == "peer g\n"


def t_ledger_shard_union(a, b):
    peer_push(b, SHARD, '{"id":"s1"}\n{"id":"s2"}\n{"id":"b1"}\n')
    write(a, SHARD, '{"id":"s1"}\n{"id":"s2"}\n{"id":"a1"}\n{"id":"a2"}\n')
    quiet(P.publish_paths, a, [SHARD], "ledger\n")
    assert show(a, SHARD) == '{"id":"s1"}\n{"id":"s2"}\n{"id":"b1"}\n{"id":"a1"}\n{"id":"a2"}\n'


def t_three_way_merge_and_conflict(a, b):
    peer_push(b, "f.txt", LINES.replace("line 1\n", "LINE 1\n"))
    write(a, "f.txt", LINES.replace("line 9", "LINE 9"))
    quiet(P.publish_paths, a, ["f.txt"], "merge\n")
    got = show(a, "f.txt")
    assert "LINE 1\n" in got and "LINE 9" in got, got
    before = sh(a, "rev-parse", "origin/main")
    peer_push(b, "g.txt", "peer says x\n")
    write(a, "g.txt", "i say y\n")
    why = refused(P.publish_paths, a, ["g.txt"], "clash\n")
    assert why and "g.txt" in why, why
    sh(a, "fetch", "-q")
    assert sh(a, "rev-parse", "origin/main^") == before            # only the peer's push landed


def t_delete_publishes(a, b):
    os.remove(os.path.join(a, "g.txt"))
    quiet(P.publish_paths, a, ["g.txt"], "rm\n")
    sh(a, "fetch", "-q")
    assert "g.txt" not in sh(a, "ls-tree", "--name-only", "origin/main")


def t_interleaved_cherry_picks_then_sync(a, b):
    for n in ("x", "y", "z"):                                        # three local commits
        write(a, n + ".txt", n + "\n")
        sh(a, "add", n + ".txt")
        sh(a, "commit", "-q", "-m", n, "--", n + ".txt")
    sh(b, "pull", "-q", "--ff-only")                                 # upstream re-lands x, z
    for n in ("x", "z"):
        write(b, n + ".txt", n + "\n")
        sh(b, "add", n + ".txt")
        sh(b, "commit", "-q", "-m", n + " (cherry-picked)", "--", n + ".txt")
    sh(b, "push", "-q", "origin", "HEAD:main")
    up = P.fetch(a)
    left = P.local_only(a, up)
    assert [sh(a, "log", "-1", "--format=%s", c) for c in left] == ["y"], left
    for c in left:
        quiet(P.publish_commit, a, c)
    quiet(P.catchup, a)
    assert sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert show(a, "y.txt") == "y\n" and sh(a, "status", "--porcelain") == ""


def t_catchup_untracked_collision(a, b):
    peer_push(b, "new.txt", "upstream\n")
    write(a, "new.txt", "mine, untracked\n")
    head = sh(a, "rev-parse", "HEAD")
    why = refused(P.catchup, a)
    assert why and "new.txt" in why and "untracked" in why, why
    assert sh(a, "rev-parse", "HEAD") == head and read(a, "new.txt") == "mine, untracked\n"
    write(a, "new.txt", "upstream\n")                                # identical -> fine
    quiet(P.catchup, a)
    assert sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")


def t_catchup_keeps_edits_and_untracked(a, b):
    write(a, "f.txt", LINES.replace("line 2", "LINE 2 (mine, uncommitted)"))
    write(a, "scratch/keep.bin", "untracked\n")
    peer_push(b, "f.txt", LINES.replace("line 9", "LINE 9 (upstream)"))
    peer_push(b, "g.txt", "g2\n")
    quiet(P.catchup, a)
    assert sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    f = read(a, "f.txt")
    assert "LINE 2 (mine" in f and "LINE 9 (upstream)" in f, f
    assert read(a, "g.txt") == "g2\n" and read(a, "scratch/keep.bin") == "untracked\n"
    assert sh(a, "diff", "--name-only") == "f.txt"                   # only my edit is dirty
    write(a, "f.txt", LINES.replace("line 9", "MINE 9"))             # overlap -> refuse
    peer_push(b, "f.txt", LINES.replace("line 9", "THEIRS 9"))
    head = sh(a, "rev-parse", "HEAD")
    why = refused(P.catchup, a)
    assert why and "f.txt" in why and sh(a, "rev-parse", "HEAD") == head, why
    assert "MINE 9" in read(a, "f.txt")


def t_janitor_removes_only_clean_published(a, b):
    d = os.path.dirname(a)
    clean, dirty = os.path.join(d, "wt-clean"), os.path.join(d, "wt-dirty")
    sh(a, "fetch", "-q")
    sh(a, "worktree", "add", "-q", "--detach", clean, "origin/main")
    sh(a, "worktree", "add", "-q", "--detach", dirty, "origin/main")
    write(dirty, "wip.txt", "wip\n")
    _, log = quiet(P.janitor, a, True)
    assert not os.path.exists(clean) and os.path.exists(dirty), log
    assert "uncommitted" in log, log


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
