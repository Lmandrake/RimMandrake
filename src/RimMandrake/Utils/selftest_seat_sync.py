#!/usr/bin/env python3
"""Selftest for seat_sync.py: throwaway bare origin + seat clone + peer clone, every refusal and every sync path."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seat_sync as S  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sh(cwd, *a):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def git(cwd, *a):
    return sh(cwd, "git", *a)


def write(repo, name, text):
    p = Path(repo) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def peer_push(peer, files: dict, msg="peer"):
    git(peer, "pull", "-q", "--ff-only", "origin", "main")
    for k, v in files.items():
        write(peer, k, v)
    git(peer, "add", "--", *files)
    git(peer, "commit", "-q", "-m", msg, "--", *files)
    git(peer, "push", "-q", "origin", "HEAD:main")


def run(repo, *extra):
    from io import StringIO
    import contextlib
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        rc = S.main(["--repo", repo, *extra])
    return rc, buf.getvalue()


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        os.environ["HOME"] = td
        for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                     "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}.items():
            os.environ[k] = v
        o, seat, peer = f"{td}/o.git", f"{td}/bench", f"{td}/peer"
        sh(td, "git", "init", "-q", "--bare", "-b", "main", o)
        sh(td, "git", "clone", "-q", o, seat)
        write(seat, "a.txt", "a1\n"); write(seat, "b.txt", "b1\n")
        git(seat, "add", "--", "a.txt", "b.txt"); git(seat, "commit", "-q", "-m", "init"); git(seat, "push", "-q", "origin", "HEAD:main")
        sh(td, "git", "clone", "-q", o, peer)

        rc, out = run(seat)
        check(rc == 0 and "IN SYNC" in out, "level clone reports IN SYNC")

        # land.sh -m shape: the seat's dirty a.txt was published from elsewhere with the same bytes
        write(seat, "a.txt", "a2\n"); write(seat, "dirty_unrelated.txt", "x\n")
        write(seat, "b.txt", "b-mine\n")                       # unrelated dirty tracked file upstream does not touch
        peer_push(peer, {"a.txt": "a2\n"}, "land a2")
        rc, out = run(seat)
        check(rc == 0 and "SYNCED" in out, "-m landing: dirty path holding upstream bytes syncs")
        check(git(seat, "rev-parse", "HEAD") == git(seat, "rev-parse", "origin/main"), "HEAD now equals origin/main")
        check(Path(seat, "b.txt").read_text() == "b-mine\n", "an unrelated dirty tracked file is untouched")
        check(Path(seat, "dirty_unrelated.txt").exists(), "an unrelated untracked file is untouched")
        check("a.txt" not in git(seat, "status", "--porcelain"), "the landed path reads clean")

        # dirty path upstream changes with OTHER bytes -> refused, nothing moves
        write(seat, "a.txt", "a-mine\n")
        peer_push(peer, {"a.txt": "a3\n"}, "a3")
        before = git(seat, "rev-parse", "HEAD")
        rc, out = run(seat)
        check(rc == 1 and "REFUSED" in out and "a.txt" in out, "conflicting dirty path is refused and named")
        check(git(seat, "rev-parse", "HEAD") == before and Path(seat, "a.txt").read_text() == "a-mine\n",
              "a refusal changes nothing")
        write(seat, "a.txt", "a3\n")
        rc, out = run(seat)
        check(rc == 0, "same path syncs once it holds upstream bytes")

        # land.sh sha shape: a local commit replayed upstream (patch-equivalent duplicate)
        write(seat, "c.txt", "c1\n"); git(seat, "add", "--", "c.txt"); git(seat, "commit", "-q", "-m", "c1", "--", "c.txt")
        local = git(seat, "rev-parse", "HEAD")
        peer_push(peer, {"d.txt": "d\n"}, "unrelated upstream")
        git(peer, "fetch", "-q", seat, local); git(peer, "cherry-pick", local); git(peer, "push", "-q", "origin", "HEAD:main")
        rc, out = run(seat)
        check(rc == 0 and "patch-equivalent" in out and "backup branch" in out, "patch-equivalent local commit syncs with backup")
        check(git(seat, "rev-parse", "HEAD") == git(seat, "rev-parse", "origin/main"), "duplicate is gone from main")
        check(any(b.strip().startswith("backup/") for b in git(seat, "branch", "--list", "backup/*").splitlines()),
              "backup branch keeps the original")

        # a local commit NOT upstream -> refused
        write(seat, "e.txt", "e\n"); git(seat, "add", "--", "e.txt"); git(seat, "commit", "-q", "-m", "e only here", "--", "e.txt")
        peer_push(peer, {"f.txt": "f\n"}, "f")
        before = git(seat, "rev-parse", "HEAD")
        rc, out = run(seat)
        check(rc == 1 and "NOT on origin/main" in out, "unpublished local commit is refused")
        check(git(seat, "rev-parse", "HEAD") == before, "refusal leaves the local commit in place")
        git(peer, "fetch", "-q", seat, before); git(peer, "cherry-pick", before); git(peer, "push", "-q", "origin", "HEAD:main")
        run(seat)

        # untracked file where upstream adds one
        write(seat, "g.txt", "g\n")
        peer_push(peer, {"g.txt": "g\n"}, "g")
        rc, out = run(seat)
        check(rc == 0 and "moved" in out and Path(seat, "g.txt").read_text() == "g\n", "identical untracked copy is moved aside")
        write(seat, "h.txt", "mine\n")
        peer_push(peer, {"h.txt": "theirs\n"}, "h")
        rc, out = run(seat)
        check(rc == 1 and "h.txt" in out and Path(seat, "h.txt").read_text() == "mine\n", "different untracked file is refused")
        os.remove(Path(seat, "h.txt")); run(seat)

        # wrong branch / dry run
        git(seat, "checkout", "-q", "-b", "side")
        rc, out = run(seat)
        check(rc == 1 and "not main" in out, "a non-main branch is refused")
        git(seat, "checkout", "-q", "main")
        peer_push(peer, {"i.txt": "i\n"}, "i")
        before = git(seat, "rev-parse", "HEAD")
        rc, out = run(seat, "--dry-run")
        check(rc == 0 and "WOULD SYNC" in out and git(seat, "rev-parse", "HEAD") == before, "dry run changes nothing")
    print(f"{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
