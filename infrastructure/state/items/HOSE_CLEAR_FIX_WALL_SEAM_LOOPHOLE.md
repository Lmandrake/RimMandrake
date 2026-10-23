# HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE

`HoseMath.WallDepth` (FlowWorks `Source/Hose/HoseMath.cs`) is the distance from a sample to the nearest edge of ITS OWN
cell. `Clear` refuses only depth > `ClipTolerance` (0.06), so a hose centreline lying on the seam between two blocked cells
reads ~0 and passes; `SegmentClear` (RoutePulled) and every LayOnce stage share the test. Live: reel o1 (19,42) on
RM_fw_walkthrough_20261022b map C is drawn through walls (22,39)/(22,40); a forced fresh re-lay draws the same pose.
Evidence: `Transient/pile_2026-10-22/hose_audit.md` §4, `hose_audit/C09_C3n_battery_wall.jpg`, `E01_relay_C3north.jpg`.

## criteria
- A1 L0: FlowWorks SelfTest HoseWall_S1 (a hose along z = k.0 across a one-thick wall) and HoseWall_S3 (WallDepth agrees with an
  independent nearest-walkable-cell ruler) are red on the per-cell rule and green after (HoseWallSeamChecks.cs).
- A2 L0: HoseWall_S4: the walkthrough's C3-north scene re-laid (12 seeds; seeds 7/8 crossed (22,39)/(22,40) at z~40.04 before)
  and a 160-scene sweep of one-thick walls never leave a pose sample deeper than 0.12 inside a wall.
- A3 L2: on RM_fw_walkthrough_20261022b with the new DLL, reel o1 (19,42) re-lays through the wall gap (22,42)-(22,43), captured,
  and `proof_hose.py --live --no-fresh-map --only walls` reads HW1_no_laid_hose_crosses_a_wall PASS on map C and map R.

## built 2026-10-22 (BENCH helper)
Fix: `HoseMath.WallDepth` = -`CordWorld.Clearance` (distance to the nearest WALKABLE cell box, the measure the GSS cords use).
History: the per-cell rule came in 9e9f153d4e (GSS round 4, 2026-10-04); before it Clear refused any sample whose cell was
blocked. The GSS hose selftests (HoseSelfTest, GSS fuzz -> HoseFuzz) DID move to FlowWorks at 7cf08bf64e, but every wall
assertion in them measured with WallDepth/Clear, the code under test, so the hole was invisible before and after the move.
Side effect, measured: the station-34 owner maze's taut route was 30.9 cells only because it cut wall seams (44 samples inside
walls); it is 35.0 now (needs a 37-cell hose; default 40). Progress: `Transient/pile_2026-10-22/hose_walls_fix.md`.
