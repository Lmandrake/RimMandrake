# HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS

FlowWorks: a laid hose on RM_fw_walkthrough_20261022b map C is drawn under the yellow battery and through a wall
(owner shot `Transient/pile_2026-10-22/walk_owner_shots/20261022184237_1.jpg`).

Cause and history: `Transient/pile_2026-10-22/hose_audit.md` §4.

## criteria
- A1 L0: FlowWorks SelfTest HoseWall_S1-S4 green (HoseWallSeamChecks.cs; S1/S3/S4 red on the code before 849b1674ea): no laid
  pose, fresh or re-planned, crosses a wall or a seam between two wall cells.
- A2 L2: `proof_hose.py --live --no-fresh-map --only walls` on RM_fw_walkthrough_20261022b reads HW1_no_laid_hose_crosses_a_wall
  PASS on map C and map R (every laid hose's census wallCross = 0), plus a capture of reel o1 (19,42) through the gap (22,42)-(22,43).
- A3 L2: a wall built across a laid hose's corridor re-plans it or reels it in (live state read).

Under-buildings (D2, the battery/power connector): not a criterion here. Owner card 2026-10-22 *"let's not do that yet"*
deferred it to HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE, ruled 2026-10-23 (keep over-ground); the work is
HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK.

## built 2026-10-22 (BENCH helper)
Walls: fixed by the wall-depth measure (HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE, 849b1674ea, DLL cf6d33f7b6). The route planner itself
never entered a wall cell (RouteCells/CordPlanner walk walkable cells only); every shaping stage and the string-pulling
accepted poses on a wall seam because Clear's depth was per-cell. Live instrument: HoseProbe census `wallCross`/`wallCrossAt`,
proof_hose.py block `walls` (HW1; reads the map as it stands, no calming). Progress: `Transient/pile_2026-10-22/hose_walls_fix.md`.

## audit 2026-10-22 (`Transient/pile_2026-10-22/hose_audit.md` §4)
- Through the wall: mechanism filed as HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE (not a stale lay; a fresh re-lay repeats it).
- Under buildings: World() prices every walk-over building (battery, power connector) as ground; only reels/pumps cost
  (CostsAsBuilding); the hose draws below buildings. Fix: avoid non-rig buildings, and draw above one it must cross.
- GSS power cords from the connector also run under the battery (C08, C17): same rule owed in GSS.
