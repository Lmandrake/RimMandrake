#!/usr/bin/env python3
"""A test that passes within 10% of its timeout is tomorrow's nightly red (NIGHTLY_COP_FIX_RED_HMGHDI_RQAA).

The instance: selftest_arena_tasks.py passed alone at 468 s against a 480 s tag and timed out on the 6-worker nightly,
which reopened this item twice. Nothing looked at a PASS's margin, so the first anyone heard of it was the red.

Reads run_selftests' last measured wall times (selftest_timings.json, the slowest-first schedule's file) against each
test's own cap. A timed-out run is not in that file: it is already red, and its time is the cap, not a measurement.
On a machine with no timings file (a walled checker) only the fixture checks below can run, and the output says so.

    selftest_near_cap.py                               fixtures, then this machine's timings
    selftest_near_cap.py --reading <path>=<secs>/<cap>   replay one reading; red when it is past the line
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_selftests as RS  # noqa: E402

LINE = 0.90


def past_line(readings):
    """[(path, secs, cap)] -> those at or past LINE of their cap, the closest to it first."""
    return sorted((r for r in readings if r[1] >= LINE * r[2]), key=lambda r: r[1] / r[2], reverse=True)


def measured(timings, root):
    """{repo-relative path: secs} -> [(path, secs, cap)] for tests that still exist; a deleted test owes nothing."""
    out = []
    for rel, secs in timings.items():
        p = Path(root) / rel
        if p.is_file():
            out.append((rel, float(secs), RS.per_test_timeout(p)))
    return out


def report(rows):
    for rel, secs, cap in rows:
        print("NEAR CAP  %.0f s of %d s (%.0f%%)  %s" % (secs, cap, 100 * secs / cap, rel))
    if rows:
        print("%d test(s) past %.0f%% of their timeout: speed each one up or split it. Raising its tag only moves the line "
              "if the time is honest." % (len(rows), 100 * LINE))
    return 1 if rows else 0


def fixtures():
    """-> failures: the line, the tag and the deleted-test rule, on a real tagged file."""
    bad = []
    if [r[0] for r in past_line([("a", 468.0, 480), ("b", 216.0, 240), ("c", 215.9, 240)])] != ["a", "b"]:
        bad.append("past_line: 468/480 and 216/240 are past the line, 215.9/240 is not")
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "selftest_slow.py").write_text("#!/usr/bin/env python3\n# selftest-timeout: 600\n")
        (Path(d) / "selftest_plain.py").write_text("#!/usr/bin/env python3\n")
        got = measured({"selftest_slow.py": 300, "selftest_plain.py": 230, "selftest_gone.py": 999}, d)
        if sorted(got) != [("selftest_plain.py", 230.0, RS.PER_TEST_TIMEOUT_S), ("selftest_slow.py", 300.0, 600)]:
            bad.append("measured: a test's own tag sets its cap and a deleted test is dropped, got %r" % (got,))
        if [r[0] for r in past_line(got)] != ["selftest_plain.py"]:
            bad.append("the tagged test at half its 600 s cap passes, the plain one at 230 of 240 s does not")
    return bad


def main(argv):
    if argv[:1] == ["--reading"]:
        rel, _, rest = argv[1].partition("=")
        secs, _, cap = rest.partition("/")
        return report(past_line([(rel, float(secs), int(cap))]))
    bad = fixtures()
    for b in bad:
        print("FAIL  " + b)
    if bad:
        return 1
    print("fixtures: the line, the tag and the deleted-test rule hold")
    if not RS.TIMINGS_FILE.is_file():
        print("no timings at %s: this machine's margins were not read" % RS.TIMINGS_FILE)
        return 0
    rows = measured(json.loads(RS.TIMINGS_FILE.read_text()), RS.REPO_ROOT)
    print("%d measured test(s) read from %s" % (len(rows), RS.TIMINGS_FILE))
    return report(past_line(rows))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
