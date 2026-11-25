#!/usr/bin/env python3
"""Make the fixture save of `colony_drift.py` on a test game: a fresh quicktest map, saved under FIXTURE, and the thing ids of its
colonists printed for the plan. Item RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED.

    python.exe src\\RimMandrake\\Utils\\scene_compare_plans\\make_fixture.py ArchSmall
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scene  # noqa: E402

FIXTURE = "rm_fixture_play_vs_step"


def main(game):
    with scene.open(game, needs={"map": "fresh:quicktest"}) as s:
        pawns = s.raw("jawa/pawn_get", limit=200)
        rows = [p for p in pawns.get("pawns") or [] if p.get("faction") == "PlayerColony"]
        r = s.raw("rimworld/save_game", saveName=FIXTURE)
        print(json.dumps({"fixture": FIXTURE, "saved": r.get("success"), "reply": {k: r.get(k) for k in ("saveName", "message", "path")},
                          "colonists": [{"id": p.get("thingId"), "name": p.get("name")} for p in rows]}, indent=1))
    return 0 if r.get("success") is True and rows else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "ArchSmall"))
