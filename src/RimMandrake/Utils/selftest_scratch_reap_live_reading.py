#!/usr/bin/env python3
"""selftest_scratch_reap_live_reading.py [READING ...] — a file a `--live "unit=rm-scratch-reap.timer reading=<f> max_age=…"`
promise names must be rewritten by EVERY apply run, including a quiet one that finds nothing new. Otherwise the deadman
reads a healthy unit as dead. Instance: MIRROR_PACK_REPAIR_STILL_GRUMBLING (2026-11-05) promised alarms.log, which a run
writes only on a new refusal (alarms_seen.json dedups); with the unit firing hourly the reading aged past 6 h and the
fixed item was reopened as broken. With no arguments this checks the readings the scratch-reap promises use now
(last_run.json); `alarms.log` as an argument replays the instance and fails."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMISED = ["last_run.json"]


def run(env):
    return subprocess.run([sys.executable, str(HERE / "scratch_reap.py"), "--apply"], env=env, capture_output=True,
                          text=True, timeout=300)


def main(argv) -> int:
    readings = argv or PROMISED
    bad = []
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        for d in ("roots", "corpus", "state", "mirrors", "transcripts", "archive", "tmp"):
            (t / d).mkdir()
        env = dict(os.environ, SCRATCH_REAP_ROOTS=str(t / "roots"), SCRATCH_REAP_SCAN=str(t / "roots"),
                   SCRATCH_REAP_CORPUS=str(t / "corpus"), SCRATCH_REAP_STATE=str(t / "state"),
                   SCRATCH_REAP_MIRRORS=str(t / "mirrors"), SCRATCH_REAP_TRANSCRIPTS=str(t / "transcripts"),
                   SCRATCH_REAP_RM_SCRATCH="/nonexistent", SCRATCH_REAP_TMP=str(t / "tmp"),
                   LEFTOVERS_ARCHIVE_ROOT=str(t / "archive"), SCRATCH_REAP_UNIT="rm-scratch-reap-selftest.service")
        first = run(env)
        sd = t / "state"
        before = {}
        for name in readings:
            p = sd / name
            if not p.exists():
                p.write_text("")        # a reading the first run did not make: it must still be made by the next
            os.utime(p, (time.time() - 7200, time.time() - 7200))
            before[name] = p.stat().st_mtime
        second = run(env)
        for name in readings:
            p = sd / name
            if not p.exists() or p.stat().st_mtime <= before[name] + 60:
                bad.append(f"{name}: a quiet apply run left it {time.time() - p.stat().st_mtime:.0f} s old "
                           "(a live promise on it reads a healthy unit as dead)" if p.exists() else f"{name}: gone")
        if not (sd / "last_run.json").exists():
            bad.append(f"the isolated reaper wrote no last_run.json (rc {first.returncode}/{second.returncode}): "
                       f"{(second.stderr or second.stdout)[-300:]!r}")
    for b in bad:
        print("FAIL", b)
    print("selftest_scratch_reap_live_reading:", "FAIL" if bad else "PASS", " ".join(readings))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
