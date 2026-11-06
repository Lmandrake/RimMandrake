#!/usr/bin/env python3
"""selftest_scratch_reap_vanished_age.py -- a dir gone before its walk has no age (OPS_SCRATCH_DIRT_MEASURE_AT_END_HPCK).

The instance: 2026-11-05 23:11Z the end sanity read `oldest_h 498311.1 over 480`. 498311 h is now/3600: a fixture dir
listed by fixture_dirs() and removed (its selftest finished) before Tree() walked it keeps Tree.newest = 0.0, so
fixture_age_h answered "56 years old" and the line alarmed on a dir that no longer exists. The same zero reached
base_row's age_h (about forty REFUSE rows on 2026-11-05 02:03Z and 11:03Z carried age_h 4982xx). A dir that is gone
has no age: fixture_age_h answers None, base_row leaves age_h None, and measure()'s oldest_h stays a real age."""
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import scratch_reap as R  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def main():
    now = time.time()
    with tempfile.TemporaryDirectory(prefix="selftest_vanished_age_") as td:
        gone = Path(td) / "selftest_gone_fixture"          # listed, then removed before the walk: never created here
        age = R.fixture_age_h(gone, now)
        check(age is None, f"a fixture dir gone before its walk has no age (got {age!r})")

        row = R.base_row("clone", gone, R.walked(gone), now)
        check(row["age_h"] is None, f"base_row of a vanished candidate carries no age (got {row['age_h']!r})")

        live = Path(td) / "selftest_live_fixture"
        live.mkdir()
        (live / "f").write_text("x")
        a = R.fixture_age_h(live, now + 7200)
        check(a is not None and 1.9 < a < 2.1, f"a real fixture still reads its real age (got {a!r})")

        real_dirs = R.fixture_dirs
        R.fixture_dirs = lambda: [gone, live]
        try:
            m = R.measure(now, [], {})
        finally:
            R.fixture_dirs = real_dirs
        check(m["oldest_h"] < 1000, f"measure() oldest_h ignores a vanished fixture (got {m['oldest_h']})")
        check(m["selftest_dirs"] == 1, f"a vanished fixture is not counted as a fixture dir (got {m['selftest_dirs']})")
        lines = R.sanity_limits()
        check(not any("oldest_h" in p for p in R.judge_sanity("end", m)),
              f"the shipped end line ({lines.get('end', {}).get('oldest_h')}) raises nothing for a vanished fixture")
    print("FAILED: %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
