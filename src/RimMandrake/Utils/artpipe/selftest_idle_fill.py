#!/usr/bin/env python3
"""selftest_idle_fill.py — ARTPIPE_IDLE_FILL_EMPTY_ALL_NIGHT: the art queue sat empty all night (10-26/27) with the
daemon alive and Codex at 15% of its week, because (a) nothing ran the gated feeder (donor_regen_jobs.py submit) on a
schedule and (b) its only job list was built once on 10-18, so defs that became owed later never entered it.

Each case was written before idle_fill.py existed (red: ImportError), then made green. No real queue, census or
Codex call is touched: every effect is injected.

    python3 src/RimMandrake/Utils/artpipe/selftest_idle_fill.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def state(tmp: Path, pending: int = 0, active: int = 0) -> Path:
    for d in ("pending", "active", "done", "failed", "status"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    for i in range(pending):
        (tmp / "pending" / f"job{i}.json").write_text("{}")
    for i in range(active):
        (tmp / "active" / f"act{i}.json").write_text("{}")
    (tmp / "active" / "x.manifest.json").write_text("{}")   # a manifest is not a job
    return tmp


class Fake:
    def __init__(self, filed: int = 0):
        self.built, self.submitted, self.filed = [], [], filed

    def build(self, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / "jobs.json"
        p.write_text(json.dumps({"rows": [{"id": "dregen_RM_New_v1", "facings": []}]}))
        self.built.append(p)
        return p

    def submit(self, jobs: list[Path], cap: int, dry: bool) -> dict:
        self.submitted.append((list(jobs), cap, dry))
        return {"rc": 0, "filed": self.filed}


def main() -> int:
    import idle_fill as IF

    with tempfile.TemporaryDirectory() as t:
        st = state(Path(t), pending=0)
        f = Fake(filed=3)
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f.build, submit=f.submit)
        check("empty queue, no list yet: builds a fresh owed list", len(f.built) == 1, str(f.built))
        check("empty queue: feeds the gated submit with that list", len(f.submitted) == 1
              and f.submitted[0][0] == f.built, str(f.submitted))
        check("result says FED with the filed count", r["action"] == "FED" and r["filed"] == 3, str(r))
        s = json.loads((st / "status" / "idle_fill.json").read_text())
        check("status file records depth/action/list", s["action"] == "FED" and s["depth"] == 0
              and s["jobs_list"].endswith("jobs.json"), str(s))

        # the same list again an hour later: no rebuild (the census costs ~11 min), still fed
        f2 = Fake(filed=0)
        r2 = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f2.build, submit=f2.submit)
        check("fresh list is reused, not rebuilt", f2.built == [] and len(f2.submitted) == 1, str(f2.built))
        check("nothing eligible left reads NOTHING_OWED, not FED", r2["action"] == "NOTHING_OWED", str(r2))

        # the 10-26 failure: the only list is stale (built long ago) -> must rebuild, not keep feeding the dead list
        lst = Path(r["jobs_list"])
        old = time.time() - 30 * 3600
        os.utime(lst, (old, old))
        f3 = Fake(filed=2)
        IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f3.build, submit=f3.submit)
        check("stale list (>max_age_h) is rebuilt before feeding", len(f3.built) == 1, str(f3.built))

    with tempfile.TemporaryDirectory() as t:
        st = state(Path(t), pending=2, active=2)
        f = Fake()
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f.build, submit=f.submit)
        check("busy queue (4 in flight >= low water 3): files nothing, builds nothing",
              r["action"] == "BUSY" and not f.built and not f.submitted and r["depth"] == 4, str(r))

    with tempfile.TemporaryDirectory() as t:
        f = Fake()
        try:
            IF.tick(Path(t) / "nope", low_water=3, cap=40, max_age_h=20, dry=False, build=f.build, submit=f.submit)
            check("absent state dir is an error, never an empty queue", False, "no exception")
        except SystemExit:
            check("absent state dir is an error, never an empty queue", not f.built and not f.submitted)

    with tempfile.TemporaryDirectory() as t:
        st = state(Path(t))

        def bad_build(out_dir):
            raise RuntimeError("census failed")
        f = Fake()
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=bad_build, submit=f.submit)
        check("a failed rebuild with no previous list files nothing and says so",
              r["action"] == "BUILD_FAILED" and not f.submitted, str(r))

    with tempfile.TemporaryDirectory() as t:
        st = state(Path(t))
        calls = []

        def failing_build(out_dir):
            calls.append(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)     # a real failed attempt leaves its dir and log behind
            raise RuntimeError("census rc=1")
        f = Fake()
        IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=failing_build, submit=f.submit)
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=failing_build, submit=f.submit)
        check("a failed rebuild is not retried on the next tick (backoff)", len(calls) == 1
              and r["action"] == "BUILD_FAILED" and "build_backoff" in r, f"{len(calls)} {r}")

    with tempfile.TemporaryDirectory() as t:
        st = state(Path(t))
        f = Fake()

        def hung_submit(jobs, cap, dry):
            raise TimeoutError("submit hung")
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f.build, submit=hung_submit)
        s = json.loads((st / "status" / "idle_fill.json").read_text())
        check("a crashed submit still writes a SUBMIT_FAILED status", r["action"] == "SUBMIT_FAILED"
              and s["action"] == "SUBMIT_FAILED", str(r))

        def backoff_submit(jobs, cap, dry):
            return {"rc": 0, "filed": 0, "tail": ["backing off: 4 429 lines in the artpipe journal; filing nothing"]}
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f.build, submit=backoff_submit)
        check("a 429 back-off reads BACKOFF_429, not NOTHING_OWED", r["action"] == "BACKOFF_429", str(r))

        def requeue_submit(jobs, cap, dry):
            (st / "pending" / "requeued.json").write_text("{}")   # failed-pool requeue: no 'job(s) filed' line
            return {"rc": 0, "filed": 0, "tail": ["eligible failed pool 1; in flight 0 / cap 40; this run up to 10"]}
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=False, build=f.build, submit=requeue_submit)
        check("a requeue that adds pending jobs reads FED", r["action"] == "FED" and r["depth_after"] == 1, str(r))

    with tempfile.TemporaryDirectory() as t:
        st = state(Path(t))
        f = Fake(filed=5)
        r = IF.tick(st, low_water=3, cap=40, max_age_h=20, dry=True, build=f.build, submit=f.submit)
        check("--dry-run passes dry to submit and writes no status", f.submitted and f.submitted[0][2] is True
              and not (st / "status" / "idle_fill.json").exists(), str(f.submitted))

    # the parsed count of the real submit's summary line (the tick reports what it filed)
    check("parse_filed reads submit's summary", IF.parse_filed(
        "x\n13 job(s) filed, 0 duplicate(s) refused, 0 row(s) refused\n") == 13)
    check("parse_filed: no summary line reads 0", IF.parse_filed("nothing to file (queue at cap)\n") == 0)

    print(f"\n{'FAILED ' + str(len(FAILS)) if FAILS else 'ALL PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
