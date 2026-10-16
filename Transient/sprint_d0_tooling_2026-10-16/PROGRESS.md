# BENCH D0 tooling slice — progress (offline only)

Started 2026-10-15 night. Owner asleep; bridge with FOUNDRY; no live game, no ModsConfig.

## 1. `biomes_sprint` tier (modset_builder.py)
DONE. `TIERS["biomes_sprint"]` = ratchet_pilot wants + guards, plus forbids sarg.alphaanimals and
daria40k.alphaanimalspatchoutposts (Phase 0). ExplosiveGrowth guard reads Biomes.compose.json at import: not folded ->
wants mandrake.rm.explosivegrowth; folded -> forbids it. Plan (no --apply): 22 mods, all 5 DLC, no refusals.
Selftest: `src/RimMandrake/Utils/selftest_modset_biomes_sprint.py`.
Open for S0/FOUNDRY: X1's "loads before mandrake.rut.plantgrowth" needs plantgrowth in the tier; NOT added (would change
plant growth under every suite) -- decide at S0.

## 2. Preflight: Cauldron, Contagion, LeaningScrub
_pending_

## 3. Cauldron saved-site spec
_pending_

## 4. LeaningScrub lean-site item
_pending_

## Selftests
_pending_

## Left for the live round
_pending_
