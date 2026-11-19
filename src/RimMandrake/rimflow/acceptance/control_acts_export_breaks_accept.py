#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_EXPORT_CONTROL_ACTS_BELT_SPLIT_FROM_SLICE_FOUR: each promise on
`design/specs/2026-11-19-control-acts-export/boundary.md`, broken on purpose, turns its named test red.

One deliberately broken stand-in of `control_acts_export.py` per promise, run against that promise's named test in
`selftest_control_acts_export.py`, in a private copy of src/RimMandrake/{rimflow,Utils,contracts} (temp dir): the real
file is never edited. The unbroken copy must first pass every named test (else a test that always fails would read as
a catch).

  exit 0  PASS: every break rejected by its named test
  exit 1  FAIL: a break slipped past (its named test passed), each named
  exit 3  COULD NOT LOOK: the page and the breaks differ, a break no longer matches the file exactly once, or the
          unbroken copy fails a named test (cause named); not a verdict about the tests"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PAGE = os.path.join(REPO, "design", "specs", "2026-11-19-control-acts-export", "boundary.md")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import boundary_check as B  # noqa: E402

RUN_ONE = r"""
import shutil, sys
sys.path.insert(0, ".")
import selftest_control_acts_export as S
try:
    getattr(S, sys.argv[1])()
except Exception as e:      # noqa: BLE001  a test that raises is red, as in main()
    S.check(False, "%s raised %s: %s" % (sys.argv[1], type(e).__name__, e))
shutil.rmtree(S.TMP, ignore_errors=True)
if S.FAILS:
    print("RED %s" % " | ".join(S.FAILS[:3])); sys.exit(1)
print("GREEN"); sys.exit(0)
"""

BREAKS = {
    "export-holds-every-act": ("only the first act is exported", [
        ("            text = f.read()", "            text = f.readline()")]),
    "unchanged-store-makes-no-commit": ("an equal file is pushed again", [
        ("        if old == text:", "        if False:")]),
    "touches-no-working-tree": ("the commit is built in the clone's own index", [
        ('        env = {"GIT_INDEX_FILE": idx}', "        env = {}")]),
    "never-loses-a-published-act": ("no check for lost lines", [
        ('        lost = _lost(old or "", text)', "        lost = None")]),
    "could-not-look-publishes-nothing": ("an unreadable store exports as an empty file", [
        ('            return BLIND, ["COULD NOT LOOK: the control store %s: %s (nothing pushed)" % (store or C.db_path(), e)]',
         '            n = 0\n            open(out, "w").close()')]),
    "reading-only-on-success": ("a refused run writes the reading", [
        ("        if lost:\n", '        if lost:\n            _write_reading(reading, "refused", n, top, None, now)\n')]),
    "push-race-rebuilds": ("a refused push is a failure at once", [
        ("        if not any(w in said for w in REJECT_WORDS):", "        if True:")]),
}


def run_test(rimflow, test):
    """-> ("GREEN"|"RED"|"ERROR", line)."""
    try:
        r = subprocess.run([sys.executable, "-c", RUN_ONE, test], cwd=rimflow, capture_output=True, text=True,
                           timeout=300)
    except subprocess.TimeoutExpired:
        return "ERROR", "timed out after 300 s"
    out = (r.stdout or "").strip().splitlines()
    word = {0: "GREEN", 1: "RED"}.get(r.returncode, "ERROR")
    return word, (out[-1] if out else (r.stderr or "").strip()[-200:])[:240]


def main():
    try:
        names = B.promises(PAGE)
    except Exception as e:      # noqa: BLE001
        print("COULD NOT LOOK control_acts_export_breaks: the page cannot be read: %s" % e)
        return 3
    if sorted(names) != sorted(BREAKS):
        print("COULD NOT LOOK control_acts_export_breaks: the page's promises and the breaks differ: page only %s; "
              "breaks only %s" % (sorted(set(names) - set(BREAKS)), sorted(set(BREAKS) - set(names))))
        return 3
    tmp = tempfile.mkdtemp(prefix="acts_export_breaks_")
    try:
        for d in ("rimflow", "Utils", "contracts"):
            shutil.copytree(os.path.join(REPO, "src", "RimMandrake", d), os.path.join(tmp, "src", "RimMandrake", d),
                            symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
        rimflow = os.path.join(tmp, "src", "RimMandrake", "rimflow")
        target = os.path.join(rimflow, "control_acts_export.py")
        with open(target, encoding="utf-8") as f:
            orig = f.read()
        blind = []
        for n in names:
            word, line = run_test(rimflow, B.test_name(n))
            if word != "GREEN":
                blind.append("%s: unbroken, %s is %s (%s)" % (n, B.test_name(n), word, line))
            if any(orig.count(old) != 1 for old, _new in BREAKS[n][1]):
                blind.append("%s: its break no longer matches control_acts_export.py exactly once" % n)
        if blind:
            print("COULD NOT LOOK control_acts_export_breaks: %s" % "; ".join(blind))
            return 3
        slipped = []
        for n in names:
            what, edits = BREAKS[n]
            src = orig
            for old, new in edits:
                src = src.replace(old, new)
            with open(target, "w", encoding="utf-8") as f:
                f.write(src)
            try:
                word, line = run_test(rimflow, B.test_name(n))
            finally:
                with open(target, "w", encoding="utf-8") as f:
                    f.write(orig)
            if word == "ERROR":
                print("COULD NOT LOOK control_acts_export_breaks: %s under the break of %s" % (line, n))
                return 3
            print("%-8s %s: %s (%s)%s" % ("REJECTED" if word == "RED" else "SLIPPED", n, what, B.test_name(n),
                                          "" if word == "RED" else ": the test passed"))
            if word == "GREEN":
                slipped.append(n)
        if slipped:
            print("FAIL control_acts_export_breaks: %d of %d breaks slipped past: %s" % (
                len(slipped), len(names), ", ".join(slipped)))
            return 1
        print("PASS control_acts_export_breaks: %d of %d breaks rejected by their named test" % (len(names), len(names)))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
