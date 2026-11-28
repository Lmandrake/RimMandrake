# A dry pit floor prints the ground it was dug in (RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER)

Build B (the builder's pick; the art judge passed it): the walls layer prints the recorded ground (OriginalTerrainAt) over a
dry dug floor, and the depth shade darkens THAT ground by StepK. Fix 669fe2fc9c.

- ArchSmall, 2026-11-28 00:19-00:22 PST, 26-mod list holding FlowWorks, quicktest map, noon, Clear, open sky.
- `northstar/pit_floor_ground_live.py --origin 62,62 --keep`: 9 of 9 PASS (result `northstar/pit_floor_ground_result_20261128T001952.json`).
  Floor over its own ground, 0.5 m | 2 m: Soil .862 | .602, SoilRich .830 | .636, Sand .856 | .630, Gravel .815 | .610,
  MarshyTerrain .828 | .623, Mud .879 | .615, Slate_Rough .804 | .642, Granite_Rough .801 | .628, Marble_Rough .853 | .600.
  The code predicts .847 | .630 on every ground; the spread (.80 to .88) is the textures' local variation between the centre
  square and the margin. Closest to the 0.90 limit: Mud at 0.5 m (.879). The same check read 4 FAIL on build 81ee41df54
  (2026-11-23; SoilRich 1.00, MarshyTerrain .98, Mud 1.11, Slate 1.22 at 0.5 m).
- `northstar/pit_floor_ladder_live.py --origin 62,84`: 5 of 5 PASS (result `northstar/pit_floor_ladder_result_20261128T002117.json`);
  the 16 m floor's grain reads 3.3 (bar 2.0; 2.38 on 81ee41df54).
- Pictures: `strip_left_after.png` (Soil, SoilRich, Sand, Gravel), `strip_right_after.png` (MarshyTerrain, Mud, Slate, Granite,
  Marble); top row 2 m, bottom row 0.5 m. Before: `design/specs/2026-11-23-pit-floor-depth-ladder/img/pit_floor_on_nine_grounds.png`.
- Art judge (fresh rm-judge, delegated call): PASS for B, "no flaw that B has and A would not"; Slate keeps its rock grain and
  reads as a deep rock pit, Marsh and Mud do not read as water.
