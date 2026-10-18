#!/usr/bin/env python3
"""Selftest for transient_pin.py: the Transient/.gitignore it writes ignores everything except itself,
*.decisions.json and the pins (a dir pin covers files deep inside), and untrack lists exactly the
tracked files the rules now ignore."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def ignored(repo, path):
    return subprocess.run(["git", "-C", repo, "check-ignore", "-q", "--no-index", "--", path]).returncode == 0


def main():
    with tempfile.TemporaryDirectory() as td:
        os.environ["TRANSIENT_PIN_ROOT"] = td
        subprocess.run(["git", "init", "-q", "-b", "main", td], check=True)
        files = ["Transient/sheet.html", "Transient/sheet.decisions.json", "Transient/keep/deep/a.png",
                 "Transient/keep/b.json", "Transient/one [x].md", "Transient/other/c.txt"]
        for f in files:
            p = Path(td, f)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x\n")
        subprocess.run(["git", "-C", td, "add", "--", *files], check=True)
        import transient_pin as T
        with contextlib.redirect_stdout(io.StringIO()):
            T.main(["add", "Transient/keep", "one [x].md"])
            T.main(["add", "Transient/keep"])                       # idempotent
        pins = T.read_gi()[1]
        check(pins == ["!/keep/**", "!/one \\[x\\].md"], "pins written once, dir as /**, glob chars escaped: %r" % pins)
        check(ignored(td, "Transient/sheet.html") and ignored(td, "Transient/other/c.txt"), "unpinned files are ignored")
        check(not ignored(td, "Transient/sheet.decisions.json"), "a decisions file is never ignored")
        check(not ignored(td, "Transient/keep/deep/a.png") and not ignored(td, "Transient/keep/b.json"),
              "a dir pin keeps files at any depth")
        check(not ignored(td, "Transient/one [x].md"), "a file pin with glob characters works")
        check(not ignored(td, "Transient/.gitignore"), "the pin file itself is tracked")
        ti = T.tracked_ignored()
        check(sorted(ti) == ["Transient/other/c.txt", "Transient/sheet.html"], "untrack lists exactly the ignored tracked files: %r" % ti)
        with contextlib.redirect_stdout(io.StringIO()):
            T.main(["rm", "Transient/keep"])
        check(ignored(td, "Transient/keep/b.json"), "unpinning makes the dir ignored again")
    print("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
