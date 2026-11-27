#!/usr/bin/env python3
"""Outcome check of RIMMANDRAKE_SORT_KNOCKBACK_LANE_FAILS_ARCHBIG_PASSES_SAME_CHECKS: the SteveDesktop lane decides
sc_pawn_arc and sc_pit_fetch.

Exit 0 when one done SteveDesktop lane job of ExplosiveKnockback, on its proof build, from a source sha that holds the
fix commit (FIX below), reads PASS on both rows. Exit 1 when the queue was read and no such job exists (each candidate
job is printed with its verdicts). Exit 2 when the queue could not be read (no done/ folder, or git cannot answer the
ancestry).

    python3 design/concepts/ExplosiveKnockback/version/in_game/road_back_2026-11-25/scripts/lane_decides_pawn_arc_pit_fetch.py
"""
import glob
import json
import os
import subprocess
import sys

FIX = "11fffbf13b626ee7af05e830a1fec578cf6734fc"   # ResumeHaul waits for a stack still in flight; sc_pawn_arc reads it
ROWS = ("sc_pawn_arc", "sc_pit_fetch")
QHOME = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 7))


def holds_fix(sha):
    """True / False, or None when git cannot answer (the sha is unknown here)."""
    r = subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", FIX, sha], capture_output=True)
    return True if r.returncode == 0 else False if r.returncode == 1 else None


def main():
    done = os.path.join(QHOME, "done")
    if not os.path.isdir(done):
        print("COULD NOT LOOK: no queue folder %s" % done)
        return 2
    seen, unknown = 0, 0
    for path in sorted(glob.glob(os.path.join(done, "J*.json"))):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        job = d.get("job") or {}
        if job.get("mod") != "ExplosiveKnockback" or job.get("lane") != "stevedesktop" \
                or "ExplosiveKnockback" not in (job.get("proof_build") or []):
            continue
        rows = {r.get("row"): r.get("verdict") for r in ((d.get("result") or {}).get("rows") or [])}
        if not all(k in rows for k in ROWS):
            continue
        fix = holds_fix(job.get("source_sha") or "")
        if fix is None:
            unknown += 1
            continue
        if not fix:
            continue
        seen += 1
        verdicts = " ".join("%s=%s" % (k, rows[k]) for k in ROWS)
        print("%s source %s: %s" % (job.get("id"), (job.get("source_sha") or "")[:10], verdicts))
        if all(rows[k] == "PASS" for k in ROWS):
            print("HOLDS: the lane decides both rows PASS on the proof build of a sha that holds %s" % FIX[:10])
            return 0
    if seen == 0 and unknown:
        print("COULD NOT LOOK: %d candidate job(s) with a source sha git does not know here" % unknown)
        return 2
    print("NOT YET: %d lane job(s) on a sha with the fix, none PASS on both rows" % seen)
    return 1


if __name__ == "__main__":
    sys.exit(main())
