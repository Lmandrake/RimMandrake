# GREENTIDE_MECHANICS_2 offline pass — 2026-10-11 (FOUNDRY)

## status
- [x] probe: what is unbuilt — nothing offline. M1-M12 shipped; M10 + M2 suppression wired to the explosive-growth grid at 555df9b7b.
- [x] L0 checks: dll_source_stamp MATCH for EnvironmentalHazards/Greentide/CreatureBehaviors; selftests 318 PASS / 4 FAIL, none Greentide-related
- [x] rimflow implemented GREENTIDE_MECHANICS_2 --sha 555df9b7b -> built; owes A3 L1, A4-A6 L2 (bridge)
- [x] fallback slice: SCALD_MECHANICS_1 S2 steam-catch output (RUT_SteamCatch outputDef was unset)

## findings
- The item prose said the M10/M2 grid writes were no-op stubs; EXPLOSIVE_PLANT_GROWTH_1's engine landed 2026-09-26 and 555df9b7b wired both.
- Selftest failures (pre-existing, not this pass): selftest_walklint (BENCH's owner_walk_gss_flowworks_2026-10-11.md has no subject: header), selftest_art_checks (threshold drift), selftest_tool_metadata (DLL missing jawa/telemetry_mark, jawa/telemetry_tier), selftest_utinnipatches_dump (RUT_Thought_DeadDrawn not in dump).

## built (Scald S2)
- New `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_DistilledWater.xml` (Fluid food item, PROVISIONAL numbers copied from RM_MeltedWater).
- `RUT_SteamCatch` outputDef -> RM_DistilledWater (25/day, PROVISIONAL).
- TerminalBiomes validation.py: steam_catch_checks() + chain scald_steam_catch_output (falsified: removing outputDef makes it FAIL); walk line added.
- Art queued: artpipe job RM_DistilledWater (interim texPath = RM_MeltedWater jug, flagged in def header).

## owed
- Live: a condenser on a RUT_ScaldVent drops 25 RM_DistilledWater per day; refuses off-vent.
- FlowWorks pipe-water form of card 2 (BENCH/FlowWorks, not touched).
- Repoint texPath once the art job is installed.
