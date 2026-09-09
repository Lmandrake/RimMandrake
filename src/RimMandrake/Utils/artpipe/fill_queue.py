#!/usr/bin/env python3
"""fill_queue.py — turn an art-list CSV/JSON into artpipe job files.

Reads rows describing art to (re)generate and writes one job JSON per row per
facing into `infrastructure/artpipe/pending/` (ART_PIPELINE_DAEMON_1,
deliverable 4) — the only writer of that directory a human is meant to run by
hand; the daemon's claim (atomic rename to `active/`) never touches it.

CSV columns (JSON: same keys; `facings` may be a JSON list there):
    id                 base id — one job file per facing gets "<id>_<facing>"
                       (bare "<id>" if facings is empty)
    rimflow_item_id    provenance — which ledger item this art serves
    prompt             the generation instruction
    canvas_w, canvas_h pixels the worker must generate at
    reference          optional — path to the existing sprite this reskins;
                       blank means new art, no --image on the worker
    facings            optional — comma/semicolon-separated (CSV) or a list
                       (JSON); empty means one job named bare "<id>"
    style_notes        optional — free text, folded into the prompt
    priority           optional int, default 100 — LOWER claims sooner
    background         optional, default "transparent"

Refuses a duplicate job id — checked against pending/active/done/failed all
at once, so an id already claimed, finished or failed is exactly as
protected as one still waiting. The check-then-create has an O_EXCL backstop
on the actual pending/ write, for the same reason claim_next() in
artpiped.py relies on rename atomicity rather than a check-then-act pair.

    python3 fill_queue.py --input art_list.csv
    python3 fill_queue.py --input art_list.json --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

REQUIRED_ROW_FIELDS = ("id", "rimflow_item_id", "prompt", "canvas_w", "canvas_h")


class DuplicateJobId(ValueError):
    pass


def _split_facings(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(f).strip() for f in raw if str(f).strip()]
    raw = str(raw).strip()
    if not raw:
        return []
    return [f.strip() for f in raw.replace(";", ",").split(",") if f.strip()]


def load_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            data = data.get("items") or data.get("rows") or []
        return list(data)
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def row_to_jobs(row: dict) -> list[dict]:
    missing = [f for f in REQUIRED_ROW_FIELDS if not row.get(f)]
    if missing:
        raise ValueError(f"row {row.get('id', '?')!r} missing {missing}")

    base_id = str(row["id"]).strip()
    facings = _split_facings(row.get("facings"))
    canvas = {"width": int(row["canvas_w"]), "height": int(row["canvas_h"])}
    reference = row.get("reference") or None
    if reference:
        reference = str(reference).strip() or None

    jobs = []
    for facing in (facings or [None]):
        job_id = f"{base_id}_{facing}" if facing else base_id
        jobs.append({
            "id": job_id,
            "rimflow_item_id": row["rimflow_item_id"],
            "reference": reference,
            "canvas": canvas,
            "prompt": row["prompt"],
            "style_notes": row.get("style_notes") or "",
            "priority": int(row.get("priority", 100)),
            "background": row.get("background") or "transparent",
            "facing": facing,
            "facings": facings,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
    return jobs


def write_job(job: dict, pending_dir: Path, active_dir: Path, done_dir: Path,
              failed_dir: Path, dry_run: bool) -> None:
    taken = common.id_taken(job["id"], pending_dir, active_dir, done_dir, failed_dir)
    if taken:
        raise DuplicateJobId(f"{job['id']} already exists at {taken}")

    dest = pending_dir / f"{job['id']}.json"
    if dry_run:
        print(f"would write {dest}")
        return

    fd = os.open(str(dest), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(fd, (json.dumps(job, indent=2, sort_keys=True) + "\n").encode())
    finally:
        os.close(fd)
    print(f"filed {dest}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", required=True, help="CSV or JSON art list")
    ap.add_argument("--pending-dir", type=Path, default=common.DEFAULT_PENDING)
    ap.add_argument("--active-dir", type=Path, default=common.DEFAULT_ACTIVE)
    ap.add_argument("--done-dir", type=Path, default=common.DEFAULT_DONE)
    ap.add_argument("--failed-dir", type=Path, default=common.DEFAULT_FAILED)
    ap.add_argument("--dry-run", action="store_true",
                     help="print what would be filed, write nothing")
    args = ap.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"ERROR no such input: {path}", file=sys.stderr)
        return 2

    if not args.dry_run:
        # fill_queue only ever writes pending/ — active/done/failed/ are read
        # here purely for the duplicate-id check, so only pending/ needs to
        # exist before we can write to it.
        for d in (args.pending_dir, args.active_dir, args.done_dir, args.failed_dir):
            d.mkdir(parents=True, exist_ok=True)

    rows = load_rows(path)
    filed, duplicates, errors = 0, [], []
    for row in rows:
        try:
            jobs = row_to_jobs(row)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for job in jobs:
            try:
                write_job(job, args.pending_dir, args.active_dir, args.done_dir,
                          args.failed_dir, args.dry_run)
                filed += 1
            except DuplicateJobId as exc:
                duplicates.append(str(exc))

    for msg in errors:
        print(f"ERROR skipped row: {msg}", file=sys.stderr)
    for msg in duplicates:
        print(f"REFUSED duplicate: {msg}", file=sys.stderr)

    print(f"\n{filed} job(s) filed, {len(duplicates)} duplicate(s) refused, "
          f"{len(errors)} row error(s)")
    return 1 if (duplicates or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
