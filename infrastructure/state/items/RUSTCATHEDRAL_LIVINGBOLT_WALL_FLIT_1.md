# RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1

Owner, Rust Cathedral sheet 2026-10-05, verbatim: "Very small 0.1 cells, more like a little button that flits around on walls and other surfaces."

RM_LivingBolt (`src/RimMandrake/RustCathedral/Defs/ThingDefs_Races/RM_LivingBolt.xml`) is a slow walking mech dancer; it has no wall or surface movement. A src/ search (wall-crawl, cling, flit, surface-walk) found no existing mechanism to reuse. Not built; this item owes the design: how a creature moves on wall cells and other surfaces, and how that sits with the dancer behaviour (`RM_ThinkTree_LivingBolt.xml`, `RM_JobGiver_ResonantDance.cs`). Art and size (0.1 cells) are on RUSTCATHEDRAL_SHEET_ART_REDO_1.

## Design options (BENCH, 2026-10-06, for the Rust Cathedral sitting — not built)

MEASURED from decompiled 1.6 (`Verse/AI/PathGrid.cs` l.125-141, `PathGridDef.flying`): pathing has a separate Flying
grid, and an impassable building is passable to flyers only when its def sets `forcePassableByFlyingPawns`. No
pawn of any kind can stand IN a wall cell without that flag on the wall itself.

- **A. Clings to walls by drawing (recommended).** It stays a pawn, but only ever picks wall-ADJACENT standable cells
  (a JobGiver choosing the next cell beside a wall or other `fillPercent >= 0.9` building), hops there fast
  (short Goto, high move speed), and its render is offset half a cell INTO the wall face, drawn above the wall
  layer, so it reads as a button on the wall. The dancer behaviour (`RM_JobGiver_ResonantDance`) keeps
  running between hops. Cost: one JobGiver + a draw-offset comp; no pathing change. Limit: on open ground with
  no walls it falls back to the dance and looks like a small floor critter.
- **B. Not a pawn at all.** A wall-attached ambient Thing (like a mote that lives on wall buildings and jumps
  between them). Cheapest to look right everywhere, but it can't be hunted, tamed or counted as fauna, so it
  leaves the roster.
- **C. Real wall-walking (rejected).** Setting `forcePassableByFlyingPawns` on walls lets EVERY flyer path
  through every wall, raids included. The engine has no per-race version.

NEXT: put A vs B to the owner at the Rust Cathedral sheet sitting (with RUSTCATHEDRAL_SHEET_ART_REDO_1's 0.1-cell art), then build the one he picks.
