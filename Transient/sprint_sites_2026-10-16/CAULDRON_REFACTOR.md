# Cauldron onto the shared saved-site recipe

Cauldron/prep_site.py now calls Utils/modcheck/biome_site.py (b4d14d44c8) instead of its own copy (e1e5a6ff3a).
## Changed
- `Cauldron/prep_site.py`: 217 -> ~80 lines. Keeps `probe` (records the RM_CauldronVent count, never required),
  `site_problems`, `build_site_save`, its own STEPS text, `main`. Removed: pyre, _call, choose_tile, retile, census, the build body.
- `Cauldron/selftest_cauldron_site.py`: retile/choose_tile/_NS stubs now target biome_site (B), the module that owns them.
- `biome_site.py`: docstring no longer says Cauldron keeps a copy.
## Behaviour kept / differences
- Kept: step order, "nothing saved unless clean read-back + >=1 living native (MIN_NATIVES) + map biome", never overwrite,
  reload -> loadVerified registry write; preflight O-SITE still passes only on loadVerified True (untouched).
- Difference (record shape only): registry/receipt `census` was {"natives", "vents"}, now {"natives", "probe": {"vents"}}
  (same as Contagion/LeaningScrub). No reader of `census` exists outside the recipe (grepped). A probe read error in the
  shared recipe now becomes a "probe: ..." problem; Cauldron's probe never raises (vents unreadable -> None, as before).
- Cauldron's site-dir name is now `<SITE>_site` = `cauldron_site` (unchanged).
## Selftests (GREEN 6/6)
selftest_cauldron_site, selftest_cauldron, selftest_contagion_site, selftest_leaningscrub_site, selftest_test_site_saves, selftest_biome_preflight.
Still UNPROVEN live (same as the other two): build/load through the shared recipe.
