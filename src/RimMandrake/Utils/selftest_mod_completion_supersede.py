#!/usr/bin/env python3
"""selftest_mod_completion_supersede.py -- judge_works must not paint a def broken on an item-level partial/fail
verify once the def's own newer L2 rows PASS (item COMPLETION_FIX_PARTIAL_VERIFY_PAINTS_RED: RM_Ladder, RM_PitRamp)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mod_completion as mc  # noqa: E402

LADDER = {"type": "ThingDef", "defName": "RM_Ladder", "label": "pit ladder"}


def run(rows, verifies, inv=(LADDER,)):
    runs = [{"path": "x.json", "script": s, "started": t, "level": "L2",
             "rows": [{"id": rid, "status": st, "class": "MOD", "text": f'{{"id": "{rid}", "def": "RM_Ladder"}}'}]}
            for s, rid, st, t in rows]
    return {w["defName"]: w for w in mc.judge_works(list(inv), runs, verifies, [])}


def ver(result, ts, criterion="", why="RM_Ladder could not be climbed"):
    return {"id": "WATERED_PIT_FIX_NO_WAY_IN", "criterion": criterion, "result": result, "level": "L2", "ts": ts,
            "why": why}


fails = []


def check(name, got, want):
    if got != want:
        fails.append(f"{name}: got {got!r}, want {want!r}")


# 1. item-level PARTIAL (no criterion) older than the def's own row PASS -> superseded -> works
r = run([("climb_proof", "CLIMB_ladder_prison_door", "PASS", "2026-10-29T06:00:00")],
        [ver("partial", "2026-10-24T10:00:00Z")])
check("item-level partial superseded by newer row pass", r["RM_Ladder"]["status"], "works")

# 2. the same partial NEWER than the pass -> still broken (a newer failure is news)
r = run([("climb_proof", "CLIMB_ladder_prison_door", "PASS", "2026-10-20 06:00:00")],
        [ver("partial", "2026-10-24T10:00:00Z")])
check("item-level partial newer than pass stays broken", r["RM_Ladder"]["status"], "broken")

# 3. a criterion-bound FAIL that names the def is a verdict on it -> not superseded
r = run([("climb_proof", "CLIMB_ladder_prison_door", "PASS", "2026-10-29T06:00:00")],
        [ver("fail", "2026-10-24T10:00:00Z", criterion="ladder climbs out of a wet pit")])
check("criterion fail naming the def stands", r["RM_Ladder"]["status"], "broken")

# 4. a criterion fail reaching the def only by LABEL text -> superseded by a newer name-matched pass
r = run([("climb_proof", "CLIMB_ladder_prison_door", "PASS", "2026-10-29T06:00:00")],
        [ver("fail", "2026-10-24T10:00:00Z", criterion="raid", why="the pit ladder blocked the harness")])
check("label-only fail superseded", r["RM_Ladder"]["status"], "works")

# 5. a row FAIL is never superseded by another row's newer PASS
r = run([("climb_proof", "CLIMB_ladder_wet", "FAIL", "2026-10-24T06:00:00"),
         ("climb_proof", "CLIMB_ladder_prison_door", "PASS", "2026-10-29T06:00:00")], [])
check("row fail not superseded by another row", r["RM_Ladder"]["status"], "broken")

# 6. a label-only PASS does not supersede an item-level fail
r = run([], [ver("partial", "2026-10-24T10:00:00Z"),
             {"id": "OTHER_ITEM", "criterion": "x", "result": "pass", "level": "L2", "ts": "2026-10-29T10:00:00Z",
              "why": "the pit ladder looked fine"}])
check("label-only pass does not supersede", r["RM_Ladder"]["status"], "broken")

# 7. the timestamp key ignores separator and zone
check("ts_key", mc.ts_key("2026-10-24 10:00:00"), mc.ts_key("2026-10-24T10:00:00Z"))

if fails:
    print("FAIL\n" + "\n".join(fails))
    sys.exit(1)
print("PASS selftest_mod_completion_supersede (7 checks)")
