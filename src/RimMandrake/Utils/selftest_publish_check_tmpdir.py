#!/usr/bin/env python3
"""selftest_publish_check_tmpdir.py — every check ./publish runs gets a TMPDIR of its own, removed after, pass, red or
timeout (RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH). Measured 2026-11-18: 2,236 of the scratch
cleaner's 3,836 waiting clones were tmpXXXXXXXX git repos under ~/.seat-tmp/BENCH, five per run of the tree check
selftest_alpha_biomes_census.py, which every publish ran in the publisher's own TMPDIR.

A fake tree holds checks that mkdtemp and `git init` and never clean up: one passes, one is red, one sleeps past the
limit. Proves: the publisher's TMPDIR is empty after each; the check saw a TMPDIR that was not the publisher's; a red
check still refuses. Pure: temp dirs and a local `git init`."""
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish as P                                         # noqa: E402

FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


LEAKER = """import os, subprocess, sys, tempfile, time
t = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", t], check=True)
open(os.path.join(os.environ.get("SEEN_DIR", "/nonexistent"), os.path.basename(sys.argv[0]) + ".tmpdir"), "w").write(
    tempfile.gettempdir())
mode = sys.argv[1]
if mode == "sleep":
    time.sleep(30)
sys.exit(1 if mode == "red" else 0)
"""

outer = tempfile.mkdtemp(prefix="selftest_publish_check_tmpdir_")
saved_tmp, saved_env = tempfile.tempdir, os.environ.get("TMPDIR")
try:
    top, pub_tmp, seen = (os.path.join(outer, n) for n in ("top", "pubtmp", "seen"))
    for d in (top, pub_tmp, seen):
        os.makedirs(d)
    for name in ("ok_check.py", "red_check.py", "slow_check.py"):
        Path(top, name).write_text(LEAKER)
    os.environ["TMPDIR"], os.environ["SEEN_DIR"] = pub_tmp, seen
    tempfile.tempdir = pub_tmp

    P._run_tree_checks(top, {"timeout_s": 60, "checks": [{"test": "ok_check.py", "args": ["ok"]}]})
    ok(os.listdir(pub_tmp) == [], "a passing check leaves the publisher's TMPDIR empty (%s)" % os.listdir(pub_tmp))
    got = Path(seen, "ok_check.py.tmpdir").read_text() if Path(seen, "ok_check.py.tmpdir").exists() else ""
    ok(got and os.path.realpath(got) != os.path.realpath(pub_tmp), "the check ran in a TMPDIR of its own (%r)" % got)

    refused = False
    try:
        P._run_tree_checks(top, {"timeout_s": 60, "checks": [{"test": "red_check.py", "args": ["red"]}]})
    except P.Refuse:
        refused = True
    ok(refused, "a red check still refuses")
    ok(os.listdir(pub_tmp) == [], "a red check leaves the publisher's TMPDIR empty (%s)" % os.listdir(pub_tmp))

    P._run_tree_checks(top, {"timeout_s": 2, "checks": [{"test": "slow_check.py", "args": ["sleep"]}]})
    ok(os.listdir(pub_tmp) == [], "a timed-out check leaves the publisher's TMPDIR empty (%s)" % os.listdir(pub_tmp))
finally:
    tempfile.tempdir = saved_tmp
    if saved_env is None:
        os.environ.pop("TMPDIR", None)
    else:
        os.environ["TMPDIR"] = saved_env
    os.environ.pop("SEEN_DIR", None)
    shutil.rmtree(outer, ignore_errors=True)

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
