#!/usr/bin/env python3
"""selftest_boundary_check.py — boundary_check.py keeps its four answers apart, and refuses a broken page at ./publish.

RIMMANDRAKE_BUILD_BOUNDARY_CHECK_PROMISE_WITHOUT_TEST_REFUSED (owner by card 2026-11-18, `standing_rulings.md` §A
boundary page before pipeline code): each promise on a boundary page has a test of the same name. The four answers:
every promise tested (exit 0, `promises covered N of M`); a promise with no test (exit 1, named); a page with no
promises (exit 4, its own outcome); a page or tests file that cannot be read or parsed (exit 3, UNREADABLE with the
cause, never `0 of 0`). Last, every page the tool checks by default (what ./publish runs) passes today.

RIMMANDRAKE_CHECK_PAGE_ONLY_EDIT_AT_PUBLISH_SLIPS_PAST: a promise is covered only by a test the tests file's `main()`
runs (a test nothing runs is not a cover; a `main()` that picks its tests at run time, or none, is UNREADABLE), and a
change to a boundary page alone selects boundary_check at ./publish, where an untested promise on it is refused.
"""
import os
import re
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


def page_only_change(td, write):
    """Hole 1: a commit that touches only a boundary page selects boundary_check at ./publish, and the tool refuses the
    page when a promise added to it has no test; a page nobody registered is not passed by silence."""
    import json
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import boundary_check as B
    import publish as P
    top = B.TOP
    rel = sorted(B.PAGES)[0]
    cfg = json.load(open(os.path.join(top, P.PIPELINE_TESTS), encoding="utf-8"))
    sel = [c["test"] for c in P.pipeline_selection(top, [rel], cfg)]
    check("src/RimMandrake/Utils/boundary_check.py" in sel, "a change to %s alone selects boundary_check at ./publish"
          % rel, sel)
    spec = os.path.join(td, "spec")
    os.makedirs(os.path.join(spec, os.path.dirname(rel)))
    with open(os.path.join(top, rel), encoding="utf-8") as f:
        text = f.read()
    write(os.path.join(spec, rel), text.replace("## PROMISES", "## PROMISES\n\n- **a-promise-nobody-tested.** new.", 1))
    tests = B.PAGES[rel]
    os.makedirs(os.path.join(spec, os.path.dirname(tests)))
    write(os.path.join(spec, tests), open(os.path.join(top, tests), encoding="utf-8").read())
    stray = os.path.join(spec, "design", "specs", "2099-01-01-unregistered", "boundary.md")
    os.makedirs(os.path.dirname(stray))
    write(stray, "# BOUNDARY: u\n\n## PROMISES\n\n- **x.** y.\n")
    import contextlib
    import io
    B.TOP, buf = spec, io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = B.main([])
    finally:
        B.TOP = top
    out = buf.getvalue()
    check(rc != 0 and "t_a_promise_nobody_tested" in out, "that page with an untested promise added is refused by the "
          "run ./publish makes", (rc, out[-600:]))
    check("2099-01-01-unregistered" in out and "UNREADABLE" in out, "a boundary page with no tests file registered in "
          "PAGES is UNREADABLE, not passed by silence", (rc, out[-600:]))


def runtime_optional_test_counted(td, write):
    page = os.path.join(td, "optional.md")
    tests = os.path.join(td, "selftest_optional.py")
    write(page, "# BOUNDARY: optional\n\n## PROMISES\n\n- **always.** a.\n- **live.** b.\n")
    defs = "import argparse\nimport sys\n\ndef t_always():\n    pass\n\ndef t_live():\n    pass\n\n"
    parse = ('    parser = argparse.ArgumentParser()\n    parser.add_argument("--live", action="store_true")\n'
             '    args = parser.parse_args()\n')
    for signature, setup, guard in (("argv", "", "'--live' in argv"),
                                    ("", "", "'--live' in sys.argv"),
                                    ("", parse, "args.live")):
        write(tests, defs + "def main(%s):\n%s    t_always()\n    if %s:\n        t_live()\n"
              % (signature, setup, guard))
        rc, out = run(page, "--tests", tests)
        check(rc == 3 and "UNREADABLE" in out and "run time" in out and "t_live" in out and "covered" not in out,
              "runtime_optional_test_counted: a CLI-only promise is unreadable, with no coverage count (%s)" % guard,
              (rc, out))


