# FOUNDRY offline helper 2026-10-07

## ART_LEDGER_SEAT_DEFAULT_1 — done, 9c284892e
- artledger.seat(): RIMFLOW_SEAT > ART_SEAT > AGENT_SEAT > session role file, else NoSeat at write time (no silent BENCH).
- PreToolUse push guards (dll stamp, unledgered texture, ledger lint) now check the refspec source, not HEAD.
- Misfiled BENCH-shard events NOT moved: no move verb, append-only union shard, events carry seat:BENCH inside. Documented in items/closed/ART_LEDGER_SEAT_DEFAULT_1.md.

## WEEPINGSTONES_CONDENSER_QUESTS_1 — built, 1ed0cb8a3
- UtinniPatches/Patches/RUT_CondenserQuestSlots.xml: Hutt Cartel heads the buyer slot. selftest_condenser_slots.py. L1/L2 owed (bridge).

## Skipped
- All *_RITE_* items: SALVATION_RITES_UNIFICATION_1 blocked, owner 2026-10-03 "table the rites"; found-rite machinery unbuilt.
- WARLAB_CRATER_ACCIDENTAL_TRIGGER_1 blocked (design); BIOME_DEFNAME_MIGRATION_WAVE_1 needs live tile read.

## RUSTCATHEDRAL_BASE_FINISH_BUILD_1 — built, adbeaa649 (helper 2)
- All 7 parts offline: line-cycle (Hum: RM_LineCycle.cs, MTB roll in a map comp, IncidentDef baseChance 0), hum reading (trait, exposure GameComponent, bolt readout comp, RM_HumPrimer book + trait-gated recipe), coolant eel (GenStep into water, never wildAnimals), overhead sun, cooked strays, mynock row merged into the EXISTING WildAnimals_RustCathedral.xml (it already held RSW_Vozzik).
- validation.basefinish_problems + selftest_rustcathedral_basefinish.py 20/20. L1-L3 owed (bridge; art install from artpipe done/RM_CoolantEel_*, done/RM_HumPrimer).
- Judgement calls: "hum drops one band" = band-1 and one hum layer fewer (worst band unchanged); "the Scorch" has no BiomeDef, strays draw from RM_Warscar/RUT_Scarlands; "a desk" = crafting spot/tailoring benches.
- Pre-existing, not mine: validate_patch flags RM_LivingBolt corpse texPath Things/Pawn/Animal/RM_LivingBolt/RM_LivingBoltCorpse missing (pink placeholder).
- Skipped as not fully offline: PYRELANDS_SHIP_READINESS_1 (owner-present flyer frames, BARBSLINGER), NORTHSTAR_VALIDATION_SKILL_1 (no prose; skills only in curation sessions), EXCAVATION_WALL_ART_1 (art gen + wiring waits on spikes/ladder items).

## Helper 3 (2026-10-07)
- RM_LivingBolt corpse: PROVEN missing (corpseGraphicData -> RM_LivingBoltCorpse, no PNGs anywhere; PawnRenderNode_AnimalPart swaps to it on death). No render or ruling exists. Removed corpseGraphicData (dead bolt draws body) 33f8f94fc; filed LIVINGBOLT_CORPSE_ART_1.
- RM_CoolantEel: artpipe facings are byte-exact column C of owner keep fd20804b (rustcathedral sheet, row RM_CoolantEelCatch); installed via `art install --ruling`, texPath wired, drawSize 1.1 (job brief), no shadowData (as vanilla Cobra) 0c0e3584f.
- RM_HumPrimer: render exists (_artsrc/RM_HumPrimer, 0fb990d5) but NO ruling -> not installed; stays vanilla Schematic.
- RUSTCATHEDRAL_HULL_BOLTS_BUILD_1: built c5b3085d6, `implemented` (A1 L1, A2-A9 L2 owed). Oldest offline item after skips: STATUE_ART_EXPANSION_1 umbrella, SUMP_TAR_LIVING_SYSTEMS_1 + WARSCAR_AEROSOL_SCREEN_1 BLOCKED, NINEFOLD_FAVOUR_ODDS_BUILD_1 already built at aa93c306a (rite half tabled), rites skipped.
  - Boarding = prefix on GravshipUtility.GenerateGravship; vanilla capture carries pawns on substructure. Free tier only; campaign Ishko/Regard owed (hook RM_HullBolts.OnWitnessed). Hull bolt uses living-bolt texPath; _artsrc/RM_HullBolt_* unruled.
  - L0: hullbolts_problems in static_checks, selftest_rustcathedral_hullbolts.py 17/17, run_selftests 220/221 (utinnipatches_dump only). Both RustCathedral DLLs rebuilt.
