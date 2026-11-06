#!/usr/bin/env python3
"""selftest_relentless_revert_landing.py: RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN, the r7 graded review's two upheld claims.

(a) Patch equivalence named a landing that origin/main has since reverted: `unlanded` passed the commit and `find_landed`
    returned the reverted one, so `finish` let the fix leave its lease while main lacked it (Codex r7 part1 #1).
(b) `worker_changed` dropped a commit restore_commits carried back, because a cherry-pick keeps its old author time, so
    proof_gate could not see code the supervisor had returned to the clone (Codex r7 part4 #1).
Real git repos in a temp dir.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402

FAILS = []
ITEM = "REVERT_ITEM_X"


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(cwd, *a, at=None, who="t@t"):
    env = dict(os.environ)
    if at is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "@%d +0000" % at
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=" + who, "-c", "commit.gpgsign=false", *a],
                          cwd=cwd, check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env).stdout.strip()


def commit(repo, path, line, msg, at=None):
    with open(os.path.join(repo, path), "a") as f:
        f.write(line + "\n")
    git(repo, "add", path)
    git(repo, "commit", "-q", "-m", msg, at=at)
    return git(repo, "rev-parse", "HEAD")


def world(base):
    """-> (publisher, clone): both at one base; the clone holds a commit origin has not got under its hash."""
    origin, pub, clone = (os.path.join(base, x) for x in ("origin.git", "pub", "clone"))
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
    subprocess.run(["git", "clone", "-q", origin, pub], check=True, capture_output=True)
    git(pub, "checkout", "-q", "-b", "main")
    commit(pub, "other.txt", "base", "base", at=1000)
    git(pub, "push", "-q", "origin", "main")
    subprocess.run(["git", "clone", "-q", origin, clone], check=True, capture_output=True)
    return pub, clone


def land_twin(pub, clone):
    """the clone's commit, and the same patch on origin under another hash"""
    mine = commit(clone, "f.txt", "the fix", ITEM + ": the fix", at=2000)
    commit(pub, "other.txt", "origin moved", "origin moved", at=2100)
    twin = commit(pub, "f.txt", "the fix", ITEM + ": the fix", at=2000)
    return mine, twin


def push(pub, clone):
    git(pub, "push", "-q", "origin", "main")
    git(clone, "fetch", "-q", "origin")


def t_revert():
    base = tempfile.mkdtemp(prefix="rvl_")
    try:
        pub, clone = world(base)
        mine, twin = land_twin(pub, clone)
        push(pub, clone)
        key = R.landing_key(clone, mine)
        ok(R.unlanded(clone) == [], "control: a twin that stands is landed: %s" % R.unlanded(clone))
        ok(R.find_landed(clone, key, ITEM)[0] == twin, "control: find_landed names the standing twin")
        ok(R.reverted_on(clone, twin) is False, "control: reverted_on says no while it stands")
        git(pub, "revert", "--no-edit", twin)
        push(pub, clone)
        ok(R.reverted_on(clone, twin) is True, "a reverted twin reads reverted")
        ok(R.unlanded(clone) == [mine], "a commit whose only twin was reverted is unlanded: %s" % R.unlanded(clone))
        ok(R.unlanded_owed(clone) is not None, "so finish refuses it")
        ok(R.find_landed(clone, key, ITEM)[0] is None, "find_landed will not name the reverted commit: %s" % (R.find_landed(clone, key, ITEM),))
        commit(pub, "f.txt", "the fix", ITEM + ": the fix", at=2000)      # re-landed: the same patch, after the revert
        push(pub, clone)
        ok(R.reverted_on(clone, twin) is False, "a patch re-landed after its revert is back")
        ok(R.unlanded(clone) == [], "... and the clone's commit is landed again: %s" % R.unlanded(clone))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_worker_changed():
    base = tempfile.mkdtemp(prefix="rvl_")
    try:
        repo = os.path.join(base, "books")
        os.makedirs(repo)
        git(repo, "init", "-q", "-b", "main")
        held = commit(repo, "a.txt", "built", ITEM + ": the build", at=1000)
        since, run, end = 1500, 2000, 3000
        commit(repo, "mend.txt", "mend", ITEM + ": a mend between runs", at=1700)
        git(repo, "commit", "-q", "--allow-empty", "-m", "pad", at=1701)
        # what restore_commits leaves: old author time, the supervisor as committer, picked just before the run started
        with open(os.path.join(repo, "code.txt"), "a") as f:
            f.write("old code\n")
        git(repo, "add", "code.txt")
        env = dict(os.environ, GIT_AUTHOR_DATE="@900 +0000", GIT_COMMITTER_DATE="@1999 +0000")
        subprocess.run(["git", "-c", "user.name=relentless", "-c", "user.email=" + R.RESTORE_EMAIL, "commit", "-q",
                        "--author=t <t@t>", "-m", ITEM + ": carried back"], cwd=repo, check=True, env=env, capture_output=True)
        sha = commit(repo, "proof.txt", "proof", ITEM + ": proof", at=2500)
        store = R.Store(os.path.join(base, "store"))
        os.makedirs(store.item_dir(ITEM), exist_ok=True)
        store.attempt(ITEM, {"at": R.iso(run), "gen": 2, "start": "u"})
        store.attempt(ITEM, {"at": R.iso(end), "gen": 2, "end": "finish", "sha": sha})
        fx = types.SimpleNamespace(store=store, books=repo, r={})
        for n in ("git", "changed", "worker_changed"):
            setattr(fx, n, types.MethodType(getattr(R.Effects, n), fx))
        got = fx.worker_changed(held, sha, ITEM, since)
        ok("code.txt" in got, "a commit restore_commits carried back counts despite its old author time: %s" % got)
        ok("proof.txt" in got and "mend.txt" not in got, "the run's own commit counts, a mend between runs still does not: %s" % got)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    t_revert()
    t_worker_changed()
    print("FAILED: %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
