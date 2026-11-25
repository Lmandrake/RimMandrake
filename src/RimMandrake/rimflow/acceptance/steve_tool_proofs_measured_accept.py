#!/usr/bin/env python3
"""steve_tool_proofs_measured_accept.py - the outcome check of RIMMANDRAKE_PUT_STEVEDESKTOP_ON_NON_MOD_WORK_ALL_DAY_HE_ASKED.

The need: the tool-ticket live proofs sent to the SteveDesktop lane measure their tickets. On 2026-11-24 seven of them
came back with no reading: five voided by the lane (a stale swap marker on Steve2: LOAD; a stale companion: DEPLOY) and
two blind by a wrong check (Beskar read Steve1's probe file; the alloc probe ran under WSL Python, which cannot reach
the bridge; fixed at 9dc47e435f). They were asked again at 2026-11-25 8:34 AM PST.

For each item below, the check holds when a testq done record for it, finished after SINCE, ran on a SteveDesktop game
with no lane cause and at least one PASS or FAIL row. UNMEASURED, a lane cause, or no record yet is not measured.
Reads the queue at $TESTQ_QUEUE (default D:\\ClaudeWork\\rimmandrake\\testq). Exit 0: every item measured; 1: not yet;
2: the queue could not be read (could not look). Base 2026-11-25 8:40 AM PST: 0/7, exit 1.
"""
import glob
import json
import os
import sys

SINCE = "2026-11-25T16:30:00Z"
ITEMS = ("BESKARPROBE_FIX_EIGHTEEN_POKES_NO_NET", "MONO_ALLOC_MEASURE_PER_TICK_ON_GAME",
         "WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF", "VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL",
         "MAP_AWARENESS_PROVE_ON_A_QUIET_MAP", "TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS", "ART_RESOLUTION_MEASURE_AT_MAX_ZOOM")


def verdict(rec):
    """-> 'measured' | a short reason it is not."""
    r = rec.get("result") or {}
    host = str(rec.get("host") or r.get("host") or "")
    if not host.startswith("stevedesktop"):
        return "not on SteveDesktop (%s)" % (host or "no host")
    if r.get("cause"):
        return "lane cause %s" % r.get("cause")
    c = r.get("counts") or {}
    if c.get("PASS") or c.get("FAIL"):
        return "measured"
    return "no PASS or FAIL row (%s)" % (c or "no rows")


def main(argv):
    done = os.path.join(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"), "done")
    if not os.path.isdir(done):
        print("COULD NOT LOOK: no testq done folder at %s" % done)
        return 2
    best = {i: "no record finished after %s" % SINCE for i in ITEMS}
    for f in glob.glob(os.path.join(done, "J2026*.json")):
        try:
            rec = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        item = (rec.get("job") or {}).get("item")
        if item not in best or str(rec.get("finished") or "") <= SINCE or best[item] == "measured":
            continue
        best[item] = verdict(rec)
    n = sum(v == "measured" for v in best.values())
    for i in ITEMS:
        print("%s %s: %s" % ("ok  " if best[i] == "measured" else "FAIL", i, best[i]))
    print("%d/%d measured" % (n, len(ITEMS)))
    return 0 if n == len(ITEMS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
