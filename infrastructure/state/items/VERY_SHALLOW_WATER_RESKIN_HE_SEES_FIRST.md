## spec
Plan P9 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`). Owner R2 (card 2026-10-17): a new look for water under 25 cm.
**Check first:** `RM_WaterThin` (pond-depth "thin water", provisionally installed by `ffdf058c2`, judged in game
only) may already be this look; reuse it if it is. One review for him with `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST`,
`CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES` and P5's deeper wall faces and floor tints. Cosmetic: nothing ships before his look.

## verify
- L1: every square whose water depth (solver) is above 0 and under 25 cm draws the very-shallow look, for every liquid.
- L3: in a frame, dry / under 25 cm / 0.5 m are distinguishable (feeds `fill_tier_legible`).
- L4: he has looked (true-scale sheet or in-game shot) and kept it.
