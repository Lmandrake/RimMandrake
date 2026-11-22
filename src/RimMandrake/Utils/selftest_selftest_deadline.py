#!/usr/bin/env python3
"""The selftest runner's deadline is one hang guard (design/specs/2026-11-22-selftest-deadline/boundary.md).

Item RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES, principle 7 (a limit names its danger). Before this,
the 240 s default killed real passes, so 136 test files carried their own `# selftest-timeout:` tag: each a per-case
repair of one limit with no danger named. One default of 600 s, which a tag may only raise, makes those tags dead.

    python3 src/RimMandrake/Utils/selftest_selftest_deadline.py        exit 0 all pass, 1 a promise is broken
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_selftests as RS  # noqa: E402

TOP = Path(__file__).resolve().parents[3]
DEFAULT = 600


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
        for tag, want in ((30, DEFAULT), (240, DEFAULT), (600, DEFAULT), (900, 900), (2400, 2400)):
            got = RS.per_test_timeout(_file(d, "selftest_t%d.py" % tag, "# selftest-timeout: %d\n" % tag))
            if got != want:
                bad.append("a tag of %d s gives %r s, not %d" % (tag, got, want))
    return bad


TAG = re.compile(r"^#\s*selftest-timeout:\s*(\d+)", re.M)


def dead_tags(top=TOP):
    """[(repo-relative path, tag)] for tracked selftest files whose head holds a tag at or below the default."""
    out = subprocess.run(["git", "-C", str(top), "ls-files", "*selftest*.py"], capture_output=True, text=True,
                         timeout=60, check=True).stdout.split()
    dead = []
    for rel in out:
        try:
            head = "".join(open(os.path.join(top, rel), encoding="utf-8", errors="replace").readlines()[:40])
        except OSError:
            continue
        m = TAG.search(head)
        if m and int(m.group(1)) <= DEFAULT:
            dead.append((rel, int(m.group(1))))
    return dead


def t_no_dead_tag():
    dead = dead_tags()
    return ["%d test file(s) carry a tag of %d s or less, which has no effect: delete the line (first: %s)"
            % (len(dead), DEFAULT, ", ".join("%s=%d" % x for x in dead[:3]))] if dead else []


def _planted_dead_tag_is_seen():
    """The tree scan can see: a temp repo with one dead tag reads red, one live tag reads green."""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", d], check=True, timeout=30)
        _file(d, "selftest_dead.py", "# selftest-timeout: 300\n")
        _file(d, "selftest_live.py", "# selftest-timeout: 900\n")
        subprocess.run(["git", "-C", d, "add", "."], check=True, timeout=30)
        got = dead_tags(Path(d))
    return [] if got == [("selftest_dead.py", 300)] else ["the tree scan read %r on a planted dead tag" % (got,)]


def main():
    tests = (t_one_hang_guard, t_a_tag_only_raises, t_no_dead_tag, _planted_dead_tag_is_seen)
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
