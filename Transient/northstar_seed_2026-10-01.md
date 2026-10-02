# North-star seeding pass — 2026-10-01 (NORTH_STAR_WALK_AUTHORING_1)

Owner ruling 2026-10-01: *"There will be many such mods that require a human nearby to build them
proper northstar scripts. You are mostly seeding the field right now with reasonable initial
guesses for refinement later through debugging needs or live feedback."*

Every section seeded here is `state: DRAFT` with an empty `validated-hash:` — it binds nothing.
`modcheck validate` was not run. Lines tagged `(guess)` are the least certain.

## Baseline (before any edit, worktree at origin/main b819a5d76)
- `modcheck lint`: 3 FAIL (BAD_PACKAGEID `mandrake.rm.biomes` in Cauldron/GelatinousSlime/TheForge), 12 WARN
- `floor --all`: 0 refusals among seeded mods (all DRAFT, "no bar")
- run_selftests.py: (pending)

## Batches
- run_selftests.py baseline: 100/105, 4 FAILED pre-existing (selftest_walklint, selftest_one_path_seam, selftest_sound_paths, selftest_sun_heat), 1 unmeasured

### Batch 1 — creatures (SWBestiary subject, 1,748 PNGs)
SWBestiary, SeaBeasts, SeasWaterline, Livestock, JawaIkee, HelixTellurox, BeastNorm — 7 walks.
Lint/floor: no new findings. Notable seeded question: Cindermare/Skarnix/Karrask/Tellurox each ship ONE
`Graphic_Single` texture (no facings) — seeded as a `(guess)` cannot-show for him to rule.

### Batch 2 — gear, species, droids, vehicles
Armoury, StarWarsRaces, Droidworks, KotORBandolierNorthFix, CereanManeFix, MSEDroidFix, JawaIonWeapons,
DesertVehicleReskin — 8 walks. Lint/floor: no new findings. The three single-PNG fixes get a tight
must/cannot pair naming the exact defect they repair.
