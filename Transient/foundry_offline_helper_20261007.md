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

## Helper 4 (2026-10-07)
- FEVERWOOD_BROOD_RANSOM_1 campaign half: built 81f360450, `implemented` (A1 L0; A2 L1, A3-A7 L2 owed).
  Sporefall display tank (RM_GenStep_DisplayTank on Base_Faction, faction+name gated, never rebuilt once freed), free/breach/kill
  frees with giftRolls 2 + goodwill -50 setting, Wildsteam cask stock (onlyFactions, 0.6, Expensive), deep lines comp on the cask.
  Open (noted on item): which are "the prison towns"; bigger young; raised buy-back price.
  L0: selftest_feverwood_broodcampaign.py, validate_patch clean on 613-list snapshot, run_selftests 221/222 (utinnipatches_dump only).
- Skipped on the oldest-first scan: owner/design items (RAKATAN_ARCHOTECH, MINERALS, LONGSHADE_SHADE_EXTRAS, CRACKEDLANDS_*,
  LEANINGSCRUB_SWEETLINE, FORGE_DHOKKUR, SHADECRAFT), bridge/game-up (PYRELANDS_NORTHSTAR_TRIAL, NORTHSTAR_FAST_DRIVER,
  FLOWWORKS/GRAFFITI northstar, STILLSAND_*_LIVE/REMAINDER), NORTHSTAR_ADVERSARIAL_REVIEW_1 (owner-released rounds only),
  RUSTCATHEDRAL_WORN_BIT_ARC_1 (stage 4 is the tabled Stranger's Overhaul rite).

## Helper 5 (2026-10-07) — MESSYCONDUIT_CABLE_PILE_LOOK_1 (claimed)
- Rule 1 (no orphan strip) already built + checked: ReviewRound1Checks B13 (50b906466).
- Built 8bab86beb, `implemented` (A1 L0; A2-A3 L2, A4 L4 owed). GSS selftest 803/803, run_selftests 221/222 (utinnipatches_dump only).
- Rule 2 bar CordAudit.EndsOnBodies: measured 0 faults once junction-arm/strip-socket ports count as nodes (first cut, centres only, read 123 false faults, all ends plugged into junction arms). Fray ends are NOT exempt.
- Rule 3 was a real gap: hoses rank by reel age, so a newer hose's end/joiner could draw over an older hose. HoseMath.Layer ranks an end-on-hose beneath it, drops joiners over a lower hose; probe field fittingsOnTop for L2. DLL rebuilt (not deployed).
- Skipped this pass (blocked/not offline): FEVERWOOD_HIVE_GUARD_CHAMBER_1 (build last, after the reacting hive is played), FLOWWORKS_QUARRY_DIGGING_1 remainder (waits on mineral registry + River Works), FLOWWORKS_NORTHSTAR_SHIP_1 (88 DIRTY review + deploy), pit umbrella children all built/bridge.

## Helper 6 (2026-10-07) — FLOWWORKS_SLUICE_TWO_DOORS_1 (claimed)
- FLOWWORKS_CONFINEMENT_TOGGLE_VESTIGIAL_1 stale-dropped: setting retired at cc8bbdff9.
- Skipped: FLOWWORKS_CHECKOUT_SCOPE_1 (moves chains into the live core proof the bridge agent runs), NORTHSTAR_PARTIAL_GAPS_FILL_1 (standing, "beside that mod's own build or live run").
- Built fe20a045f + DLL f056d3012, `implemented` (A1-A2 L0; A3-A4 L2 owed). No new def/setting: shut RM_Sluice seals its cell
  (RM_FlowKernel.sealedCell <- RM_FlowDoorRules.SealsLiquid <- RM_PitTrapMath.FlowDoorSeals); legacy flood refuses it; grate always passes.
  L2 already written: JawaBench playtest ScnSluice (expected-fail until this build -> should XPASS once the DLL is deployed). DLL NOT deployed.
  extension chain flow_doors: doors_pass_liquid_closed -> grate_passes_sluice_seals. Runsheet regenerated (also dropped stale toggle_confinement rows).
  C# selftest 122/122, run_selftests 221/222 (utinnipatches_dump only).
