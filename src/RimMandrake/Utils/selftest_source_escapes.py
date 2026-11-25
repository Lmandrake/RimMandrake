#!/usr/bin/env python3
"""selftest_source_escapes.py - every tracked Python source compiles with no SyntaxWarning
(RIMMANDRAKE_REPAIR_FLOWWORKS_REPIN_REFUSAL_AND_ESCAPE_WARNING).

Why: an invalid escape in a docstring (`"\\wsl.localhost\\..."` reads `\\.`) prints
`<unknown>:2357: SyntaxWarning: "\\." is an invalid escape sequence` on stderr whenever a tool parses that file
(src/RimMandrake/FlowWorks/northstar/live_session.py). On 2026-11-25T09:33Z that text failed a run-end publish note,
and `./pipe why <Mod>` printed it three times. Python 3.12 warns; a later Python makes it an error.

The check compiles every file `git ls-files '*.py'` lists with SyntaxWarning raised as an error. Before it trusts a
clean result it shows that it can see: a planted bad escape must be caught, and a raw string and a doubled backslash
must pass. Exit 0 all clean, 1 a file warns (each named with its line), 2 could not look (git or the probe failed).
Watched red on the parent of its fix: live_session.py:2357 and selftest_retired_era_gone.py:27."""
import os
import subprocess
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def warns(src, name):
    """-> a list of "name:line: message" for each SyntaxWarning compiling `src` raises; [] when it compiles clean.
    A SyntaxError is reported too (a file that cannot compile is not clean)."""
    out = []
    with warnings.catch_warnings(record=True) as got:
        warnings.simplefilter("always", SyntaxWarning)
        try:
            compile(src, name, "exec", dont_inherit=True)
        except SyntaxError as e:
            out.append("%s:%s: SyntaxError: %s" % (name, e.lineno, e.msg))
    for w in got:
        if issubclass(w.category, SyntaxWarning):
            out.append("%s:%s: SyntaxWarning: %s" % (name, w.lineno, w.message))
    return out


def check_file(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError:          # a listed file absent from the working tree (deleted, not yet committed): nothing to read
        return []
    return warns(src, rel)


def probe():
    """The instrument can see: a planted bad escape is caught, two good spellings are not."""
    bad = warns('x = "C:\\Program Files\\."\n', "planted")
    good = warns('x = r"C:\\Program Files\\."\ny = "a\\\\.b"\n', "good")
    return bool(bad) and not good, (bad, good)


def main():
    ok, got = probe()
    if not ok:
        print("COULD NOT LOOK: the probe failed (planted bad escape caught: %s; good spellings flagged: %s)" % got)
        return 2
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "*.py"], capture_output=True, timeout=600)
    files = [f for f in r.stdout.decode("utf-8", "replace").split("\0") if f]
    if r.returncode != 0 or not files:
        print("COULD NOT LOOK: git ls-files listed %d file(s) (exit %s)" % (len(files), r.returncode))
        return 2
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as ex:
        found = [w for ws in ex.map(check_file, files, chunksize=64) for w in ws]
    for w in found:
        print("FAIL " + w)
    print("%d of %d Python source(s) warn" % (len(found), len(files)) if found else
          "ok   %d Python sources compile with no SyntaxWarning (probe: planted escape caught)" % len(files))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
