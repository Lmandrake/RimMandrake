# HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK

FlowWorks hose, audit F2 / defect D2 (`Transient/pile_2026-10-22/hose_audit.md` §3-§5): a laid hose priced walk-over
buildings (battery, power connector, sandbags) as bare ground and was drawn UNDER them (owner 2026-10-22: *"the hose is
going under the battery and wall"*). Deferred from HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS until the over-ground ruling; ruled
2026-10-23 by card (HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE: keep over-ground, add a joint check).

## criteria
- A1 L0: FlowWorks SelfTest `joints:` over-draw rows green (HoseOverDraw spans, altitude band above Building and under
  Item, source guard that CostsAsBuilding costs DrawsOverHose buildings and DrawAll redraws over them).
- A2 L2: on the rebuilt walkthrough, joint_check.py --all-maps shows no `over_building` or `under_rig` FAIL, and a hose
  laid across a battery (forced: walled either side) draws ABOVE it in a zoomed capture.

## built
- `RM_MapComponent_Hoses.CostsAsBuilding`: reels/pumps (IsRig) AND any walk-over edifice drawn above the hose layer
  (DrawsOverHose: not a door, altitude > Shadows) cost BuildingCrossCost in World() and LiveCellSig; still a cost, never a block.
- `DrawOverBuildings`: the strand stretches over such cells (HoseOverDraw.Spans + 0.3 sprite margin) are redrawn on
  BuildingOnTop (17) in the hose's crossing band; spans recorded for the probe. Not while a hose winds in (per-frame pose).
- Probe rows `over_building` / `under_rig` (HoseJointProbe). GSS power cords under the battery (D12) are GSS's, not done here.
