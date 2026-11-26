#!/usr/bin/env python3
"""selftest_scratch_reap_row_age.py — the reaper's runs.jsonl row is aged from the moment it was WRITTEN, not from the
moment its run STARTED (RIMMANDRAKE_SPEED_SCRATCH_REAP_APPLY_RUNS_PASS_TWO_HOURS).

The failure: ops_watch dated the row by `ts` (the run's start) and refused a row over 3 h old. The row is written at the
end of the run. On Archmagi runs grew to 1.5-2.3 h (journal, 2026-11-24..26), so a fresh row read 2 h old the moment it
landed and disk.scratch_total_gb / disk.scratch_refused_gb went UNMEASURED for part of every cycle (blind 29 times since
2026-11-05). A slow live reaper was read as a dead one.

Proves: (1) a real isolated apply run writes `end_epoch` on its runs.jsonl row; (2) the reader takes a row that started
3.5 h ago and was written 20 min ago as MEASURED; (3) a row written 3.2 h ago still ages out (a dead or hung reaper
writes no new row, so the bound still catches it); (4) an old-format row with no end_epoch is aged by `ts` as before;
(5) a row written in the future is refused.
Page: design/specs/2026-11-26-scratch-row-aged-by-write/boundary.md (each check names its promise)."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = []


def ck(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        F.append(w)


def t_the_row_carries_its_write_time():
    with tempfile.TemporaryDirectory(prefix="selftest_row_age_") as td:
        t = Path(td)
        for d in ("roots", "corpus", "state", "mirrors", "transcripts", "archive", "tmp"):
            (t / d).mkdir()
        env = dict(os.environ, SCRATCH_REAP_ROOTS=str(t / "roots"), SCRATCH_REAP_SCAN=str(t / "roots"),
                   SCRATCH_REAP_CORPUS=str(t / "corpus"), SCRATCH_REAP_STATE=str(t / "state"),
                   SCRATCH_REAP_MIRRORS=str(t / "mirrors"), SCRATCH_REAP_TRANSCRIPTS=str(t / "transcripts"),
                   SCRATCH_REAP_RM_SCRATCH="/nonexistent", SCRATCH_REAP_TMP=str(t / "tmp"),
                   LEFTOVERS_ARCHIVE_ROOT=str(t / "archive"), SCRATCH_REAP_UNIT="rm-scratch-reap-selftest.service")
        t0 = time.time()
        r = subprocess.run([sys.executable, str(HERE / "scratch_reap.py"), "--apply"], env=env, capture_output=True,
                           text=True, timeout=600)     # hang guard only: an empty fixture run takes seconds
        p = t / "state" / "runs.jsonl"
        if not p.exists():
            ck(False, "the-row-carries-its-write-time: the isolated reaper wrote runs.jsonl (rc %s): %r" % (r.returncode, (r.stderr or r.stdout)[-300:]))
            return
        row = json.loads(p.read_text().splitlines()[-1])
        e = row.get("end_epoch")
        ck(isinstance(e, (int, float)) and t0 - 5 <= e <= time.time() + 5,
           "the-row-carries-its-write-time: an apply run's runs.jsonl row carries end_epoch, the time it was written (%r)" % e)


def read(row):
    """-> the disk.scratch_total_gb point for a runs.jsonl whose last row is `row` (two scratch rows, 4 GB)."""
    os.environ.setdefault("RM_OPS_WATCH_DIR", tempfile.mkdtemp(prefix="selftest_row_age_ops_"))
    sys.path.insert(0, str(HERE))
    import ops_watch as OW
    with tempfile.TemporaryDirectory(prefix="selftest_row_age_rd_") as td:
        p = Path(td) / "runs.jsonl"
        os.environ["RM_SCRATCH_REAP_RUNS"] = str(p)
        rows = [{"verdict": "YOUNG", "bytes": 3e9}, {"verdict": "REFUSE", "bytes": 1e9}]
        p.write_text(json.dumps(dict({k: (OW.iso(v) if k == "ts" else v) for k, v in row.items()}, rows=rows)) + "\n")
        out = {}
        try:
            OW.scratch_reading(NOW, out)
        except AttributeError as e:
            return {"m": "crash: %s" % e}
        return out.get("disk.scratch_total_gb", {})


H = 3600.0
NOW = time.time()


def t_a_slow_live_reaper_reads_measured():
    got = read({"ts": NOW - 3.5 * H, "end_epoch": NOW - 0.33 * H})
    ck(got.get("m") == "MEASURED" and got.get("v") == 4.0,
       "a-slow-live-reaper-reads-measured: a 3.5 h run whose row was written 20 min ago reads MEASURED (%r)" % got)


def t_a_dead_reaper_still_ages_out():
    got = read({"ts": NOW - 5 * H, "end_epoch": NOW - 3.2 * H})
    ck(got.get("m") == "UNMEASURED", "a-dead-reaper-still-ages-out: a row written 3.2 h ago reads UNMEASURED (%r)" % got)


def t_an_old_row_is_aged_by_its_start():
    got = read({"ts": NOW - H})
    ck(got.get("m") == "MEASURED", "an-old-row-is-aged-by-its-start: no end_epoch, ts 1 h old -> MEASURED (%r)" % got)
    got = read({"ts": NOW - 5 * H})
    ck(got.get("m") == "UNMEASURED", "an-old-row-is-aged-by-its-start: no end_epoch, ts 5 h old -> UNMEASURED (%r)" % got)


def t_a_future_row_is_refused():
    got = read({"ts": NOW - H, "end_epoch": NOW + H})
    ck(got.get("m") == "UNMEASURED", "a-future-row-is-refused: a row written in the future is refused (%r)" % got)


def main() -> int:
    t_the_row_carries_its_write_time()
    t_a_slow_live_reaper_reads_measured()
    t_a_dead_reaper_still_ages_out()
    t_an_old_row_is_aged_by_its_start()
    t_a_future_row_is_refused()
    print("selftest_scratch_reap_row_age:", "FAIL" if F else "PASS", len(F))
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
