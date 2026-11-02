"""SUMP_GLASSWALK_SPEED_RATIO_1, offline half: is glasswalk's pathCost 3 right for the spec's "~80%, never full speed"?

The law (decompiled 1.6, D:\\ClaudeWork\\rimmandrake\\decomp\\rw16\\all\\Verse.AI\\Pawn_PathFollower.cs, CostToMoveIntoCell):
  cost = TicksPerMoveCardinal + PathGrid.CalculatedCostAt   (terrain pathCost; TileGranite has none, so 0)
  then x1 for LocomotionUrgency.Jog (an ordered Goto), x2 (min 50) Walk, round(x0.75) Sprint.
  The pawn pays 1 per tick and carries the overshoot into the next cell, so ticks/cell == cost on average.
So glass/granite speed = T / (T + 3) at Jog: 13/16 = 0.81 for a standard colonist (MoveSpeed 4.6 -> 60/4.6 = 13.04).

The 2026-10-10 reading of 0.65 (granite 9.8, glass 15 ticks/cell) is not this law at ANY T: the law gives T/(T+3) = 0.77 at
T = 9.8, and 0.65 would need pathCost 5.3. The instrument explains it: the scene's timer called scenes.scenelib.run(10),
which plays at speed 4 for at least 200 ms (~80 ticks at ~400 ticks/s), so each sample was ~80 ticks, not 10, against
walks of 120-200 ticks. The live re-measure (prove_glasswalk_speed.py) times with exact rimworld/step_game_ticks steps.

Run: python3 src/RimMandrake/TheSump/test_glasswalk_speed_model.py   (exit 0 = every check holds)
"""
import ast
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFS = os.path.join(HERE, "Defs", "TerrainDefs", "RM_SumpWalkways.xml")
PROVE = os.path.join(HERE, "prove_glasswalk_speed.py")
SCENELIB = os.path.join(ROOT, "src", "RimMandrake", "Utils", "scenes", "scenelib.py")

BAND = (0.72, 0.90)          # the spec's "~80%" acceptance band (as the 2026-10-10 scene judged it)
STANDARD_T = 60.0 / 4.6      # vanilla Human MoveSpeed 4.6 -> 13.04 ticks per cardinal cell


def cost(T, path_cost, urgency="Jog"):
    """Pawn_PathFollower.CostToMoveIntoCell for a cardinal step onto a plain floor (no edifice, no terrain tag factor)."""
    n = min(T + path_cost, 450.0)
    if urgency == "Amble":
        n = max(n * 3, 60.0)
    elif urgency == "Walk":
        n = max(n * 2, 50.0)
    elif urgency == "Sprint":
        n = float(int(n * 0.75 + 0.5))   # Mathf.RoundToInt (banker's rounding differs only at exact .5; irrelevant here)
    return max(n, 1.0)


def ticks_per_cell(T, path_cost, cells=200, urgency="Jog"):
    """Simulate the follower's pay loop: pay 1 per tick, carry the overshoot (nextCellCostLeft) into the next cell."""
    left, ticks = 0.0, 0
    for _ in range(cells):
        c = cost(T, path_cost, urgency)
        left = max(c + min(left, 0.0), 1.0)
        while left > 0:
            left -= 1.0
            ticks += 1
    return ticks / cells


def glass_path_cost():
    """RM_Glasswalk's own <pathCost>, read from its own TerrainDef element (None if absent)."""
    for td in ET.parse(DEFS).getroot().iter("TerrainDef"):
        if (td.findtext("defName") or "").strip() == "RM_Glasswalk":
            v = td.findtext("pathCost")
            return int(v) if v is not None else None
    return None


def times_exactly(path):
    """True when walk_exact's timing loop steps through step(), step() calls the bridge's rimworld/step_game_ticks, and no
    function calls S.run (scenelib.run's 200 ms floor is ~80 ticks a sample)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    funcs = {f.name: f for f in tree.body if isinstance(f, ast.FunctionDef)}

    def calls(node):
        return [n for n in ast.walk(node) if isinstance(n, ast.Call)]

    def is_tool_call(c, tool):
        return (isinstance(c.func, ast.Attribute) and c.func.attr == "call" and c.args
                and isinstance(c.args[0], ast.Constant) and c.args[0].value == tool)

    step_ok = "step" in funcs and any(is_tool_call(c, "rimworld/step_game_ticks") for c in calls(funcs["step"]))
    loop_ok = "walk_exact" in funcs and any(
        isinstance(w, ast.While) and any(isinstance(c.func, ast.Name) and c.func.id == "step" for c in calls(w))
        for w in ast.walk(funcs["walk_exact"]))
    no_run = not any(isinstance(c.func, ast.Attribute) and c.func.attr == "run" for c in calls(tree))
    return step_ok and loop_ok and no_run


def main():
    fails = []

    def check(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    pc = glass_path_cost()
    check(pc == 3, "RM_Glasswalk pathCost read from the def = %r (expected 3)" % pc)
    pc = pc or 3

    # The pay loop reproduces the closed form (ticks/cell == cost) across the whole pawn range.
    worst = max(abs(ticks_per_cell(T / 10.0, pc) - (T / 10.0 + pc)) for T in range(50, 401, 7))
    check(worst < 0.05, "simulated pay loop matches T+pathCost within 0.05 ticks/cell for T in 5..40 (worst %.3f)" % worst)

    r13 = ticks_per_cell(STANDARD_T, 0) / ticks_per_cell(STANDARD_T, pc)
    check(BAND[0] <= r13 <= BAND[1] and abs(r13 - 0.8) < 0.02,
          "standard colonist (T=%.2f): glass/granite speed = %.3f, in %s and ~0.80" % (STANDARD_T, r13, BAND))

    # "never full speed": strictly slower for every pawn below the engine's 450-tick cost cap, because pathCost is ADDED.
    # (At T >= 450 - pathCost both floors clamp to 450: a pawn that slow is immobile in practice, not "full speed".)
    never_full = all(cost(T / 10.0, pc) > cost(T / 10.0, 0) for T in range(10, int((450 - pc) * 10)))
    check(never_full, "glass strictly slower than granite for every T in 1..%d ticks/cell (never full speed below the cap)"
          % (450 - pc - 1))

    # Retune check: is 3 the pathCost closest to 0.80 for the standard pawn?
    best = min(range(0, 11), key=lambda c: abs(STANDARD_T / (STANDARD_T + c) - 0.80))
    check(best == pc, "pathCost closest to 0.80 for T=13.04 is %d (shipped %d)" % (best, pc))

    # The 2026-10-10 reading is outside the law: at T=9.8 the law says 0.77, the scene said 0.65.
    r98 = 9.8 / (9.8 + pc)
    check(abs(r98 - 0.65) > 0.08, "law at T=9.8 gives %.3f; the scene's 0.65 (implied pathCost %.1f) is outside the law (instrument suspect; A1 decides)"
          % (r98, 15 - 9.8))

    # The instrument: scenelib.run(n) never plays less than 200 ms at speed 4.
    lib = open(SCENELIB, encoding="utf-8").read()
    check("max(200," in lib, "scenelib.run floors each play_for at 200 ms (~80 ticks at speed 4): coarse for n=10")

    # The live proof must time with exact steps, not scenelib.run.
    if os.path.exists(PROVE):
        check(times_exactly(PROVE),
              "prove_glasswalk_speed.walk_exact's loop steps via step() -> rimworld/step_game_ticks; nothing calls S.run")
    else:
        check(False, "prove_glasswalk_speed.py exists")

    print("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/offline %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
