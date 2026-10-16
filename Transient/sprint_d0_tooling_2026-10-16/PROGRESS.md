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
northstar_plan.py already existed for all three (thin USE_SUITE=True wrappers) -- untouched.
NEW: shared rows `src/RimMandrake/Utils/northstar_driver/biome_preflight.py` (+ selftest_biome_preflight.py) and thin
wrappers `src/RimMandrake/<Biome>/preflight_<biome>.py`. Rows O-TIER, O-PLAN, O-DEPLOY (src vs deployed composite,
byte-equal), O-ROSTER, O-TEX (M2), O-SUITE (required_checks.json current + probe count), O-MANIFEST, O-SITE.
First run (2026-10-16 ~00:xx, offline, ~60 s each):
- Cauldron: O-TEX FAIL -- RM_Bezzul, RM_GiantCrownedSilkie (Phase 0 ports, no Textures in src or deployed) and the 2
  fleck overlays on RM_TreeMartyr/RM_TwistingThornwood (packet §0 confirms). The 5 dew variants are code-derived paths,
  invisible to an XML read -- still owed, not measured here.
- Contagion: O-SUITE FAIL -- required_checks.json STALE for Contagion/validation.py (FOUNDRY is editing it; rerun
  required_checks.py once its edit lands). O-TEX PASS 36/36.
- LeaningScrub: O-TEX PASS (77 OK, 1 base-game, 5 not on tier). Instrument trap found and fixed on the way:
  placeholder_lint.resolve's mask filter drops `*_m` texPaths (RSW_Anooba/RSW_Nuna read MISSING falsely).
- All three: O-MANIFEST UNMEASURED (S0 freezes `design/RimMandrake/sprint_manifests/<Biome>.json`), O-SITE UNMEASURED.

## 3. Cauldron saved-site spec
_pending_

## 4. LeaningScrub lean-site item
_pending_

## Selftests
_pending_

## Left for the live round
_pending_
