#!/usr/bin/env python3
"""selftest_ops_watch_scratch_dirty_mid_run.py -- disk.scratch_dirty_end must not read a clean 0 while a run is going.

RIMMANDRAKE_HOLD_SCRATCH_DIRTY_END_WHILE_CLEANER_RUNS: the cleaner's start dropped the last run's end, and a run lasts
~50 min of every hour, so disk.scratch_dirty_end read 0 ("clean") for most passes while every finished run ended with
4 problems (measured 2026-11-17: 11 of 12 passes read 0, sanity.json end 4). The start now keeps the last end as
`prev_end`, and the reader shows it, marked running, until the new end lands. Real writer, real reader, a temp dir."""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402
import scratch_reap as R  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def read(sd):
    return OW.scratch_dirty(sd / "sanity.json")


sd = Path(tempfile.mkdtemp(prefix="selftest_scratch_dirty_mid_run_"))
san = sd / "sanity.json"

r = read(sd)
check(r["disk.scratch_dirty_start"]["v"] == 0 and r["disk.scratch_dirty_end"]["v"] == 0, "no record yet reads 0 at both ends")

R.sanity_write(sd, "start", {}, ["a", "b"])
r = read(sd)
check(r["disk.scratch_dirty_end"]["v"] == 0, "first run ever, in progress: no end on record reads 0")

R.sanity_write(sd, "end", {}, ["p1", "p2", "p3", "p4"])
r = read(sd)
check(r["disk.scratch_dirty_end"]["v"] == 4 and not (r["disk.scratch_dirty_end"].get("x") or {}).get("running"),
      "a finished run's end reads its 4 problems, not running")

R.sanity_write(sd, "start", {}, ["s1"])
rec = json.loads(san.read_text())
check("end" not in rec and (rec.get("prev_end") or {}).get("problems") == ["p1", "p2", "p3", "p4"],
      "a new start drops `end` and keeps it as `prev_end`")
r = read(sd)
e = r["disk.scratch_dirty_end"]
check(e["v"] == 4 and (e.get("x") or {}).get("running") is True,
      "mid-run, the end reads the last finished run's 4 problems, marked running (was a false clean 0)")
check(r["disk.scratch_dirty_start"]["v"] == 1, "the start reads the new run's own problems")

R.sanity_write(sd, "end", {}, [])
r = read(sd)
check(r["disk.scratch_dirty_end"]["v"] == 0 and "prev_end" not in json.loads(san.read_text()),
      "a clean end reads 0 and retires prev_end")

R.sanity_write(sd, "start", {}, [])
check(read(sd)["disk.scratch_dirty_end"]["v"] == 0, "mid-run after a clean end reads that clean 0")

san.write_text("{torn")
check(read(sd)["disk.scratch_dirty_end"]["v"] == 9999, "a torn record is the alarm, not silence")

print("PASS" if not FAILS else "FAIL %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
