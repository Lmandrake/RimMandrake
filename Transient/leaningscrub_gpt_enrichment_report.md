# LEANINGSCRUB_GPT_ENRICHMENT_1 — report (FOUNDRY, 2026-10-01)

## built (offline, compiled clean, mod `mandrake.rm.leaningscrub`)

Each part has its own Mod Settings switch, and every switch defaults to on.

- **Dripping venomvine, timed harvest.** `RM_RegrowingHarvestExtension` (harvestAfterGrowth 0.3,
  TUNED) is applied at startup to `plant.harvestAfterGrowth`. Vanilla `Plant.PlantCollected` then
  resets the stand's growth instead of destroying it. With the setting off, the harvest destroys the
  stand again. Source: `Source/RM_VenomvineRooms.cs`.
- **Crown venomvine, Stall cloud.** `RM_MapComponent_CrownMob`: while the weather is `RM_Stall`,
  idle wild dustflutters within 40 cells fly (real flight) to the crown and settle within 3 cells,
  at most 30 per stand. The existing Stall freeze holds them there, and when the wind returns they
  disperse.
- **Runway bloom.** `RM_MapComponent_RunwayBloom` (`Source/RM_RunwayBloom.cs`). The trigger is a
  humanlike pawn, or one with body size of at least 1, moving through non-tree plants. Wild animals
  carrying `RM_RunwayBloomExtension` answer in stages: crustweevil scatters at 0 ticks, vissler
  sheds `RM_VisslerArm` (chance 0.5) and flees at 15, fuzzrunner bolts at 30, and dustflutter erupts
  into flight about 40 cells at 60. Nothing despawns. Dustflutter `MaxFlightTime` went from 2 to 6
  (TUNED to reach about 40 cells).
- **Named sweetline trees.** `RM_CompSweetlineStation` (`Source/RM_SweetlineStation.cs`) gives each
  tree a generated name (unique on the map, Scribed, shown in the label), a History gizmo of up to
  12 dated entries (named, wool shed, struck), and a snagged-wool timer: a mature tree sheds 5 giant
  wool every 5 days (TUNED). Names come from `RM_NamerSweetlineTree`, whose vocabulary is a
  PLACEHOLDER.
- Already shipped and untouched: the twitcher lash, the hollow stand's galleries and the thicket wall.

## follow-ups filed (caused-by this item)

- LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1 (BENCH/owner): the further venomvine forms.
- LEANINGSCRUB_SWEETLINE_GUARDIAN_1 (BENCH/owner): the guardian creature.
- LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1 (BENCH/owner): the naming register.
- LEANINGSCRUB_SWEETLINE_VISITORS_1 (FOUNDRY): travellers and pilgrim tokens.
- LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 (FOUNDRY): arms drawing scavengers.
- LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1 (FOUNDRY): ribbonwhip sway and exit holes.
- LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 (FOUNDRY, bridge): the live state-read proof.

## tests

- `run_selftests.py`: 78/81. The two failures are the known `selftest_sound_paths.py` and the
  Pyrelands walklint `mandrake.rm.biomes` BAD_PACKAGEID. One test was unmeasured (bridge).
- `dll_source_stamp.py check`: the LeaningScrub DLL MATCHes its sources.
