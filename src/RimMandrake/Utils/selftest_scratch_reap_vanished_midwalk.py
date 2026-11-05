#!/usr/bin/env python3
"""selftest_scratch_reap_vanished_midwalk.py -- a candidate that vanishes while it is judged is gone, not refused
(OPS_SCRATCH_DIRT_MEASURE_AT_END_QLKI).

The instance: the 2026-11-05 11:03Z run ended `refused 139 over 60` and `oldest_h 498299.1 over 480`. 106 of the rows
were /tmp/selftest_run_*/…/clone dirs a selftest removed while the reaper walked them: each came back REFUSE
`unreadable: … No such file or directory`, aged from the epoch. The first fix (4583393f) skipped a candidate already gone
before its walk began; this one vanishes INSIDE judge_clone, after that check, as the live ones did."""
import os
import shutil
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
    td = Path(tempfile.mkdtemp(prefix="selftest_vanished_midwalk_"))
    root, sd = td / ".seat-tmp", td / "state"
    root.mkdir()
    sd.mkdir()
    os.environ.pop("SCRATCH_REAP_SANITY", None)
    os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_STATE=str(sd), SCRATCH_REAP_RM_SCRATCH=str(td / "rm_scratch"),
                      SCRATCH_REAP_CORPUS=str(td / "corpus"), SCRATCH_REAP_TMP="")
    gone = []
    for i in range(R.sanity_limits()["end"].get("refused", 60) + 5):
        c = root / "BENCH" / f"run{i}" / "clone"
        (c / ".git").mkdir(parents=True)
        (c / "f.txt").write_text("x")
        gone.append(c)
    real_judge = R.judge_clone

    def vanishing(p, ctx):
        shutil.rmtree(p)              # the selftest that owned it tears it down mid-walk
        return real_judge(p, ctx)

    R.candidates = lambda: [("clone", p) for p in gone]
    R.judge_clone = vanishing
    try:
        now = time.time()
        rows = R.judge_all(R.Ctx(now))
        refused = [r for r in rows if r["verdict"] == "REFUSE"]
        check(refused == [], f"no vanished clone is refused ({len(refused)} of {len(gone)} were)")
        m = R.measure(now, rows, {})
        probs = [p for p in R.judge_sanity("end", m) if p.startswith(("refused", "oldest_h"))]
        check(probs == [], f"the end reading raises no refused/oldest_h line ({probs})")
    finally:
        R.judge_clone = real_judge
        shutil.rmtree(td, ignore_errors=True)
    print("FAIL" if FAILS else "OK", "selftest_scratch_reap_vanished_midwalk")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
