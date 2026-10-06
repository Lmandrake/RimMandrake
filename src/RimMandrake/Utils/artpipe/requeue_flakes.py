#!/usr/bin/env python3
"""Requeue artpipe jobs that failed for reasons a plain retry fixes.

  worker_error   -> codex 'response-schema channel mismatch' flake; requeue as-is
  master_failed  -> a facing whose derive_from master failed; requeue once that
                    master is pending, active or done again (never while it sits in failed/)

failed_canon and bad_job_file are never touched: the first already had the daemon's
corrected retry, the second needs a human fix. Each job is requeued at most --max times,
counted from its parked manifests in _requeued_manifests/. Same move the 2026-10-05
triage made by hand (Transient/biome_ffar/failure_triage_2026-10-05.md):
job json failed/ -> pending/, manifest -> _requeued_manifests/<id>.manifest.<ts>.json.
Item: ARTPIPE_REQUEUE_AUTOMATION_1.

  python3 requeue_flakes.py [--dry-run] [--max 3] [--since-hours 24]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from state_dir import require  # D:\Luke\dev\_artpipe; refuses when absent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--since-hours", type=float, default=24)
    a = ap.parse_args(argv)
    S = Path(require())
    failed, pending, active, done, parked = (S / d for d in ("failed", "pending", "active", "done", "_requeued_manifests"))
    missing = [d.name for d in (failed, pending) if not d.is_dir()]
    if missing:  # require() checks done/ only; a missing pending/ would fail mid-pass at the rename
        raise SystemExit(f"artpipe state dir {S} has no {'/, '.join(missing)}/ — refusing to requeue.")
    cutoff = time.time() - a.since_hours * 3600
    alive = lambda jid: any((d / f"{jid}.json").exists() for d in (pending, active, done))
    moved = {"worker_error": 0, "master_failed": 0}
    skipped = {"cap": 0, "master_still_failed": 0, "unreadable": 0}
    unreadable = []
    for man in sorted(failed.glob("*.manifest.json")):
        jid = man.name[: -len(".manifest.json")]
        job = failed / f"{jid}.json"
        if not job.exists() or man.stat().st_mtime < cutoff:
            continue
        try:
            ws = json.loads(man.read_text()).get("worker_status")
        except (OSError, ValueError, AttributeError) as e:
            skipped["unreadable"] += 1; unreadable.append(f"{man.name}: {e}")
            continue
        if ws not in moved:
            continue
        if len(list(parked.glob(f"{jid}.manifest*.json"))) >= a.max:
            skipped["cap"] += 1
            continue
        if ws == "master_failed":
            try:
                master = json.loads(job.read_text()).get("derive_from")
            except (OSError, ValueError, AttributeError) as e:
                skipped["unreadable"] += 1; unreadable.append(f"{job.name}: {e}")
                continue
            if master and not alive(master):
                skipped["master_still_failed"] += 1
                continue
        moved[ws] += 1
        if not a.dry_run:
            parked.mkdir(exist_ok=True)
            man.rename(parked / f"{jid}.manifest.{int(time.time())}.json")
            job.rename(pending / job.name)
    print(f"requeue_flakes{' (dry run)' if a.dry_run else ''}: requeued {moved}, skipped {skipped}")
    for u in unreadable:
        print(f"  unreadable, left in failed/: {u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
