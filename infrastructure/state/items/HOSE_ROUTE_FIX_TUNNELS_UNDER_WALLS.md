# HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS

FlowWorks: a laid hose on RM_fw_walkthrough_20261022b map C is drawn under the yellow battery and through a wall
(owner shot `Transient/pile_2026-10-22/walk_owner_shots/20261022184237_1.jpg`).

Cause and history: `Transient/pile_2026-10-22/hose_audit.md` §4.

## criteria
- A hose never draws across a cell holding a wall or a non-walk-over building; a wall built on a laid hose's corridor
  re-plans or reels it in, also while the game is paused for a review. Live capture + state read prove it.

## audit 2026-10-22 (`Transient/pile_2026-10-22/hose_audit.md` §4)
- Through the wall: mechanism filed as HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE (not a stale lay; a fresh re-lay repeats it).
- Under buildings: World() prices every walk-over building (battery, power connector) as ground; only reels/pumps cost
  (CostsAsBuilding); the hose draws below buildings. Fix: avoid non-rig buildings, and draw above one it must cross.
- GSS power cords from the connector also run under the battery (C08, C17): same rule owed in GSS.
