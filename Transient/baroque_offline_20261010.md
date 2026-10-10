# Baroque offline 2026-10-10 (FOUNDRY helper)

Baroque Biomes = mandrake.rm.biomes (composed biome mods). Open offline candidates were mostly large, blocked or owner/bridge-only
(GREENTIDE_HUMMING_GROVE_1 built, owes L2/L4 live; BAROQUE_LOAD_RESIDUE_ERRORS_1 done; GLOW_TANK_SEED_LIVE_SOW_1 bridge; BEDAZZLE_TOP_SHAPE_PROGRAM_1 umbrella).

## Built
- LONGSHADE_BEDAZZLE_MECHANICS_1 haze act, a7163b849: RM_SmokeHazeCondition + RM_SmokeHazeFront incident, RM_ShadeHazeExtension
  (CreatureBehaviors), shade-grid length factor, heat-bed muffle, toggles smokeHazeFrontEnabled / smokeHazeEffectsEnabled,
  haze_problems validation + planted-defect selftest. PROVISIONAL: 1.6x shadows, 0.5 sound, 0.6 glow, 2~4 days, chance 0.5.
- 76f226278: LongShade STATIC was red because the tollok check read the removed bleedRate; now checks BloodPumping capMods.

## Owed / not built
- Ash-pulse growth + sand-lock acts (growth virtual UNMEASURED, needs Volcanic Winter decompile). L2 live check of haze.
