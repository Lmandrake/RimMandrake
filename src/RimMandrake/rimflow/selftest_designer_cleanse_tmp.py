#!/usr/bin/env python3
"""selftest_designer_cleanse.py leaves nothing in its TMPDIR, on a pass and on a failed row (item
RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH). Measured 2026-11-18: one direct run left 1,659 dc_*
folders; 19,204 stood in /tmp and 113,232 in ~/.seat-tmp/BENCH, and the scratch cleaner spent its whole 30-minute budget
walking them. run_selftests.py gives each test a TMPDIR of its own, but a builder runs the file directly.
Pure: one fresh temp root per row, removed after."""
import contextlib
import importlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "selftest_designer_cleanse.py")
sys.path.insert(0, HERE)
FAILS = []


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def left(base):
    return sorted(os.listdir(base))


def test_subprocess_pass():
    base = tempfile.mkdtemp(prefix="dctmp_")
    try:
        p = subprocess.run([sys.executable, TARGET], env=dict(os.environ, TMPDIR=base),
                           capture_output=True, text=True, timeout=300)
        tail = (p.stdout.strip().splitlines() or [""])[-1]
        check(p.returncode == 0, "the designer cleanse selftest passes (rc %d, %s)" % (p.returncode, tail))
        rest = left(base)
        check(rest == [], "a passing run leaves its TMPDIR empty (%d left, e.g. %s)" % (len(rest), rest[:3]))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_inprocess_failed_row():
    base = tempfile.mkdtemp(prefix="dctmp_")
    saved_tmp, saved_env = tempfile.tempdir, dict(os.environ)
    tempfile.tempdir = base
    try:
        mod = importlib.import_module("selftest_designer_cleanse")
        real = mod.test_release

        def broken():
            real()
            tempfile.mkdtemp(prefix="dc_injected_")
            raise RuntimeError("injected")
        mod.test_release = broken
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = mod.main()
        check(rc == 1, "an injected crash fails the run (rc %r)" % rc)
        rest = left(base)
        check(rest == [], "a failed run leaves its TMPDIR empty too (%d left, e.g. %s)" % (len(rest), rest[:3]))
        check(tempfile.tempdir == base and os.environ.get("TMPDIR") == saved_env.get("TMPDIR"),
              "main() hands back the caller's tempdir and TMPDIR")
    finally:
        tempfile.tempdir = saved_tmp
        os.environ.clear()
        os.environ.update(saved_env)
        shutil.rmtree(base, ignore_errors=True)


def main():
    for t in (test_subprocess_pass, test_inprocess_failed_row):
        try:
            t()
        except Exception as e:      # a crash is a failed row, not a silent stop
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
