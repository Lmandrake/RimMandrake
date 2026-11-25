"""decide_rebound_legs_from_record.py - decide the repaired V_SHORTER of sc_storeroom_mortar_rebound_legs from the records
of its two live runs of 2026-11-25 on ArchSmall, with no new live run (RIMMANDRAKE_RULE_REBOUND_NEAR_WALL_OUTFLIES_FIRST_LEG).

The logs print, per room, the legs flown and the planned cells of each leg. The kernel writes `left` = cells planned for
the leg minus cells travelled (RM_ThingFlyer_Knockback.cs, cellsLeft), and every leg of this scene runs along one row, so
left = planned - flown, exactly. Cross-check: ReboundCells(left, keep) must equal the next leg's planned cells; a log whose
numbers fail the cross-check is COULD NOT LOOK, never a verdict.

This rebuilds the journal records (item_move, item_rebound with `left`, item_land) and runs the scene's own functions
(good_legs, rebound_ratios; taken from the scene file by AST, so the check judged is the check that runs live).

    python3 design/concepts/ExplosiveKnockback/version/pilot_throwaway/decide_rebound_legs_from_record.py
Exit 0: real build PASS and plant keep_all FAIL, as wanted. 1: a reading is not as wanted. 2: could not look.
"""
import ast
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
SCENE = os.path.join(ROOT, "src/RimMandrake/ExplosiveKnockback/proof/scene_storeroom_mortar_rebound_legs.py")
EARLY = os.path.join(ROOT, "design/concepts/ExplosiveKnockback/version/in_game/early")
RUNS = [("real build, keep 70", "sc_storeroom_mortar_rebound_legs_ek-u-rebound.log", 70, "PASS"),
        ("plant keep_all, keep 100", "sc_storeroom_mortar_rebound_legs_plant_ek-v-storeroom_mortar_rebound_legs-keep_all.log",
         100, "FAIL")]
LINE = re.compile(r"INFO budgets (\w+) (\w+): legs flown \[([^\]]*)\], planned cells \[([^\]]*)\]")


def scene_functions():
    tree = ast.parse(open(SCENE, encoding="utf-8").read())
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("cell", "dist", "good_legs", "rebound_ratios")]
    ns = {"math": math}
    exec(compile(ast.Module(body=keep, type_ignores=[]), SCENE, "exec"), ns)
    for f in ("good_legs", "rebound_ratios"):
        if f not in ns:
            raise SystemExit("COULD NOT LOOK: %s has no %s" % (SCENE, f))
    return ns


def rebound_cells(left, keep):
    return 0 if left <= 0 else min(left, int(math.floor(left * keep / 100.0 + 1e-4)))


def records(legs, planned, keep):
    """One good thrown east along a row from (0, 0): the journal records its run would have written."""
    x = 0
    recs = [{"type": "item_move", "thing": "Steel1", "from": [0, 0], "planned": planned[0], "wallFirst": False}]
    for i in range(len(legs) - 1):
        x += legs[i] * (1 if i % 2 == 0 else -1)
        left = planned[i] - legs[i]
        if rebound_cells(left, keep) != planned[i + 1]:
            return None, "leg %d: ReboundCells(%s, %s) = %s, the log says %s" % (i, left, keep, rebound_cells(left, keep),
                                                                                 planned[i + 1])
        recs.append({"type": "item_rebound", "thing": "Steel1", "at": [x, 0], "left": left, "cells": planned[i + 1],
                     "bounce": i + 1, "tick": i + 1})
    x += legs[-1] * (1 if (len(legs) - 1) % 2 == 0 else -1)
    recs.append({"type": "item_land", "thing": "Steel1", "dest": [x, 0], "to": [x, 0], "bounces": len(legs) - 1})
    return recs, None


def main():
    ns = scene_functions()
    bad = 0
    for label, log, keep, want in RUNS:
        path = os.path.join(EARLY, log)
        rooms = [(m.group(1), [float(v.strip(" '")) for v in m.group(3).split(",")],
                  [int(v) for v in m.group(4).split(",")]) for m in LINE.finditer(open(path, encoding="utf-8").read())]
        if len(rooms) != 3:
            print("COULD NOT LOOK %s: %d room line(s) in %s, want 3" % (label, len(rooms), path))
            return 2
        worst, of, n = None, None, 0
        for room, legs, planned in rooms:
            recs, err = records([int(round(v)) for v in legs], planned, keep)
            if err:
                print("COULD NOT LOOK %s %s: %s" % (label, room, err))
                return 2
            g = ns["good_legs"](recs, "Steel1")
            ratios, unread = ns["rebound_ratios"](g["legs"], g["lefts"])
            if unread:
                print("COULD NOT LOOK %s %s: %d rebound leg(s) unread" % (label, room, unread))
                return 2
            for i, r in ratios:
                n += 1
                if worst is None or r > worst:
                    worst, of = r, "%s leg %d: %.0f of %s cells left" % (room, i, g["legs"][i], g["lefts"][i])
            print("  %s %s: legs %s, cells left %s, ratios %s" % (label, room, g["legs"], g["lefts"],
                                                                ["%.2f" % r for _, r in ratios]))
        got = "PASS" if worst < 1.0 else "FAIL"
        print("%s V_SHORTER all (%s): worst ratio %.3f (%s), limit < 1.0, %d rebound leg(s); wanted %s" % (
            got, label, worst, of, n, want))
        bad += got != want
    print("%s: the repaired check %s" % ("OK" if not bad else "NOT AS WANTED",
                                         "fails the plant and passes the real build" if not bad else "misjudges a run"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
