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

Also absorbed (consolidation 2026-10-17, `design/RimMandrake/flowworks_ticket_consolidation_2026-10-17.md`):
`WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` (the whole-unit "gap >= 2" surface rule, built but never deployed; its
station-1 walk showed 0/deep/0) and `KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER`. Natural water (ponds, lakes) joins
when `WATER_NATURAL_DECIDE_ONE_SURFACE` brings his decisions.

## verify
- L1 offline: S6 pond = nine squares at 1.44 m; full 3×3 pond + ten 0.5 m canal squares = every canal square 0.237 m
  wet; one full pond square + same canal = all ten at 4.5 cm; litres conserved to the decilitre; Python oracle agrees.
- L1: each connected body holds a whole number of decilitres; the sum over all bodies and containers is unchanged by
  any pulse, split or merge (fuzz suite covers a falling pond splitting and a rising one merging).
- L1: the per-body surface-gap diagnostic reads under 1 cm in every scene; it is the instrument
  `northstar/level_surface_bar.py` reads live.
- L1: the solver's selftests run at the full shipped flag combination (absorbed `KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER`).
- L1: save migration logs a before/after per body; an old save loads with every body's litres unchanged.
- L2 (proved in the epic's P10 walk): `still_water_one_surface_height` live on S5, S6 and the 4/7/7/4 square.
