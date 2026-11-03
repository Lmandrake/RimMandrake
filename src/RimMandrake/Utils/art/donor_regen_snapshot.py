#!/usr/bin/env python3
"""donor_regen_snapshot.py — prove DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO's verify clauses without the live artpipe.

The artpipe queue lives under the agent data root (RM_DATA_ROOT/artpipe), which a clean export cannot see. So:

  take   reads the live artpipe (needs RM_DATA_ROOT) and writes a committed snapshot of every dregen_ id per state:
         job stems in pending/active/done/failed (as donor_regen_jobs.queue_view counts them) and the ids of
         failed/dregen_*.manifest.json.
  check  offline, from the committed snapshot alone:
           1. every row of the job list is filed (one of its ids, or one per facing, is in a state) -> prints
              'every row already filed' — the same rule submit_one uses to skip a row;
           2. every failed manifest id is back in pending/active/done, or listed in the failures file ->
              prints 'failed: every id retried or listed'.
         Exit 0 only when both hold. A snapshot with no dregen_ ids at all is refused as a blind instrument.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
D = REPO / "design/RimMandrake"
JOBS = D / "donor_regen_jobs_2026-10-18.json"
FAILS = D / "donor_regen_failures_2026-11-03.json"
SNAP = D / "donor_regen_queue_snapshot_2026-11-03.json"
STATES = ("pending", "active", "done", "failed")
PREFIX = "dregen_"


def take(out: Path) -> int:
    root = os.environ.get("RM_DATA_ROOT")
    if not root:
        print("RM_DATA_ROOT is unset: take reads the live artpipe", file=sys.stderr)
        return 2
    art = Path(root) / "artpipe"
    snap = {"what": "dregen_ ids per artpipe state, read by donor_regen_snapshot.py take",
            "taken": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "item": "DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO", "jobs": {}, "failed_manifests": []}
    for st in STATES:
        d = art / st
        if not d.is_dir():
            print(f"missing artpipe state dir {d}", file=sys.stderr)
            return 2
        names = [f.name for f in d.iterdir()]
        snap["jobs"][st] = sorted(n[:-5] for n in names if n.startswith(PREFIX) and n.endswith(".json")
                                  and not n.endswith(".manifest.json"))
        if st == "failed":
            snap["failed_manifests"] = sorted(n[:-len(".manifest.json")] for n in names
                                              if n.startswith(PREFIX) and n.endswith(".manifest.json"))
    snap["counts"] = {st: len(v) for st, v in snap["jobs"].items()} | {"failed_manifests": len(snap["failed_manifests"])}
    out.write_text(json.dumps(snap, indent=1) + "\n")
    print(f"wrote {out}: {snap['counts']}")
    return 0


def check(snap_p: Path, jobs_p: Path, fails_p: Path) -> int:
    snap = json.loads(snap_p.read_text())
    filed = {i for st in STATES for i in snap["jobs"][st]}
    if not filed:
        print(f"BLIND: {snap_p.name} holds no dregen_ ids at all — refusing to call that a pass")
        return 1
    rows = json.loads(jobs_p.read_text())["rows"]
    unfiled = []
    for r in rows:
        ids = [r["id"]] if not r["facings"] else [f"{r['id']}_{f}" for f in r["facings"]]
        if not any(i in filed for i in ids):
            unfiled.append(r["id"])
    print(f"snapshot {snap.get('taken')}: {snap.get('counts')}; job list {jobs_p.name}: {len(rows)} rows")
    ok = True
    if unfiled:
        ok = False
        print(f"UNFILED {len(unfiled)} rows: {', '.join(unfiled[:20])}")
    else:
        print("every row already filed")
    retried = {i for st in ("pending", "active", "done") for i in snap["jobs"][st]}
    listed = {r["id"] for r in json.loads(fails_p.read_text())["rows"]}
    loose = [i for i in snap["failed_manifests"] if i not in retried and i not in listed]
    if loose:
        ok = False
        print(f"FAILED NEITHER RETRIED NOR LISTED {len(loose)}: {', '.join(loose[:20])}")
    else:
        print(f"failed: every id retried or listed ({len(snap['failed_manifests'])} failed manifests, "
              f"{len(listed)} listed)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("take")
    t.add_argument("--out", type=Path, default=SNAP)
    c = sub.add_parser("check")
    c.add_argument("--snapshot", type=Path, default=SNAP)
    c.add_argument("--jobs", type=Path, default=JOBS)
    c.add_argument("--failures", type=Path, default=FAILS)
    a = ap.parse_args()
    return take(a.out) if a.cmd == "take" else check(a.snapshot, a.jobs, a.failures)


if __name__ == "__main__":
    sys.exit(main())
