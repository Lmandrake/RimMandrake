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
