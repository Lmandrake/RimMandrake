#!/usr/bin/env python3
"""modpack_lint_harness.run() strands no lintplant_ temp dir when the mod copy fails (DIRTY_CODE_REVIEW_STANDING_LOOP_1
wave 9: the copytree and the real-mod lint ran before the try/finally that removes the dir). Offline, private TMPDIR."""
import atexit
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_priv = tempfile.mkdtemp(prefix="st_modpack_lint_harness_")
atexit.register(shutil.rmtree, _priv, True)
tempfile.tempdir = os.environ["TMPDIR"] = _priv

import modpack_lint_harness as H  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else " | %s" % (detail,)))
    if not cond:
        FAILS.append(name)


check("sanity: private temp dir starts empty", os.listdir(_priv) == [], os.listdir(_priv))
try:
    H.run("NoSuchMod_selftest_xyz", "no_such_lint.py", [])
    check("a missing mod dir raises", False, "run returned")
except OSError:
    check("a missing mod dir raises", True)
check("a failed copy strands no lintplant_ dir", os.listdir(_priv) == [], os.listdir(_priv))

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
