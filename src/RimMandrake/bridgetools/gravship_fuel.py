"""gravship_fuel.py - how a proof fuels a tool-built gravship, decided by the mod list it finds.

PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE. Two fuel models exist and a proof must not assume either:

* VGE (Vanilla Gravship Expanded) loaded: ChemfuelTank is astrofuel storage on a PipeSystem net and a thruster is
  a net consumer, inactive until a VGE_AstrofuelPipe run joins it to a filled tank (measured 2026-08-29). Fill
  gizmo: "DEBUG: Fill ...".
* No VGE (the Relentless live game, 2026-11-06): vanilla Odyssey. ChemfuelTank is a gravship facility with
  CompRefuelable; it feeds the engine over substructure, no pipe exists. Fill gizmo: "DEV: Set fuel to max".

Pure functions only (no bridge), so selftest_prove_gravship_fuel.py drives them offline.
"""

PIPE_DEF = "VGE_AstrofuelPipe"

# Exact label PREFIXES. A loose 'fill' match once executed 'Allow manual refill' and left the tank empty with
# success: true (2026-08-29), so a label must START WITH one of these.
FILL_PREFIXES = ("DEBUG: Fill", "DEV: Set fuel to max")


def fuel_mode(get_def_reply):
    """Read a `jawa/get_def defName=VGE_AstrofuelPipe defType=ThingDef` reply.

    Returns "pipe" (the def is loaded: lay the pipe), "vanilla" (the def is ABSENT: no pipe), or None when the
    reply proves neither -- a timeout, a typo'd def type, any other failure is no reading, never absence."""
    r = get_def_reply if isinstance(get_def_reply, dict) else {}
    if r.get("success") is True:
        return "pipe"
    msg = str(r.get("message") or "")
    if " named " in msg and not msg.startswith("No def type named"):
        return "vanilla"
    return None


def is_fill_label(label):
    return any((label or "").startswith(p) for p in FILL_PREFIXES)


def pipe_run(X, Z, tx, tank_cells, thr_cells):
    """The pipe cells joining the tank at (X+14, Z+10) to the thruster at (tx, Z+1), minus both footprints."""
    cells = [(X + 14, pz) for pz in range(Z + 2, Z + 10)]       # vertical run beside the tank column
    cells += [(px, Z + 2) for px in range(X + 11, X + 14)]       # horizontal run toward the thruster
    cells.append((tx, Z + 3))                                    # cardinal-adjacent to the thruster
    skip = set(tank_cells) | set(thr_cells)
    return [c for c in dict.fromkeys(cells) if c not in skip]
