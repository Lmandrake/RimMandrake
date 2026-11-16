#!/usr/bin/env python3
"""selftest_publish_refusal_last.py — ./publish's REFUSED line is the LAST line when stdout and stderr share a pipe.

RIMMANDRAKE_FLUSH_PUBLISH_OUTPUT_SO_TAIL_SHOWS_REFUSAL (review of 657a2a262a, 2026-11-16): publish's progress lines
go to stdout, block-buffered under a pipe, and REFUSED goes to stderr at once; so `./publish ... 2>&1 | tail -3`, the
form agents are told to use, printed the progress lines last and hid the refusal (a pre-push orphan-prose refusal
looked like a silent success). Fixture: a commit-free publish of an unchanged path, which prints "no change ..." on
stdout and then refuses "nothing to publish".
"""
import os
import subprocess
import sys
import tempfile

PUBLISH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publish.py")


def git(cwd, *a):
    subprocess.run(["git", "-C", cwd] + list(a), check=True, capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        o, c = os.path.join(td, "o.git"), os.path.join(td, "c")
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, c)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c, "config", k, v)
        with open(os.path.join(c, "a.txt"), "w") as f:
            f.write("a\n")
        git(c, "add", "a.txt")
        git(c, "commit", "-q", "-m", "base")
        git(c, "push", "-q", "origin", "main")
        r = subprocess.run("python3 %s -m x a.txt 2>&1 | cat" % PUBLISH, shell=True, cwd=c, capture_output=True,
                           text=True, timeout=120)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    ok = bool(lines) and lines[-1].startswith("REFUSED") and any("no change" in ln for ln in lines[:-1])
    print(("PASS" if ok else "FAIL") + ": combined output, last line %r (of %d)" % (lines[-1] if lines else None,
                                                                                   len(lines)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
