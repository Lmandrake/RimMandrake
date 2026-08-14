#!/usr/bin/env python3
"""capture_manifest.py — preserve the def dump's PROVENANCE, not its bulk.

A full def dump is ~1.3 GB (ThingDef.json alone is 817 MB) and costs a ~23-minute
cold load to produce. It must never be committed: one file past GitHub's 100 MB
limit hard-fails the push for every seat and stays failed until it is rewritten
out of history. But it is also *regenerable by definition* — reproducing it is
exactly what a game load does — so losing it costs a rerun, not a recreation.

`manifest.json` is the opposite case. At ~144 KB it is the only record of what the
game **actually loaded**: every mod's load order, packageId and rootDir, plus per
def-type counts. Nothing regenerates it except the load it describes, and once the
next load overwrites it that stack is unanswerable forever.

So: commit the provenance, discard the bulk.

    python3 observed/2026-08-13/dumps/capture_manifest.py            # capture the live manifest
    python3 observed/2026-08-13/dumps/capture_manifest.py --check    # report only, write nothing

Files land as `manifest.<modCount>.<capturedUtc date>.json`, which is
self-describing and cannot silently collide with a different run.

Exit codes: 0 captured (or --check and current), 1 nothing to capture, 2 refused.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# Both spellings, because this repo is driven from Windows python.exe AND from
# WSL python3 and the two see the same directory under different roots. Guessing
# one of them is how a capture step silently becomes a no-op.
CANDIDATES = [
    r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
    r"\RimWorld by Ludeon Studios\DefDump",
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios"
    "/RimWorld by Ludeon Studios/DefDump",
]


def find_dump() -> str | None:
    for path in CANDIDATES:
        if os.path.isdir(path):
            return path
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report what would be captured; write nothing")
    args = ap.parse_args()

    dump = find_dump()
    if dump is None:
        print("no DefDump directory found. Roots tried:")
        for c in CANDIDATES:
            print("   MISSING  %s" % c)
        return 1

    src = os.path.join(dump, "manifest.json")
    if not os.path.exists(src):
        print("no manifest.json in %s" % dump)
        print("The dump has never run, or ran without writing one. Arm it with:")
        print('   echo all > "%s"' % os.path.join(dump, "dump_request.txt"))
        return 1

    # utf-8-sig: RimWorld writes these with a BOM often enough that a bare
    # utf-8 read fails on the very first character, which reads like corruption.
    with open(src, encoding="utf-8-sig") as fh:
        man = json.load(fh)

    count = man.get("modCount", "?")
    captured = str(man.get("capturedUtc", "unknown"))
    date = captured.split("T")[0] if "T" in captured else "unknown"
    version = man.get("gameVersion", "?")
    defs = man.get("defCounts") or {}

    name = "manifest.%s.%s.json" % (count, date)
    dst = os.path.join(HERE, name)

    print("live dump   %s" % dump)
    print("  captured  %s   game %s" % (captured, version))
    print("  mods      %s        def types %d" % (count, len(defs)))
    print("  -> %s" % name)

    if os.path.exists(dst):
        same = os.path.getsize(dst) == os.path.getsize(src)
        print("  already captured%s" % ("" if same else " — SIZE DIFFERS, not overwriting"))
        return 0 if same else 2

    if args.check:
        print("  (--check: nothing written)")
        return 0

    shutil.copy2(src, dst)
    print("  captured %d bytes" % os.path.getsize(dst))
    print("\nCommit it — that is the whole point:")
    print("   git add observed/2026-08-13/dumps/%s && git commit -- observed/2026-08-13/dumps/%s && git push"
          % (name, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
