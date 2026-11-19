#!/usr/bin/env python3
"""selftest_boundary_check.py — boundary_check.py keeps its four answers apart, and refuses a broken page at ./publish.

RIMMANDRAKE_BUILD_BOUNDARY_CHECK_PROMISE_WITHOUT_TEST_REFUSED (owner by card 2026-11-18, `standing_rulings.md` §A
boundary page before pipeline code): each promise on a boundary page has a test of the same name. The four answers:
every promise tested (exit 0, `promises covered N of M`); a promise with no test (exit 1, named); a page with no
promises (exit 4, its own outcome); a page or tests file that cannot be read or parsed (exit 3, UNREADABLE with the
cause, never `0 of 0`). Last, every page the tool checks by default (what ./publish runs) passes today.
"""
import os
import subprocess
import sys
import tempfile

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boundary_check.py")
FAILS = []


def check(ok, what, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok else "  got %r" % (got,)))
    FAILS.append(what) if not ok else None


def run(*a):
    r = subprocess.run([sys.executable, TOOL] + list(a), capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def main():
    td = tempfile.mkdtemp(prefix="selftest_boundary_check_")
    page, tests = os.path.join(td, "boundary.md"), os.path.join(td, "selftest_x.py")

    def write(p, s):
        with open(p, "w", encoding="utf-8") as f:
            f.write(s)
    write(page, "# BOUNDARY: x\n\n## DOES NOT SURVIVE (not promised)\n\n- **two-failures.** not a promise.\n\n"
                "## PROMISES (each one is owed a test)\n\n- **off-blocks-starts.** a.\n- **queue-is-the-store's.** b.\n"
                "\n## SURVIVES\n\n- **a-lost-lock.** c.\n\n## LIFE CYCLES\n\n- **run:** not a promise.\n")
    write(tests, "def t_off_blocks_starts():\n    pass\n")
    rc, out = run(page, "--tests", tests)
    check(rc == 1 and "promises covered 1 of 3" in out and "t_queue_is_the_stores" in out and "t_a_lost_lock" in out
          and "two_failures" not in out, "untested promise and SURVIVES entry: exit 1, each named; DOES NOT SURVIVE "
          "and LIFE CYCLES are not promises", (rc, out))
    write(tests, "def t_off_blocks_starts():\n    pass\n\n\ndef t_queue_is_the_stores():\n    pass\n\n\n"
                 "def t_lost():\n    pass\n\n\nt_a_lost_lock = t_lost\n")
    rc, out = run(page, "--tests", tests)
    check(rc == 0 and "promises covered 3 of 3" in out, "every promise tested (a def, or a name bound to one): exit 0",
          (rc, out))
    for what, p, t in (("a page that does not exist", os.path.join(td, "absent.md"), tests),
                       ("a tests file that does not exist", page, os.path.join(td, "absent.py"))):
        rc, out = run(p, "--tests", t)
        check(rc == 3 and "UNREADABLE" in out and "covered" not in out, "%s: exit 3, UNREADABLE, no count" % what,
              (rc, out))
    nohead = os.path.join(td, "nohead.md")
    write(nohead, "# BOUNDARY: y\n\nsome prose, no PROMISES section\n")
    rc, out = run(nohead, "--tests", tests)
    check(rc == 3 and "UNREADABLE" in out and "PROMISES" in out, "a page with no PROMISES section cannot be parsed: "
          "exit 3, the cause named", (rc, out))
    badpy = os.path.join(td, "bad.py")
    write(badpy, "def t_x(:\n")
    rc, out = run(page, "--tests", badpy)
    check(rc == 3 and "UNREADABLE" in out, "a tests file that does not parse: exit 3", (rc, out))
    empty = os.path.join(td, "empty.md")
    write(empty, "# BOUNDARY: z\n\n## PROMISES\n\nnone yet.\n")
    rc, out = run(empty, "--tests", tests)
    check(rc == 4 and "NO PROMISES" in out and "covered" not in out, "a page with an empty PROMISES section: exit 4, "
          "its own outcome", (rc, out))
    rc, out = run()
    check(rc == 0 and "promises covered" in out and "UNREADABLE" not in out, "every page the tool checks by default "
          "(what ./publish runs) has a test for each promise", (rc, out[-600:]))
    import shutil
    shutil.rmtree(td, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "PASS selftest_boundary_check")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
