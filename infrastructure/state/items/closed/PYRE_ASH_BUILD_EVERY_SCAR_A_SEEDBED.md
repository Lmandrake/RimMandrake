# PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED (MOD, Pyrelands)

## Spec

The spec is `design/RimMandrake/pyrelands_ash_redesign_2026-10-12.md`. Owner ruling:
`PYRE_ASH_REDESIGN_BURN_FEEDS_THE_FIELD`, 2026-10-12, *"Deep ash everywhere + fresh-burn bonus"*.
Every number in it is PROVISIONAL and is a Mod Setting.

## Build

1. **Terrain** (§1):
   - Delete the Trace, Light and Heavy rungs.
   - Keep them as legacy aliases for one cycle (§7).
   - Deep ash: fertility 0.40, pathCost 2, Beauty 0.
   - Point every `RM_FE_Ground_*` `burnedDef` at `RM_FE_Ash_Deep`.
2. **Painting** (§2): the biome paints deep ash.
3. **Fertility** (§3):
   - A `RM_AshFieldExtension` on the deep-ash def.
   - A postfix on `FertilityGrid.CalculateFertilityAt`.
   - A watered grid fed by FlowWorks irrigation, using the `RM_SoakSources` rule lifted into a
     shared helper, plus natural water within 2 cells.
4. **Burn bonus** (§4): a burn-tick grid plus a rain accumulator.
5. **Mod Settings** (§5), plus the ambient-ash settings (§5a).
6. **Inspect line**: show the watered state and the remaining burn bonus.

## Regression to test

🔴 **Widen the fire-tick gate.** `RM_FireEcoKernel.IsScorchableGround` admits only
`RM_FE_Ground_*`. On a deep-ash map that would silence ash dusting, scorch-fruit and the burn
stamp on about 85% of the biome. Write a selftest for it.

## Verify (your own, per the build-designs-its-own-verification ruling)

- Kernel selftests for the bonus formula: decay, rain fade, cap and re-burn reset.
- Replace the harness chain `ground_ash_ladder` with three chains: `ground_deep_ash`,
  `ash_fertility_watered` and `fresh_burn_bonus`. Each is a STATE read of `FertilityAt`.
- Re-point `embergrass_regrow`'s cohort to `RM_FE_Ash_Deep`.
- Purge every rung reference (§6 list).

The north-star bars are the OWNER's. The proposed wording is in §6; do not edit `## north star`.

## Owner answers 2026-10-12 (cards) — added to the scope
- Deep ash is NORMAL ground: pathCost 2, beauty 0 (*"Normal ground."*).
- **Black Rain waters the ash for about a day** (`blackRainWaterHours` 24): one per-map "watered until" tick, design §3. Reverses the old "non-hydrating" stance.
- **Ambient free-flying ash, a LOT** (*"a LOT of free-flying ash blowing around like snow"*): new `RM_FE_Weather_AshDrift` replaces `Clear` in the biome; settings `ambientAshEnabled`, `ambientAshShare` (density), `ambientAshHeavy`; design §5a. Add a harness check that AshDrift is the common weather.
- The three north-star bars are APPROVED and installed in `design/validation_walks/RimMandrake/Pyrelands.md`; the old ladder bars are gone. Build must make them pass.

NEXT: build items 1–6, then run selftests and `--chains ground_deep_ash,ash_fertility_watered,fresh_burn_bonus,embergrass_regrow`.
