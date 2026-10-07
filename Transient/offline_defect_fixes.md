# Offline defect fixes from l1_manifest_report.md "Real findings" — 2026-10-06 (FOUNDRY helper)

## (1) CAULDRON_ENRICHMENT_VISUALS_1 A1 — dewfall saturation
- The criterion was NOT met another way: `RM_DewfallGraphicExtension` existed only in C#, and no def carried it.
- BUILT: `RM_DewfallGraphicExtension` on the spec V2 default set of five accent plants (RM_CrystalFlower,
  RM_BloodBouquet, RM_RedBugloss, RM_KeeningCordax, RM_GiantToxicFlower). Each texPath is
  `Things/Plant/RM_Dewfall/<defName>_dew`, in `src/RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml`.
- No C# change. The swap skips a missing texture without error, and the Harmony patch is not installed until a
  variant is on disk, so it stays dormant until the dew art lands. Which plants get variants is still the owner's pick.
- Item prose corrected: the green question was ruled 2026-10-03 (no-green lifts during dewfall).
- Re-implemented at the new sha, with A1's text naming the five extension carriers.

## (2) FORGE_WHITE_PLUME_FRONTS_1 A2 — plume-front defs
- The build is correct. The design deliberately reuses vanilla `GasType.BlindSmoke` and `Filth_Water`, so the
  fronts are code plus six settings and have no defs to resolve.
- A2 rewritten: get_defs resolves vanilla Filth_Water, and the six settings round-trip live through the TheForge
  script's `_raw_get`. It is re-implemented at 09ccb3ca5.
- Item prose corrected: it said "Not built: every mechanical choice open". It now records what was built and the
  four builder-chosen answers that A7 asks the owner to review.

## (3) THE_SUMP_FIRST_SCRIPT_1 A2 — stale held-def premise
- MEASURED: `validation.py` reports HELD_DEFS = 0 and SHIPPED = 81. The TheSump hold was lifted 2026-10-03 (`8cacbb66c`).
- Corrected: the item's `## criteria` section (now level-tagged), the TheSump `validation.py` docstring and one
  UNMEASURED message ("held BiomeDef"), and four lines of the walk `design/validation_walks/RimMandrake/TheSump.md`.
  The walk's north-star section is DRAFT and was not touched.
- Re-implemented at the new sha with the corrected A2.

## Noted only (rimflow note)
- GRAVSHIP_ACOUSTIC_SCANNER_1: the payload is on 3 BiomeDefs, against the item's "every biome".
- UTINNI_WORLDMAP_FLIGHT_ICON_1: RUT_Utinni is a texture folder, not a def. The deployed icon patch does not
  render live (df9370e09).

## L0 proof
- validate_patch on RM_CauldronFlora.xml: 0 errors. The 9 warnings are an install-wide packageId note plus owed
  art paths (4 fleck, 5 dew).
- selftest_cauldron 63/63. TheSump static: PASS (0 findings). Cauldron and TheForge static: rc 0.
- run_selftests: 207/211. The 4 failures are outside these files: placeholder_detect (Grey Sea placeholders
  installed), tool_metadata (DLL vs source drift), rimflow selftest_built (a concurrent write to the real
  FOUNDRY.jsonl during the run), and utinnipatches_dump (stale load-14 dump).
