#!/usr/bin/env python3
"""cancel_jobs.py - take PENDING artpipe jobs out of the queue before the daemon claims them.

`artreg withdraw` is registry-only and the daemon ignores it; with no cancel, an owner's "stop the Surrik
rounds" could not stop arteval_RM_Surrik_s1r2_north/south from rendering (ART_SERIES_WIRE_STOP_AND_CANCEL).

  python3 cancel_jobs.py [--dry-run] <job-id-or-glob> [...]

Each match in pending/ is renamed to cancelled/<id>.json (a rename: atomic, and the claim is also a rename,
so exactly one of cancel / claim wins). A job already in active/ is NOT touched - a worker is running it;
it is reported and the exit code is 3 so the caller knows it still has to wait or let it finish. Nothing
matching at all exits 2. Pair with `fauna_drive.py stop <def>` for a fresh art-eval series, so it files nothing new.
"""
import argparse
import fnmatch
import os
import sys
from pathlib import Path

from state_dir import require


def cancel(root: Path, patterns, dry_run: bool = False):
    """Returns (cancelled ids, still-running ids, patterns that matched nothing)."""
    pending, active, cancelled = root / "pending", root / "active", root / "cancelled"
    if not pending.is_dir():
        raise SystemExit(f"artpipe state dir {root} has no pending/ - refusing to cancel.")

    def ids(d):
        try:
            return sorted(p.stem for p in d.glob("*.json") if not p.name.endswith(".worker_last_message.json"))
        except OSError:
            return []

    done, running, unmatched = [], [], []
    pend, act = ids(pending), ids(active)
    for pat in patterns:
        hit = False
        for jid in fnmatch.filter(pend, pat):
            hit = True
            if jid in done:
                continue
            if not dry_run:
                cancelled.mkdir(exist_ok=True)
                try:
                    os.rename(pending / f"{jid}.json", cancelled / f"{jid}.json")
                except FileNotFoundError:
                    running.append(jid)  # the daemon claimed it between the listing and the rename
                    continue
            done.append(jid)
        for jid in fnmatch.filter(act, pat):
            hit = True
            if jid not in running:
                running.append(jid)
        if not hit:
            unmatched.append(pat)
    return done, running, unmatched


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs", nargs="+", help="job id or fnmatch glob (e.g. 'arteval_RM_Surrik_*')")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    done, running, unmatched = cancel(Path(require()), a.jobs, a.dry_run)
    verb = "would cancel" if a.dry_run else "cancelled"
    for j in done:
        print(f"{verb}: {j}")
    for j in running:
        print(f"RUNNING (not cancelled; a worker holds it): {j}")
    for p in unmatched:
        print(f"no pending or active job matches: {p}")
    if running:
        return 3
    return 0 if done else 2


if __name__ == "__main__":
    sys.exit(main())
