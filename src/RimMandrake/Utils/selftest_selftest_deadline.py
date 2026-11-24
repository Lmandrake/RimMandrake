#!/usr/bin/env python3
"""The selftest runner's deadline is one hang guard (design/specs/2026-11-22-selftest-deadline/boundary.md).

Item RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES, principle 7 (a limit names its danger). Before this,
the 240 s default killed real passes, so 136 test files carried their own `# selftest-timeout:` tag: each a per-case
repair of one limit with no danger named. One default (600 s then, 6000 s since 2026-11-24), which a tag may only raise.

    python3 src/RimMandrake/Utils/selftest_selftest_deadline.py        exit 0 all pass, 1 a promise is broken
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_selftests as RS  # noqa: E402

TOP = Path(__file__).resolve().parents[3]
DEFAULT = 6000


def _file(d, name, head):
    p = Path(d) / name
    p.write_text("#!/usr/bin/env python3\n" + head)
    return p


def t_one_hang_guard():
    with tempfile.TemporaryDirectory() as d:
        got = RS.per_test_timeout(_file(d, "selftest_plain.py", '"""no tag"""\n'))
        missing = RS.per_test_timeout(Path(d) / "selftest_absent.py")
    bad = []
    if RS.PER_TEST_TIMEOUT_S != DEFAULT:
        bad.append("PER_TEST_TIMEOUT_S is %r, the page says %d" % (RS.PER_TEST_TIMEOUT_S, DEFAULT))
    if got != DEFAULT:
        bad.append("an untagged test gets %r s, not %d" % (got, DEFAULT))
    if missing != DEFAULT:
        bad.append("an unreadable test gets %r s, not %d" % (missing, DEFAULT))
    return bad


def t_a_tag_only_raises():
    bad = []
    with tempfile.TemporaryDirectory() as d:
        for tag, want in ((30, DEFAULT), (900, DEFAULT), (6000, DEFAULT), (9000, 9000), (24000, 24000)):
            got = RS.per_test_timeout(_file(d, "selftest_t%d.py" % tag, "# selftest-timeout: %d\n" % tag))
            if got != want:
                bad.append("a tag of %d s gives %r s, not %d" % (tag, got, want))
    return bad


def t_out_of_time_is_unmeasured():
    """A test ended by the guard reads UNMEASURED and names the bound: never FAIL, and never the CRASH that turns a run red."""
    import progress_guard as G
    bad = []
    keep = RS.PER_TEST_TIMEOUT_S, G.communicate.__defaults__
    try:
        with tempfile.TemporaryDirectory() as d:
            RS.PER_TEST_TIMEOUT_S = 3
            G.communicate.__defaults__ = tuple(0.3 if x == G.POLL_S else x for x in keep[1])
            r = RS._run_one_in(_file(d, "selftest_spins.py", "import time\ntime.sleep(300)\n"))
            if r[1] != "UNMEASURED" or not r[3].startswith("deadline:") or "backstop" not in r[3]:
                bad.append("a test past its deadline reads %s [%s]" % (r[1], r[3]))
            RS.PER_TEST_TIMEOUT_S = 60
            r = RS._run_one_in(_file(d, "selftest_fine.py", "print('PASS')\n"))
            if r[1] != "PASS":
                bad.append("a test inside its deadline reads %s [%s]" % (r[1], r[3]))
            r = RS._run_one_in(_file(d, "selftest_red.py", "import sys\nprint('FAIL x')\nsys.exit(1)\n"))
            if r[1] != "FAIL":
                bad.append("a red test reads %s [%s]" % (r[1], r[3]))
    finally:
        RS.PER_TEST_TIMEOUT_S, G.communicate.__defaults__ = keep
    return bad


def main():
    tests = (t_one_hang_guard, t_a_tag_only_raises, t_out_of_time_is_unmeasured)
    fails = 0
    for t in tests:
        bad = t()
        for b in bad:
            print("FAIL  %s: %s" % (t.__name__, b))
        if not bad:
            print("PASS  %s" % t.__name__)
        fails += bool(bad)
    print("%d of %d pass" % (len(tests) - fails, len(tests)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
