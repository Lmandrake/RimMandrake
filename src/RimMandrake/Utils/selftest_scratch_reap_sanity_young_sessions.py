#!/usr/bin/env python3
"""selftest_scratch_reap_sanity_young_sessions.py -- young work is not dirt (OPS_SCRATCH_DIRT_MEASURE_AT_START_SANF).

The instance: 2026-11-05 the start sanity read `session_dirs 468 over 400` while 443 of 475 session dirs were inside the
24 h TTL the sweep keeps them by (eight Relentless workers each run a Claude session). A dirt line must count what the
cleaner should have taken, as selftest_stale does for fixtures. This runs the SHIPPED lines (scratch_reap_sanity.json):
more young sessions than any line allows raise nothing about sessions; a session past the TTL is counted, at both ends."""
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import scratch_reap as R  # noqa: E402
R.CTIME_COUNTS = False   # utime sets mtime only

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def session(root: Path, n: int, age_s: float = 0.0) -> Path:
    s = root / "BENCH" / "claude-1000" / "-proj" / ("%08x-0000-4000-8000-000000000000" % n)
    (s / "tasks").mkdir(parents=True)
    f = s / "tasks" / "out.txt"
    f.write_text("x")
    if age_s:
        t = time.time() - age_s
        for p in (f, s / "tasks", s):
            os.utime(p, (t, t))
    return s


def about_sessions(problems):
    return [p for p in problems if p.startswith("session")]


def main():
    td = Path(tempfile.mkdtemp(prefix="selftest_young_sessions_"))
    root, sd = td / ".seat-tmp", td / "state"
    root.mkdir()
    sd.mkdir()
    os.environ.pop("SCRATCH_REAP_SANITY", None)          # the shipped lines are the thing under test
    os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_STATE=str(sd), SCRATCH_REAP_RM_SCRATCH=str(td / "rm_scratch"),
                      SCRATCH_REAP_CORPUS=str(td / "corpus"), SCRATCH_REAP_TMP="")
    lim = R.sanity_limits()
    most = max(lim["start"].get(k, 0) for k in ("session_dirs", "session_stale"))
    young = int(most) + 50
    for i in range(young):
        session(root, i)
    now = time.time()
    m = R.measure(now, None, {})
    check(m.get("session_dirs") == young, f"the reading still counts every session dir ({m.get('session_dirs')} of {young})")
    check(about_sessions(R.judge_sanity("start", m)) == [],
          f"{young} young session dirs raise no start problem: {about_sessions(R.judge_sanity('start', m))}")
    check(about_sessions(R.judge_sanity("end", m)) == [],
          f"{young} young session dirs raise no end problem: {about_sessions(R.judge_sanity('end', m))}")
    check(m.get("session_stale") == 0, f"no young session reads stale (session_stale={m.get('session_stale')})")
    session(root, young + 1, age_s=R.ttl_s() + 3600)
    m = R.measure(time.time(), None, {})
    check(m.get("session_stale") == 1, f"a session past the TTL by its newest content is counted (session_stale={m.get('session_stale')})")
    over = dict(m, session_stale=lim["start"].get("session_stale", 0) + 1)
    check(any(p.startswith("session_stale") for p in R.judge_sanity("start", over)), "stale sessions over the start line are a problem")
    rows = [{"kind": "session", "verdict": "REFUSE", "bytes": 0, "age_h": 30.0, "why": ["held"]},
            {"kind": "session", "verdict": "YOUNG", "bytes": 0, "age_h": 1.0, "why": []},
            {"kind": "clone", "verdict": "REFUSE", "bytes": 0, "age_h": 30.0, "why": ["held"]}]
    check(R.measure(time.time(), rows, {}).get("session_stale") == 1, "at the end, the stale sessions the run left are counted")
    print("FAILED: %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
