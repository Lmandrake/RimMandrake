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
                       blank means new art, no --image on the worker.
                       VERIFIED to exist at filing time and stored ABSOLUTE
                       — a dangling reference is refused here rather than
                       surfacing later as a validate_sprite.py exit-2 the
                       daemon has to distinguish from a real art rejection.
    facings            optional — comma/semicolon-separated (CSV) or a list
                       (JSON); empty means one job named bare "<id>"
    style_notes        optional — free text, folded into the prompt
    priority           optional int, default 100 — LOWER claims sooner.
                       A blank CSV cell reads as '' (not a missing key) and
                       is treated the same as absent, not as int('').
    background         optional, default "transparent"
    channel            optional per-row override — "codex" or "gemini".
                       Every row otherwise gets --channel's value
                       (default "codex"); see GEMINI_WORKER_BACKEND_1.

Refuses a duplicate job id — checked against pending/active/done/failed all
at once, so an id already claimed, finished or failed is exactly as
protected as one still waiting. The write itself goes to a tmp file first,
then `os.link()`s it into pending/ — the same exclusivity an O_EXCL create
would give, but without ever leaving a partially-written file sitting at
the real path if this process is killed mid-write (that used to be able to
permanently block the id: a corrupt file at `dest` is still a file `dest`
has, so id_taken() would refuse every future refile of it).

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


def row_to_jobs(row: dict, default_channel: str = "codex") -> list[dict]:
    missing = [f for f in REQUIRED_ROW_FIELDS if not row.get(f)]
    if missing:
        raise ValueError(f"row {row.get('id', '?')!r} missing {missing}")

    # A per-row "channel" always wins over --channel, if the row bothers to
    # name one; otherwise every row in this invocation gets --channel's
    # value (default "codex").
    channel = str(row.get("channel") or default_channel).strip() or default_channel
    if channel not in ("codex", "gemini"):
        raise ValueError(f"row {row.get('id', '?')!r} has unknown channel "
                          f"{channel!r} — only 'codex' or 'gemini'")

    base_id = str(row["id"]).strip()
    facings = _split_facings(row.get("facings"))
    canvas = {"width": int(row["canvas_w"]), "height": int(row["canvas_h"])}

    reference = row.get("reference") or None
    if reference:
        reference = str(reference).strip() or None
    if reference:
        # Stored ABSOLUTE, and verified to exist here at filing time rather
        # than left to fail inside the daemon later — a dangling reference
        # used to reach validate_sprite.py as a plain nonzero exit, which
        # the daemon folded into the same REJECT as a genuinely bad image
        # (fixed separately in artpiped.py's run_validator; this is the
        # OTHER half of that fix: catch it before the job is even filed).
        ref_path = Path(reference).expanduser()
        if not ref_path.is_absolute():
            ref_path = (Path.cwd() / ref_path)
        if not ref_path.is_file():
            raise ValueError(f"row {base_id!r} reference does not exist: {ref_path}")
        reference = str(ref_path.resolve())

    # csv.DictReader gives '' (not a missing key) for a blank cell, and
    # int('') raises — `row.get('priority') or 100` treats a blank cell the
    # same as an absent one instead of crashing the whole file.
    priority = int(row.get("priority") or 100)

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
            "priority": priority,
            "background": row.get("background") or "transparent",
            "channel": channel,
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

    # Write to a tmp name FIRST, fully, then os.link() it into place. A
    # direct O_EXCL create-and-write at `dest` itself leaves a PARTIALLY
    # WRITTEN file sitting at the real path if this process is killed
    # mid-write — and that corrupt file then blocks every future refile of
    # this id forever (id_taken() sees it and refuses, common.load_job()
    # can't parse it). os.link fails with FileExistsError if dest already
    # exists — the same exclusivity O_EXCL gave — but only after the
    # content is already complete and closed, so a crash between link and
    # cleanup can only ever leave a fully-valid dest.
    tmp = pending_dir / f".{job['id']}.json.tmp.{os.getpid()}.{time.time_ns()}"
    tmp.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n")
    try:
        os.link(tmp, dest)
    except FileExistsError:
        raise DuplicateJobId(f"{job['id']} already exists at {dest} "
                              f"(created concurrently by another filer)")
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
    print(f"filed {dest}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", required=True, help="CSV or JSON art list")
    ap.add_argument("--pending-dir", type=Path, default=common.DEFAULT_PENDING)
    ap.add_argument("--active-dir", type=Path, default=common.DEFAULT_ACTIVE)
    ap.add_argument("--done-dir", type=Path, default=common.DEFAULT_DONE)
    ap.add_argument("--failed-dir", type=Path, default=common.DEFAULT_FAILED)
    ap.add_argument("--channel", choices=("codex", "gemini"), default="codex",
                     help="default channel for every row in this file — a row's own "
                          "'channel' column/field, if present, overrides this")
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
            jobs = row_to_jobs(row, default_channel=args.channel)
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
