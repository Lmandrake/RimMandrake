#!/usr/bin/env python3
"""selftest_sheet_newest_job.py — ART_SHEET_FIX_NEWEST_JOB_WINS: two artpipe jobs that collapse to one family/facing
(`X_north` and its regen `X_north_r2`) show the NEWEST job's bytes, in whatever order the index iterates them."""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as A  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class Idx:
    def __init__(self, variants):
        self.variants = variants

    def is_purged(self, sha):
        return False


def var(job, ts, facing="north"):
    return {"kind": "artpipe", "job": job, "ts": ts, "facing": facing, "date": ts[:10], "prompt": "p", "item": "i"}


def run(order):
    old, new = ("o" * 64, [var("zorbwyrm_north", "2026-10-01T00:00:00Z")]), ("n" * 64, [var("zorbwyrm_north_r2", "2026-10-20T00:00:00Z")])
    pairs = [old, new] if order == "old_first" else [new, old]
    A.failed_canon_jobs = lambda: set()
    A.job_slots = lambda: {}
    cols = A.name_render_cols(Idx(dict(pairs)), ["zorbwyrm"], [])
    return cols[0]["faces"].get("north"), cols[0]["date"]


for order in ("old_first", "new_first"):
    sha, date = run(order)
    check(sha == "n" * 64, f"{order}: the _r2 regen's bytes show")
    check(date == "2026-10-20", f"{order}: family date is the newest job's")

held = {}
check(A.newest_job_takes(held, "k", "a_north", var("a_north", "2026-10-01T00:00:00Z"), "x"), "first takes")
check(not A.newest_job_takes(held, "k", "a_north", var("a_north", "2026-10-01T00:00:00Z"), "y"), "tie keeps first")
check(A.newest_job_takes(held, "k", "a_north", var("a_north", "2026-10-02T00:00:00Z"), "z"), "re-seat of same job takes")
check(A.newest_job_takes(held, "k", "a_north_r1", var("a_north_r1", ""), "w") is False, "no-ts r1 does not beat a dated job")
print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
