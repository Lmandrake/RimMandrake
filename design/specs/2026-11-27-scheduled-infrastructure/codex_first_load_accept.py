#!/usr/bin/env python3
"""codex_first_load_accept.py: the outcome check of the Codex route's first load.

Item RIMMANDRAKE_REVIEW_NEW_SCRIPTS_THROUGH_CODEX_EIGHTY_THREE_UNREAD (filed by
RIMMANDRAKE_READY_ALL_SCHEDULED_INFRASTRUCTURE_HE_SAID_MAX_SPEED). The list `codex_first_load.txt` beside this file
holds the pipeline-machinery scripts (pipeline_files of src/RimMandrake/Utils/pipeline_tests.json, .py, not selftests)
that origin/main added from 2026-11-19 7:40 PM to 2026-11-26 9:03 PM PST and that still existed on 2026-11-27.

    python3 design/specs/2026-11-27-scheduled-infrastructure/codex_first_load_accept.py

Exit 0 (holds): each listed file has a review record on its present bytes (`code_review_status.py check --record` reads
CLEAN), is FLAGGED (nobody reviews it again), or no longer exists (a deleted file needs no read). Exit 1 (fails): one or
more files lack it; each is printed. Exit 2: could not look (the record or the flags could not be read).
One batched `check --record` call (about 0.4 s for 103 files, measured 2026-11-27), so the lane may run it every beat.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
LIST = os.path.join(HERE, "codex_first_load.txt")
CRS = os.path.join(REPO, "src", "RimMandrake", "Utils", "code_review_status.py")


def main():
    try:
        paths = [ln.strip() for ln in open(LIST, encoding="utf-8") if ln.strip() and not ln.startswith("#")]
    except OSError as e:
        print("could not look: the list %s: %s" % (LIST, e))
        return 2
    present = [p for p in paths if os.path.exists(os.path.join(REPO, p))]
    if not present:
        print("HOLDS: none of the %d listed files exists any longer" % len(paths))
        return 0
    try:
        r = subprocess.run([sys.executable, CRS, "check", "--record"] + present, cwd=REPO, capture_output=True,
                           text=True, timeout=600)   # hang guard: one batched call took 0.4 s on 2026-11-27
    except (OSError, subprocess.SubprocessError) as e:
        print("could not look: check --record: %s" % e)
        return 2
    rows = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    if len(rows) < len(present):
        print("could not look: check --record printed %d rows for %d files (rc %s): %s"
              % (len(rows), len(present), r.returncode, (r.stderr or "").strip()[:300]))
        return 2
    import fresh_reader
    owed = []
    for ln in rows:
        state, _, rest = ln.partition("  ")
        rel = rest.split("  ")[0].strip()
        if state == "CLEAN":
            continue
        try:
            if fresh_reader.flag_kind(rel):
                continue
        except OSError as e:
            print("could not look: the flags of %s: %s" % (rel, e))
            return 2
        owed.append(ln)
    if owed:
        print("FAILS: %d of %d listed files have no review record on their present bytes and no flag:"
              % (len(owed), len(present)))
        for ln in owed:
            print("    " + ln)
        return 1
    print("HOLDS: each of the %d listed files that exist has a review record or a flag" % len(present))
    return 0


if __name__ == "__main__":
    sys.exit(main())
