# RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES

## spec
Prove Pyrelands with four dense live scenes (S1 ARRIVAL, S2 SKIES, S3 FIRE-BORN, S4 FAUNA), each with one shared
control and rows that each name the one defect that fails them alone. Plan and inventory:
`D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\Pyrelands\plan.md` and `...\inventory.md`.

## done 2026-11-12 (sha 4418fd6809)
- `_on_site` (validation.py) finds the Pyrelands map among loaded maps rather than assuming map 1 (fixes the
  third PYRELANDS_SITE_DIAGNOSE_WRONG_BIOME_TWICE failure, job J20261112T144249Z-2ac601: map 1 was RM_TheRot);
  if no Pyrelands map is found, it reports UNMEASURED SITE.
- Offline acceptance rows in selftest_pyrelands_site.py (biome_text_says_engineered, flamefang_bite_carries_venom,
  paved_strip_excised), each with a mutant that fails only that row.
- Counts over 25 acceptance lines: before 0 PROVEN / 19 WEAK / 6 NO PROOF; after 2 / 19 / 4 (offline only).

## remains
- Read the four testq results: S1 J20261112T152215Z-99d28a, S2 J20261112T152218Z-3689c8,
  S3 J20261112T152220Z-d64460, S4 J20261112T152222Z-e47f0a (SteveDesktop, sha 4418fd6809).
- Compression for burn_line, fresh_burn_bonus and embergrass_regrow (over budget at shipped timings).
- A control for fire_tick_effects.
- Designer answers to the five questions in inventory.md (worldgen switch default, paved strip leaf, season walk
  bar, furnacebeast "banks heat", dry crop on ash).
- validation.py and selftest_pyrelands_site.py read DIRTY under code_review_status: they owe a full review.
- Untraced: why the loaded game's map 1 was RM_TheRot.
