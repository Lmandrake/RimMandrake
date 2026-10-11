#!/usr/bin/env python3
"""Repair a torn FINAL line in an art-ledger events shard (live or archive).

WHY: `infrastructure/state/art/events/**` is append-only. A crashed append can still leave a
half-written last line, and `artledger.read_events()` refuses to skip it. This is the sanctioned repair
(same family as `Utils/repair_torn_ledger.py`, which handles the rimflow ledger).

WHAT IT DOES
  - scans events/*.jsonl and events/archive/*.jsonl; a line is bad when it is not valid JSON.
  - ONLY a bad FINAL non-blank line is repairable: it is truncated off the shard, and its exact
    original bytes are kept in events/_torn/<shard>.<UTC ts>.txt (never silently dropped).
  - A bad line anywhere EARLIER is mid-file corruption: reported, file left untouched, exit 1.
  - Dry run by default; --apply writes. Clean files are never touched.

    python3 src/RimMandrake/Utils/art/repair_torn_art_events.py            # report
    python3 src/RimMandrake/Utils/art/repair_torn_art_events.py --apply
    python3 .../repair_torn_art_events.py --events DIR                       # other tree (selftests)
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
EVENTS = REPO_ROOT / "infrastructure" / "state" / "art" / "events"
TORN = "_torn"


def shard_paths(d: Path):
    out = sorted(d.glob("*.jsonl"))
    a = d / "archive"
    if a.is_dir():
        out += sorted(p for p in a.iterdir() if p.is_file() and p.suffix == ".jsonl")
    return out


def _ok(b: bytes) -> bool:
    try:
        json.loads(b.decode("utf-8"))
        return True
    except Exception:
        return False


def analyse(path: Path):
    """-> (status, info). status: clean | torn_tail | mid_file.
    torn_tail info = (keep_len, fragment_bytes); mid_file info = [1-based line numbers]."""
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    bad = [i for i, l in enumerate(lines, 1) if l.strip() and not _ok(l)]
    if not bad:
        return "clean", None
    last = max(i for i, l in enumerate(lines, 1) if l.strip())
    if bad == [last]:
        keep = sum(len(l) for l in lines[:last - 1])
        return "torn_tail", (keep, raw[keep:])
    return "mid_file", bad


def repair(events: Path, apply: bool, stamp: str = None) -> int:
    if not events.is_dir():
        print(f"REFUSING: {events} is not a directory.")
        return 1
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rc, n_clean, n_fixed = 0, 0, 0
    for p in shard_paths(events):
        rel = p.relative_to(events).as_posix()
        status, info = analyse(p)
        if status == "clean":
            n_clean += 1
        elif status == "mid_file":
            rc = 1
            print(f"REFUSED  {rel}: invalid JSON on line(s) {info[:10]} not at the tail "
                  "(mid-file corruption) -- report only, a human must look.")
        else:
            keep, frag = info
            shown = frag[:100].decode("utf-8", "replace")
            print(f"TORN     {rel}: final fragment of {len(frag)} bytes {shown!r}")
            if not apply:
                continue
            q = events / TORN / f"{rel.replace('/', '.')}.{stamp}.txt"
            q.parent.mkdir(parents=True, exist_ok=True)
            with open(q, "xb") as fh:                 # never overwrite a quarantine
                fh.write(frag)
                fh.flush()
                os.fsync(fh.fileno())
            if q.read_bytes() != frag:
                print(f"REFUSING {rel}: quarantine did not verify, shard untouched.")
                rc = 1
                continue
            os.truncate(p, keep)
            n_fixed += 1
            print(f"REPAIRED {rel}: truncated to {keep} bytes; fragment kept at {q}")
    print(f"{n_clean} clean, {n_fixed} repaired" + ("" if apply else " (dry run; --apply to write)"))
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--events", default=str(EVENTS))
    a = ap.parse_args()
    return repair(Path(a.events), a.apply)


if __name__ == "__main__":
    sys.exit(main())
