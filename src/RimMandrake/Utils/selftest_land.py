#!/usr/bin/env python3
"""Selftest for land.sh: LAND_REPO defaults to the cwd's clone, and a landing realigns the clone (seat_sync)."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LAND = Path(__file__).resolve().parent / "land.sh"
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def land(cwd, *a, env=None):
    e = dict(os.environ)
    e.pop("LAND_REPO", None)
    e.update(env or {})
    return subprocess.run(["sh", str(LAND), *a], cwd=cwd, capture_output=True, text=True, env=e)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        os.environ.update({"HOME": td, "TMPDIR": td, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"})
        o, seat, peer = f"{td}/o.git", f"{td}/seat", f"{td}/peer"
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, seat)
        Path(seat, "a.txt").write_text("a1\n")
        git(seat, "add", "--", "a.txt"); git(seat, "commit", "-q", "-m", "init"); git(seat, "push", "-q", "origin", "HEAD:main")
        git(td, "clone", "-q", o, peer)

        r = land(td, "-m", "x", "a.txt")
        check(r.returncode == 2 and "LAND_REPO is unset" in r.stderr, "outside a clone with no LAND_REPO: refused")

        # sha mode while upstream moved on: lands, then the clone realigns onto the new origin/main
        Path(peer, "p.txt").write_text("p\n")
        git(peer, "add", "--", "p.txt"); git(peer, "commit", "-q", "-m", "peer"); git(peer, "push", "-q", "origin", "HEAD:main")
        Path(seat, "b.txt").write_text("b\n")
        git(seat, "add", "--", "b.txt"); git(seat, "commit", "-q", "-m", "b", "--", "b.txt")
        Path(seat, "dirty.txt").write_text("unrelated\n")
        r = land(seat, git(seat, "rev-parse", "HEAD"), "b.txt")
        out = r.stdout.strip().splitlines()
        check(r.returncode == 0 and len(out) == 1 and out[0].startswith("PUBLISHED "), "sha mode: stdout is one PUBLISHED line")
        new = out[0].split()[1] if out else ""
        check(git(o, "rev-parse", "main") == new, "origin/main is the published sha")
        check(git(seat, "rev-parse", "HEAD") == new and "SYNCED" in r.stderr, "clone defaulted from cwd and realigned to it")
        check(Path(seat, "p.txt").is_file() and Path(seat, "dirty.txt").is_file(), "peer file arrived; unrelated untracked kept")

        # -m mode: the dirty path is published and the clone reads clean afterwards
        Path(seat, "a.txt").write_text("a2\n")
        r = land(seat, "-m", "a2", "a.txt")
        check(r.returncode == 0 and r.stdout.startswith("PUBLISHED"), "-m mode publishes")
        check(git(seat, "rev-parse", "HEAD") == git(o, "rev-parse", "main"), "-m mode: clone realigned")
        check("a.txt" not in git(seat, "status", "--porcelain"), "-m mode: landed path reads clean")

        # an unlanded local commit stays: PUBLISHED still printed, HEAD untouched, reason on stderr
        Path(seat, "c.txt").write_text("c\n")
        git(seat, "add", "--", "c.txt"); git(seat, "commit", "-q", "-m", "c not landed", "--", "c.txt")
        head = git(seat, "rev-parse", "HEAD")
        Path(seat, "a.txt").write_text("a3\n")
        r = land(seat, "-m", "a3", "a.txt")
        check(r.returncode == 0 and r.stdout.startswith("PUBLISHED"), "landing still succeeds with an unlanded local commit")
        check(git(seat, "rev-parse", "HEAD") == head and "NOT on origin/main" in r.stderr, "clone left as is, and says why")

        # losing a push race: a pre-push hook advances origin from the peer once; land.sh rebuilds and retries
        hook = Path(seat, ".git", "hooks", "pre-push")
        hook.write_text(f"#!/bin/sh\n[ -e {td}/raced ] && exit 0\ntouch {td}/raced\n"
                        f"cd {peer} && git pull -q --ff-only origin main && echo r > r.txt && git add r.txt && "
                        f"git commit -qm race && git push -q --no-verify origin HEAD:main\nexit 0\n")
        hook.chmod(0o755)
        Path(seat, "d.txt").write_text("d\n")
        r = land(seat, "-m", "d", "d.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 0 and "rebuilding on the new tip" in r.stderr, "a lost push race is retried on the new tip")
        check("r.txt" in git(o, "ls-tree", "--name-only", "main"), "the racing commit is kept under ours")
        hook.unlink()

        r = land(seat, "-m", "a3", "a.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "nothing to land" in r.stderr, "re-landing identical content is refused")
    print(f"{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
