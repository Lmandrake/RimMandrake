# HUGETHINGS_SETTINGS_HARDENING_1 — Huge Things settings hardening

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Verified fix-now findings from `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`).

- **B3.19 / C3.6 / D3.3**: `RM_HugeThingsSettings.ExposeData` sanitises only `plantTrunkScale`, `pawnHitboxScale` and `giantPlantSmashMinTier` (`:96-102`). Scribe-loaded values bypass the slider ranges. `RM_TitanicKernel.ThresholdsValid` accepts an infinite T3. Fix: clamp every numeric on load and on edit (finite, ranges as the sliders state, positive work times and batch sizes). Keep the shipped-ladder fallback.
- **A2.7 / D1.5**: the checkbox at `:137` reads "Trunks give cover, and shots into them hurt the plant", but it controls damage only, and cover stays on. Relabel it "Trunk hits damage the plant". The "Destruction wake off" text should say "no wake damage". Move all settings strings into `Languages/English/Keyed`.
- **B4.6**: rubble chance is rolled per footprint cell, about 5.6 attempts per 4×4 step at 35%. Label it "chance per footprint cell" (whether to roll once per step is a later idea).

## verify
A settings-load fixture with NaN, ∞, negative and zero values ends at sane values. Every settings label uses Translate.

## criteria
A1: every numeric field is validated. A2: labels are accurate and keyed.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
