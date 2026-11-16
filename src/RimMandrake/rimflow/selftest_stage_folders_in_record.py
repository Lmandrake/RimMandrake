#!/usr/bin/env python3
"""selftest_stage_folders_in_record.py -- no mod carries a Stage 6 visit folder past its stage record.

Only the Stage 6 driver opens a visit (a move into in_game in stage_record.json); a Test Pilot or fixer working a
road-back item during visit N writes its evidence inside visit_N/ (e.g. visit_N/pilot_<what>/), never a new visit_N+1/.
A visit folder past the record makes maturation.ingame_facts block the mod ("visit folder(s) [k] are past the record's
visit n") and the Dispatcher pauses it for good. Measured 2026-11-16: ExplosiveKnockback stood paused ~3 h on a Test
Pilot's visit_4/ written during visit 3 (item RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING).

Part one proves the reader on fixtures (it sees a past folder, passes an in-record one); part two reads the real tree.
Exit 0 = PASS. Runs in ./publish's tree checks (publish_tree_checks.json).
"""
import os
import sys
import tempfile
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def past_visits(root, mod):
    """-> the visit folder numbers past the record's visit count (max 1, as ingame_facts reads it); [] without a record."""
    rec = M.load(root, mod)
    if not isinstance(rec, dict):
        return []
    n = max(1, len(M.ingame_openings(rec)))
    return [k for k in M.visit_numbers(root, mod) if k > n]


def violations(root):
    d = os.path.join(root, "design", "concepts")
    out = []
    for mod in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        past = past_visits(root, mod)
        if past:
            out.append("%s: visit folder(s) %s past the record's visit %d (design/concepts/%s/version/in_game/); "
                       "move the evidence inside the open visit's folder" % (
                           mod, past, max(1, len(M.ingame_openings(M.load(root, mod)))), mod))
    return out


def fixture(visits, openings):
    t = tempfile.mkdtemp(prefix="stagefolders_")
    v = os.path.join(t, "design", "concepts", "Fx", "version")
    for k in visits:
        os.makedirs(os.path.join(v, "in_game", "visit_%d" % k))
    rec = {"stage": "in_game", "moves": [{"to": "in_game", "at": "2026-11-16T0%d:00:00" % i} for i in range(openings)]
           + [{"to": "offline_build"}]}
    with open(os.path.join(v, "stage_record.json"), "w") as f:
        json.dump(rec, f)
    return t


def main():
    fails = []
    if not violations(fixture([1, 2, 3, 4], 3)):
        fails.append("fixture: visit_4 with 3 openings was not seen")
    if violations(fixture([1, 2, 3], 3)):
        fails.append("fixture: visits 1-3 with 3 openings were refused")
    if violations(fixture([1], 0)):
        fails.append("fixture: visit_1 with no opening yet was refused (ingame_facts reads visit 1)")
    real = violations(ROOT)
    fails += real
    for f in fails:
        print("FAIL " + f)
    print("%s: stage folders in record (%d finding(s))" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
