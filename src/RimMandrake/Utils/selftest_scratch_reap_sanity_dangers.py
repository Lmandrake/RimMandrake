#!/usr/bin/env python3
"""Selftest: every shipped scratch-reap sanity line names the danger it guards (OPS_SCRATCH_DIRT_MEASURE_AT_START_SANF).

CLAUDE.md, No limit without the danger it guards: a line that cannot name its danger and the evidence for it is removed.
The instance: from 2026-11-23 to 2026-11-25 the sanity alarms rang about 300 times on count lines that named no danger
(selftest_stale 917 over 500, session_stale 122 over 100, refused 111 over 100, oldest_h 496.5 over 480) while / stood at
57% and the disk lines (root_disk_pct, refused_gb, rm_scratch_gb) read clear. Each line in scratch_reap_sanity.json
"start" and "end" must have an entry in "_dangers" that names the danger and its evidence; an entry with no line is stale.
"""
import json
import sys
from pathlib import Path

LINES = Path(__file__).resolve().with_name("scratch_reap_sanity.json")
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main() -> int:
    d = json.loads(LINES.read_text())
    dangers = d.get("_dangers") or {}
    keys = set()
    for phase in ("start", "end"):
        for key in d.get(phase) or {}:
            keys.add(key)
            text = dangers.get(key)
            check(isinstance(text, str) and len(text.split()) >= 6, "%s line %s names its danger and evidence in _dangers" % (phase, key))
    for key in dangers:
        check(key in keys, "_dangers entry %s has a line (a danger with no line is stale text)" % key)
    print("selftest_scratch_reap_sanity_dangers: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
