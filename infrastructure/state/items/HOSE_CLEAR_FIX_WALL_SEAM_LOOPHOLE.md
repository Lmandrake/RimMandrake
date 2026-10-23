# HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE

`HoseMath.WallDepth` (FlowWorks `Source/Hose/HoseMath.cs`) is the distance from a sample to the nearest edge of ITS OWN
cell. `Clear` refuses only depth > `ClipTolerance` (0.06), so a hose centreline lying on the seam between two blocked cells
reads ~0 and passes; `SegmentClear` (RoutePulled) and every LayOnce stage share the test. Live: reel o1 (19,42) on
RM_fw_walkthrough_20261022b map C is drawn through walls (22,39)/(22,40); a forced fresh re-lay draws the same pose.
Evidence: `Transient/pile_2026-10-22/hose_audit.md` §4, `hose_audit/C09_C3n_battery_wall.jpg`, `E01_relay_C3north.jpg`.

## criteria
- A SelfTest case: a straight hose along z = k.0 across a one-cell-thick vertical wall is refused by Clear today (red) and
  green after; reel o1's re-lay on the walkthrough save goes through the wall gap at (22,42)-(22,43), captured.
