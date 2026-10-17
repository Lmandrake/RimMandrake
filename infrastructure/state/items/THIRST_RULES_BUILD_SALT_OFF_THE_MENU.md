# THIRST_RULES_BUILD_SALT_OFF_THE_MENU

Build for FOUNDRY. Spec: `design/RimMandrake/thirst_fluids_3x3_2026-10-17/04-merged.md` §8 (owner card rulings
2026-10-17, his write-ins verbatim) and §8.2 (the ordered plan). Background design:
`design/RimMandrake/thirst_fluids_design_2026-10-17.md`.

**First, the two rule breaks in today's built code:**
1. Auto-fill gathers any liquid: `WorkGiver_FillBottle` → `RM_LiquidBottleUtility.TryFindFillCell` passes
   `requireFreshWaterOnly: false` (`Source/LiquidTypes/RM_LiquidBottleUtility.cs:110-117, 255-314`). Ruling: no
   non-potable liquid is gathered without an order (a machine's bill counts as the order).
2. Thirsty pawns drink salt water routinely: `RM_ThirstMath.Acceptable` gates only Toxic; Fouled is ranked by
   quality then distance. Ruling: salt water and brine are drunk only in a mood-pool mental break while parched.

**Then** §8.2 steps 2-8: use class on rows and terrain-only liquids; awkward-access penalty (not vessels) with
Ascetic/Tough/Undergrounder and wild/animal/tribal exemptions; slime and toxic as a last resort gated like vanilla's
desperate rotten food; slime effects through Contagion, Gelatinous Slime absorption, The Rot spores, yellow =
nausea/vomiting; salt break + `RM_SaltPoisoning`; slime containers by order; per-net drinking reserve; Dubs mode
reads `DBHThirst`. Ships with its functional script rows.

**Not in scope:** Q12's six held defaults (cooled boiling water, ice/snow, sanguophage blood, animals and
slime/salt, brine on crops, buckets on fires) — the owner will rule them later.
