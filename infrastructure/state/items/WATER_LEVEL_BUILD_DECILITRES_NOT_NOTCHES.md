## spec
Plan P3 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`).
Design: `design/RimMandrake/flowworks_level_surface_2026-10-17.md` Option 1 (§3) and order of work (§4); the code it
hits is listed in its §5. Owner: *"We need VERY smooth water. That's water's one primary characteristic: a level
surface."* Ruled exactly level by card 2026-10-17. ESTIMATE 4 to 7 agent-days, done in one pass with
`LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`.

Supersedes `WATER_SURFACE_REPAIR_LEVEL_OR_BUST`; its first-fix notes (the dry-front creep fix `fe309aefe`, the
`LevelSurfaceChecks.cs` guards, the S5 A head-rule finding) are in
`infrastructure/state/items/closed/WATER_SURFACE_REPAIR_LEVEL_OR_BUST.md`. Its live rerun moved to
`WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX`.

## verify
- Offline: S6 pond = nine squares at 1.44 m; full 3×3 pond + ten 0.5 m canal squares = every canal square 0.237 m wet;
  one full pond square + same canal = all ten at 4.5 cm; litres conserved to the decilitre; Python oracle agrees.
- The per-body surface-gap diagnostic reads under 1 cm in every scene.
