#!/usr/bin/env python3
"""desert_port_coverage.py — where every render of the 2026-09-20 desert-port wave stands (DESERT_ART_SHEET_REBUILD_DECAYED_UNSEEN).

The wave's verdict sheet (Transient/desert_art_verdict_2026-09-20) decayed unseen. Rebuilding it over all 109 jobs would
re-ask what the owner already ruled: he purged most of them on the 2026-10-04 desert sheets. This accounts for every job
from committed files only (no artpipe or D:\\ClaudeWork read), so a walled checker can rerun it:

    python3 src/RimMandrake/Utils/art/desert_port_coverage.py            # the table
    python3 src/RimMandrake/Utils/art/desert_port_coverage.py --check    # exit 1 unless every job is accounted for

Each job is, in this order of precedence:
  owner_ruled   an art-ledger event by the owner on its picture (purge or rejected)
  no_bytes      no art-ledger variant event for the job: its picture never reached the art store, nothing to show
  this_sheet    its render family is a column on the rebuilt sheet (SHEET_ID's snapshot)
  other_sheet   its render family is a column on another sheet built on or after CURRENT_FROM
  UNCOVERED     none of these: the check fails
--check also fails if the rebuilt sheet's snapshot or decisions file is missing, or if it holds a row whose render
families are all owner_ruled (that row would re-ask a ruling)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
JOBS = ROOT / "infrastructure/state/art/desert_port_jobs_2026-09-20.json"
EVENTS = ROOT / "infrastructure/state/art/events"
SHEETS = ROOT / "infrastructure/state/art/sheets"
SHEET_ID = "desert_art_verdict_sheet_2026-11-05"
DECISIONS = ROOT / "Transient/biome_ffar" / f"{SHEET_ID}.decisions.json"
CURRENT_FROM = "2026-11-03"
OWNER_RULINGS = {"purge", "rejected"}
FACING = re.compile(r"_(south|east|north|west)$")
SHEET_DATE = re.compile(r"_sheet_(\d{4}-\d{2}-\d{2})\.snapshot\.json$")


def family(job: str) -> str:
    return FACING.sub("", job)


def ledger(jobs: set[str]) -> tuple[dict, dict]:
    """(job -> picture sha, sha -> set of owner ruling types) from every committed art event shard, archive included."""
    events = []
    for f in sorted(EVENTS.rglob("*.jsonl")):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                continue
    sha_of = {e["job"]: e["sha"] for e in events
              if e.get("kind") == "artpipe" and e.get("job") in jobs and e.get("sha")}
    shas = set(sha_of.values())
    ruled: dict = {}
    for e in events:
        if e.get("sha") in shas and e.get("by") == "owner" and e.get("type") in OWNER_RULINGS:
            ruled.setdefault(e["sha"], set()).add(e["type"])
    return sha_of, ruled


def families_on(snapshot: Path) -> dict:
    """row -> set of render families shown as columns (labels read 'render <family>')."""
    rows = json.loads(snapshot.read_text()).get("rows") or {}
    return {k: {lab.split(" ", 1)[1] for lab in (v.get("labels") or {}).values() if lab.startswith("render ")}
            for k, v in rows.items()}


def census() -> dict:
    spec = json.loads(JOBS.read_text())
    jobs = list(spec["jobs"])
    sha_of, ruled = ledger(set(jobs))
    this = SHEETS / f"{SHEET_ID}.snapshot.json"
    this_rows = families_on(this) if this.exists() else {}
    this_fams = set().union(*this_rows.values()) if this_rows else set()
    other: dict = {}
    for snap in SHEETS.glob("*_sheet_*.snapshot.json"):
        m = SHEET_DATE.search(snap.name)
        if not m or m.group(1) < CURRENT_FROM or snap.name.startswith(SHEET_ID):
            continue
        for fams in families_on(snap).values():
            for fam in fams:
                other.setdefault(fam, set()).add(snap.name.replace(".snapshot.json", ""))
    out = {}
    for j in jobs:
        sha = sha_of.get(j)
        if sha and sha in ruled:
            out[j] = ("owner_ruled", ",".join(sorted(ruled[sha])))
        elif not sha:
            out[j] = ("no_bytes", "no art-ledger variant event")
        elif family(j) in this_fams:
            out[j] = ("this_sheet", SHEET_ID)
        elif family(j) in other:
            out[j] = ("other_sheet", ",".join(sorted(other[family(j)])))
        else:
            out[j] = ("UNCOVERED", "")
    # a row of the rebuilt sheet whose desert-port families are all owner-ruled would re-ask his ruling
    stale_rows = []
    for row, fams in this_rows.items():
        dp = {f for f in fams if f.startswith("desertportb_")}
        if dp and all(out.get(j, ("",))[0] == "owner_ruled" for j in jobs if family(j) in dp):
            stale_rows.append(row)
    return {"jobs": out, "sheet_exists": this.exists(), "decisions_exists": DECISIONS.exists(),
            "this_rows": sorted(this_rows), "stale_rows": stale_rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 unless every job is accounted for")
    a = ap.parse_args()
    c = census()
    counts: dict = {}
    for j, (cls, why) in sorted(c["jobs"].items()):
        counts[cls] = counts.get(cls, 0) + 1
        if not a.check or cls in ("UNCOVERED", "no_bytes", "this_sheet", "other_sheet"):
            print(f"{cls:12} {j}  {why}")
    print(f"jobs={len(c['jobs'])} " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"sheet {SHEET_ID}: snapshot={'yes' if c['sheet_exists'] else 'MISSING'} "
          f"decisions={'yes' if c['decisions_exists'] else 'MISSING'} rows={','.join(c['this_rows'])}")
    bad = []
    if counts.get("UNCOVERED"):
        bad.append(f"{counts['UNCOVERED']} job(s) on no sheet and unruled")
    if not c["sheet_exists"] or not c["decisions_exists"]:
        bad.append("rebuilt sheet snapshot/decisions missing")
    if not counts.get("this_sheet"):
        bad.append("no job is on the rebuilt sheet")
    if c["stale_rows"]:
        bad.append(f"rows re-asking an owner ruling: {c['stale_rows']}")
    if len(c["jobs"]) != 109:
        bad.append(f"job list holds {len(c['jobs'])}, not the wave's 109")
    if a.check:
        print("COVERAGE " + ("OK" if not bad else "FAIL: " + "; ".join(bad)))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