def main():
    td = tempfile.mkdtemp(prefix="selftest_boundary_check_")
    page, tests = os.path.join(td, "boundary.md"), os.path.join(td, "selftest_x.py")

    def write(p, s):
        with open(p, "w", encoding="utf-8") as f:
            f.write(s)
    write(page, "# BOUNDARY: x\n\n## DOES NOT SURVIVE (not promised)\n\n- **two-failures.** not a promise.\n\n"
                "## PROMISES (each one is owed a test)\n\n- **off-blocks-starts.** a.\n- **queue-is-the-store's.** b.\n"
                "\n## SURVIVES\n\n- **a-lost-lock.** c.\n\n## LIFE CYCLES\n\n- **run:** not a promise.\n")
    write(tests, "def t_off_blocks_starts():\n    pass\n\n\ndef main():\n    t_off_blocks_starts()\n")
    rc, out = run(page, "--tests", tests)
    check(rc == 1 and "promises covered 1 of 3" in out and "t_queue_is_the_stores" in out and "t_a_lost_lock" in out
          and "two_failures" not in out, "untested promise and SURVIVES entry: exit 1, each named; DOES NOT SURVIVE "
          "and LIFE CYCLES are not promises", (rc, out))
    write(tests, "def t_off_blocks_starts():\n    pass\n\n\ndef t_queue_is_the_stores():\n    pass\n\n\n"
                 "def t_lost():\n    pass\n\n\nt_a_lost_lock = t_lost\n\n\n"
                 "def main():\n    for t in (t_off_blocks_starts, t_queue_is_the_stores, t_lost):\n        t()\n")
    rc, out = run(page, "--tests", tests)
    check(rc == 0 and "promises covered 3 of 3" in out, "every promise tested (a def, or a name bound to one) and run by "
          "main(): exit 0", (rc, out))
    runtime_optional_test_counted(td, write)
    unrun = os.path.join(td, "selftest_unrun.py")
    write(unrun, "def t_off_blocks_starts():\n    pass\n\n\ndef t_queue_is_the_stores():\n    pass\n\n\n"
                 "def t_a_lost_lock():\n    pass\n\n\ndef main():\n    t_off_blocks_starts()\n    t_a_lost_lock()\n")
    rc, out = run(page, "--tests", unrun)
    check(rc == 1 and "promises covered 2 of 3" in out and "t_queue_is_the_stores" in out and "main()" in out,
          "a promise whose test exists but main() never runs it is not covered: exit 1, named", (rc, out))
    for what, body in (("no main()", "def t_off_blocks_starts():\n    pass\n"),
                       ("a main() that picks its tests at run time",
                        "def t_off_blocks_starts():\n    pass\n\n\ndef main():\n"
                        "    for k, v in list(globals().items()):\n        v() if k.startswith('t_') else None\n")):
        write(unrun, body)
        rc, out = run(page, "--tests", unrun)
        check(rc == 3 and "UNREADABLE" in out and "main()" in out and "covered" not in out,
              "a tests file with %s: which tests run cannot be read, exit 3, never covered" % what, (rc, out))
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
    # an UNREADABLE verdict opens its line; the word alone can sit in a clone's path (a helper clone is named for its
    # item, and RIMMANDRAKE_RENAME_GAMES_..._LETTERS_UNREADABLE read as a blind page on every line, 2026-11-22)
    check(rc == 0 and "promises covered" in out and not re.search(r"^UNREADABLE", out, re.M),
          "every page the tool checks by default "
          "(what ./publish runs) has a test for each promise", (rc, out[-600:]))
    page_only_change(td, write)
    import shutil
    shutil.rmtree(td, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "PASS selftest_boundary_check")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
