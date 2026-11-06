#!/usr/bin/env python3
"""v3 cutover (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY): RETIRED; it only shows what it once did.

It ran once, 2026-10-29, moving BENCH's open items and the FlowWorks/GSS lane to FOUNDRY. FOUNDRY was
then retired (owner, by card 2026-11-02, "What should happen to FOUNDRY?" -> "Retire it."; CLAUDE.md
"Relentless builds and accepts everything ... FOUNDRY is retired"), so both of its writers became
harmful: `apply` would hand items to a retired seat and `revert` would hand them back to BENCH and
re-land a docs patch naming FOUNDRY as owner. Both refuse (V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL); the
staged docs patch is deleted. The record of the one run stays as history.

    python3 src/RimMandrake/rimflow/v3_cutover.py status     the record of the 2026-10-29 run
    python3 src/RimMandrake/rimflow/v3_cutover.py apply|revert|plan   refused, exit 2, with this pointer
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RECORD = os.path.join(ROOT, "infrastructure", "state", "v3_cutover", "record.json")
RETIRED = ("RETIRED: v3_cutover %s would re-assert FOUNDRY ownership, and FOUNDRY is retired (owner, by card "
           "2026-11-02). Ownership moves through `rimflow reassign`; see CLAUDE.md 'FOUNDRY is retired' and "
           "item V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL. History: %s")


def refuse(verb):
    print(RETIRED % (verb, os.path.relpath(RECORD, ROOT)), file=sys.stderr)
    return 2


def apply(*_a, **_k):
    return refuse("apply")


def revert(*_a, **_k):
    return refuse("revert")


def status(record=RECORD):
    try:
        rec = json.load(open(record))
    except (OSError, ValueError) as e:
        print("no readable record (%s): %s" % (type(e).__name__, record))
        return 1
    print("v3 cutover (retired): state %s, applied %s, moved %d, kept %d, lane seat before %s" % (
        rec.get("state"), rec.get("applied_at"), len(rec.get("moved") or []), len(rec.get("kept") or []),
        rec.get("lane_seat_before")))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    verb = argv[0] if argv else ""
    if verb in ("status", "-h", "--help", ""):
        if verb in ("-h", "--help", ""):
            print(__doc__)
            return 0 if verb else 2
        return status()
    return refuse(verb)


if __name__ == "__main__":
    sys.exit(main())
