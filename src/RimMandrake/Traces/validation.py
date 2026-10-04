"""validation.py -- modcheck suite for RimMandrake: Traces (mandrake.rm.traces). First script.

Never deployed (deploy_custom_mods.py excludes `.py`). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Traces

State: STEP 0 SPIKE (design/RimMandrake/event_trace_props_library_design_2026-10-03.md §8). The mod ships
two placeholder filth defs and no C#, so this suite covers only the spike's questions; the walk's other
`## must be true` lines are UNCOVERED until step 1 builds the placer. Grows with the mod, a step at a time.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Traces")
suite.toggles = []          # no Mod Settings until step 1 (design §6); every §6 row joins here when built

WALL_SPIKE = "RM_Trace_SpikeWall"
FLOOR_SPIKE = "RM_Trace_SpikeFloor"


def _found(t, def_name, x, z, w=1, h=1):
    """Rows of def_name in a rect, or None when the call could not be read (UNMEASURED, never 'absent')."""
    r = t.bridge_call("jawa/list_things", defName=def_name, rect="%d,%d,%d,%d" % (x, z, w, h))
    if not isinstance(r, dict) or r.get("success") is False:
        return None
    return [row for row in (r.get("things") or []) if row.get("def") == def_name]


@suite.chain("spike")
def spike(t):
    """Design §2.2 UNMEASURED (1): does a filth spawn on a cell whose edifice is a wall? Plus the floor
    carrier as a control that the defs resolve at all."""
    t.clear_area(size=12)
    x, z = t.anchor
    with t.component("floor_spike_spawns", beyond_toggle=True):
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (FLOOR_SPIKE, x, z))
        if t._guard():
            rows = _found(t, FLOOR_SPIKE, x, z)
            if rows is None:
                raise ExpectationFailed("UNMEASURED: list_things did not answer for %s" % FLOOR_SPIKE)
            if len(rows) != 1:
                raise ExpectationFailed("control failed: %d %s at the anchor (want 1)" % (len(rows), FLOOR_SPIKE))
    wx = x + 3
    with t.component("wall_spike_spawns_on_a_wall_cell", beyond_toggle=True):
        t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d;%s:%d,%d" % (wx, z, WALL_SPIKE, wx, z))
        if t._guard():
            walls = _found(t, "Wall", wx, z)
            rows = _found(t, WALL_SPIKE, wx, z)
            if walls is None or rows is None:
                raise ExpectationFailed("UNMEASURED: list_things did not answer on the wall cell")
            if not walls:
                raise ExpectationFailed("UNMEASURED: the wall itself did not spawn, so the question was not asked")
            if len(rows) != 1:
                raise ExpectationFailed("wall-cell filth refused: %d %s on a wall cell -> fall back to carrier A "
                                        "(design §2.3)" % (len(rows), WALL_SPIKE))
        t.screenshot()
