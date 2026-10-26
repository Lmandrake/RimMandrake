#!/usr/bin/env python3
"""selftest_conversations_land.py — pins what conversations_land.pending() offers to land (throwaway repos only).

  1. a new record and a changed record are pending; an unrelated dirty file is not;
  2. a record whose bytes ALREADY sit on origin/main is not pending, even while this clone's main is behind.
     Before 2026-10-26 pending() compared with HEAD only: a seat whose ./sync refused after land.sh (any
     unpublished local commit) kept re-offering landed records, land.sh died "nothing to land", and every
     handoff --check read NOT READY with a fix (`--apply`) that could never succeed.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conversations_land as CL  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def write(repo, name, text):
    p = Path(repo) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def main() -> int:
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}
    os.environ.update(env)
    with tempfile.TemporaryDirectory() as td:
        o, seat, peer = f"{td}/o.git", f"{td}/seat", f"{td}/peer"
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, seat)
        write(seat, "conversations/old.md", "v1\n")
        write(seat, "README", "r\n")
        git(seat, "add", "--", "conversations/old.md", "README")
        git(seat, "commit", "-q", "-m", "init")
        git(seat, "push", "-q", "origin", "HEAD:main")
        git(td, "clone", "-q", o, peer)

        write(seat, "conversations/old.md", "v1\nv2\n")
        write(seat, "conversations/new.md", "n\n")
        write(seat, "README", "dirty\n")
        got = CL.pending(seat)
        check(got == ["conversations/new.md", "conversations/old.md"], "new + changed records pending, README not (%s)" % got)

        # the records land upstream with these exact bytes (as land.sh -m does), but this clone's main stays behind
        write(peer, "conversations/old.md", "v1\nv2\n")
        write(peer, "conversations/new.md", "n\n")
        git(peer, "add", "--", "conversations")
        git(peer, "commit", "-q", "-m", "landed")
        git(peer, "push", "-q", "origin", "HEAD:main")
        git(seat, "fetch", "-q", "origin")
        got = CL.pending(seat)
        check(got == [], "records already on origin/main with the same bytes are not pending (%s)" % got)

        write(seat, "conversations/new.md", "n\nmore\n")
        got = CL.pending(seat)
        check(got == ["conversations/new.md"], "a record that grew again after landing is pending (%s)" % got)
    print("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
