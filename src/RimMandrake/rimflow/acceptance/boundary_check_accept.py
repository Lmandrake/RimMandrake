#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_BUILD_BOUNDARY_CHECK_PROMISE_WITHOUT_TEST_REFUSED.

src/RimMandrake/Utils/boundary_check.py <boundary.md> --tests <selftest.py> reads the page's PROMISES, finds for each
promise `some-name` a test function `t_some_name`, and prints `promises covered N of M`. Exit 0 only when N == M; a
promise with no test exits 1 and is named; a page it cannot read exits 3 (could not look is not zero promises).
Exit 0 here = every check passes (expected: 4)."""
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
TOOL = os.path.join(REPO, "src", "RimMandrake", "Utils", "boundary_check.py")
PAGE = os.path.join(REPO, "design", "specs", "2026-11-18-pipeline-control-surface", "boundary.md")
TESTS = os.path.join(REPO, "src", "RimMandrake", "rimflow", "selftest_control.py")
FAILS = []


def check(name, ok, got=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else got))
    FAILS.append(name) if not ok else None


def run(page, tests):
    if not os.path.isfile(TOOL):
        return 127, "no %s" % TOOL
    r = subprocess.run([sys.executable, TOOL, page, "--tests", tests], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


T = tempfile.mkdtemp(prefix="boundary_check_")
page, tests = os.path.join(T, "boundary.md"), os.path.join(T, "selftest_x.py")
with open(page, "w") as f:
    f.write("# BOUNDARY: x\n\n## PROMISES\n\n- **off-blocks-starts.** a.\n- **kill-verified-dead.** b.\n\n## LIFE CYCLES\n\n"
            "- **run:** not a promise.\n")
with open(tests, "w") as f:
    f.write("def t_off_blocks_starts():\n    pass\n\n\ndef main():\n    t_off_blocks_starts()\n")
rc, out = run(page, tests)
check("a promise with no test of its name: exit 1, named", rc == 1 and "kill-verified-dead" in out
      and "promises covered 1 of 2" in out, (rc, out[-300:]))
with open(tests, "w") as f:      # boundary_check counts a test only if main() runs it (60274d0df2)
    f.write("def t_off_blocks_starts():\n    pass\n\n\ndef t_kill_verified_dead():\n    pass\n\n\n"
            "def main():\n    t_off_blocks_starts()\n    t_kill_verified_dead()\n")
rc, out = run(page, tests)
check("every promise tested: exit 0, `promises covered 2 of 2`", rc == 0 and "promises covered 2 of 2" in out, (rc, out[-300:]))
rc, out = run(os.path.join(T, "absent.md"), tests)
check("a page that cannot be read: exit 3, never `0 of 0`", rc == 3 and "covered 0 of 0" not in out, (rc, out[-300:]))
rc, out = run(PAGE, TESTS)
check("the control store's own page: every promise has its test", rc == 0 and "promises covered" in out, (rc, out[-300:]))
print("FAILED %d" % len(FAILS) if FAILS else "PASS boundary_check_accept (4 checks)")
sys.exit(1 if FAILS else 0)
