# FOUNDRY queue triage 2026-10-03 (belt builder r21)

Open FOUNDRY items replayed from the ledger (`model.replay()`, key `id`), bucketed by script: blocked flag + reason, `needs`, belt-log skip list, item prose length/keywords. Heuristic first pass; the offline-buildable head was hand-checked before building.

**Total open: 376.** offline-buildable 47 · too-big 40 · art-pending 12 · owner-blocked 76 · blocked-on-item 43 · bridge/live-only 158 · stale 0

Sanity probe: GREENTIDE_ILLISK_BUILD_1 -> owner-blocked, BACTA_TANK_CORE_1 -> bridge/live-only, PIT_SUPERDEEP_COLLAPSE_1 -> owner-blocked (skip list), LANTERNDEEPS_HYDROCARBON_WAVE3_BUILD_1 -> not open (closed r20). All four as expected.

## offline-buildable (47)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-17 | `FLOWWORKS_DOOR_FAMILY_1` | proposed/offline | proposed offline, unblocked, 4971-char spec | Sluice and SecurityGrateDoor as STUFFABLE doors — cheap sluice passes liquid and |
| 2026-10-01 | `WARSCAR_SNAP_MARK_1` | proposed/offline | proposed offline, unblocked, 2917-char spec | Warscar chatrak snap (scaria incubation with visible stages) and the mark made a |
| 2026-10-01 | `WARSCAR_PILGRIM_CAMPS_1` | proposed/offline | proposed offline, unblocked, 1959-char spec | Warscar pilgrim camps (RUT): camp prefabs and journals that call AdvanceStage(Sc |
| 2026-10-01 | `REPO_RENAME_SYMLINK_RETIRE_1` | proposed/offline | proposed offline, unblocked, 3644-char spec | Retire the Rimworld -> RimMandrake symlink: repoint every old-path reference, th |
| 2026-10-01 | `NORTHSTAR_PHASE_LADDER_1` | proposed/offline | proposed offline, unblocked, 1324-char spec | North-star phase ladder standard: DRAFT, VALIDATED, WIRED, GREEN min, GREEN full |
| 2026-10-01 | `PYRELANDS_SHIP_READINESS_1` | proposed/offline | proposed offline, unblocked, 1734-char spec | Pyrelands SHIPPED rung: Ashwallow/Emberscythe art, code review CLEAN, settings g |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_SHIP_1` | proposed/offline | proposed offline, unblocked, 769-char spec | FlowWorks SHIPPED: settings superb, art complete, code review CLEAN, deployed |
| 2026-10-01 | `STILLSAND_SKELETONS_REMAINDER_1` | proposed/offline | proposed offline, unblocked, 2997-char spec | Stillsand skeletons remainder: tracks on the footprint grid + dune eraser, dune  |
| 2026-10-01 | `LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1` | proposed/offline | proposed offline, unblocked, 1130-char spec | Runway bloom visuals: ribbonwhip sway and burrower exit holes (which species bur |
| 2026-10-01 | `ABYSS_FREE_CRYPTID_1` | proposed/offline | proposed offline, unblocked, 1938-char spec | The Nhaleth: Abyss free-tier cryptid; Utinni relabels to the Forsakens (Sith whi |
| 2026-10-01 | `NORTHSTAR_COVERAGE_AUDIT_1` | proposed/offline | proposed offline, unblocked, 732-char spec | Audit the 55 existing validation.py files for coverage of intended function |
| 2026-10-01 | `NORTHSTAR_ADVERSARIAL_REVIEW_1` | proposed/offline | proposed offline, unblocked, 631-char spec | Standing: periodic adversarial and GPT review of north-star scripts |
| 2026-10-01 | `NORTHSTAR_BRIDGE_UTILIZATION_1` | proposed/offline | proposed offline, unblocked, 1359-char spec | Track live bridge utilization (active driving time over held time) as the progra |
| 2026-10-01 | `EXPLOSIVE_GROWTH_PROBE_TOOL_1` | proposed/offline | proposed offline, unblocked, 945-char spec | JawaBench probe tool so the ExplosiveGrowth script can cover harvest jackpot, cu |
| 2026-10-01 | `SLIME_SEEKER_LOAD_TOOL_1` | proposed/offline | proposed offline, unblocked, 801-char spec | JawaBench tool to load a slime seeker so the GelatinousSlime script can cover pr |
| 2026-10-01 | `NIGHTSIDEICE_HEAT_DIAL_BUILD_1` | proposed/offline | proposed offline, unblocked, 730-char spec | Nightside Ice: eviction housekeeping, heat dial and shivven breach loop |
| 2026-10-02 | `SEA_DIVE_HATCH_RETIRE_1` | proposed/offline | proposed offline, unblocked, 0-char spec | Retire RM_SeaDiveHatch: the ship flies to the RM_SeabedLayer planet layer instea |
| 2026-10-02 | `HOIST_FIXED_SITE_FRAMES_1` | proposed/offline | proposed offline, unblocked, 1112-char spec | Fixed hoist head-frames placed only by site gensteps, plus the sealed holder-fea |
| 2026-10-02 | `HOIST_SHIP_PART_BUILD_1` | proposed/offline | proposed offline, unblocked, 1845-char spec | Keel hoist as a gravship part: items, awake colonists, downed beasts captured on |
| 2026-10-02 | `HUTT_SLAVE_PIT_TEST_SITE_1` | proposed/offline | proposed offline, unblocked, 1912-char spec | Hutt slave pit at a small stand-alone test site: sell slaves, prisoners and down |
| 2026-10-02 | `HUTT_LOTTERY_CHUTE_BUILD_1` | proposed/offline | proposed offline, unblocked, 1096-char spec | Hutt chance chute: stake goods, slaves or beasts; house cut; value-matched crate |
| 2026-10-02 | `PYRELANDS_LIGHTNING_BREAKER_BUILD_1` | proposed/offline | proposed offline, unblocked, 2002-char spec | Pyrelands: lightning breakers (metal+sand forge recipe, learnable only in the Py |
| 2026-10-02 | `PYRELANDS_ULLAI_GIANT_BUILD_1` | proposed/offline | proposed offline, unblocked, 1487-char spec | Pyrelands: the ullai herd and the furnace-beast grown into a giant |
| 2026-10-02 | `NORTHSTAR_VALIDATION_SKILL_1` | proposed/offline | proposed offline, unblocked, 0-char spec | Carve a northstar-validation skill out of rimworld-debug-testing: bland saved wo |
| 2026-10-02 | `SUMP_FREE_TIER_MOVE_BUILD_1` | proposed/offline | proposed offline, unblocked, 1835-char spec | Sump: move all 24 Sep content (tar coating, tarred, solvents, walkways, gaslight |
| 2026-10-02 | `SUMP_CAPSTAN_TURRET_BUILD_1` | proposed/offline | proposed offline, unblocked, 2256-char spec | Sump: the capstan turret, a turret on Melee Animation's lasso pull, learned at t |
| 2026-10-02 | `LASSO_CHERRYPICKER_REMOVAL_1` | proposed/offline | proposed offline, unblocked, 1513-char spec | Remove lassos: Cherry Picker cut AM_LassoCloth + Melee Animation lasso spawning  |
| 2026-10-02 | `SUPERDEEP_PRISON_ROOM_1` | proposed/offline | proposed offline, unblocked, 2324-char spec | An enclosed superdeep area is a room; a prisoner bed makes it a prison; capture  |
| 2026-10-02 | `PIT_TEMPERATURE_SOFTENING_1` | proposed/offline | proposed offline, unblocked, 1530-char spec | Pit temperature couples hard to ambient and wears down resistance; Exposed Priso |
| 2026-10-02 | `DEPTH_FILL_COST_MATRIX_1` | proposed/offline | proposed offline, unblocked, 1098-char spec | Path cost as a depth × fill-tier matrix so flooded is always slower than dry |
| 2026-10-02 | `LIQUID_BODY_FLUID_IDENTITY_1` | proposed/offline | proposed offline, unblocked, 3821-char spec | Fluid identity per liquid body (retire per-map ActiveFluid); the merge rule |
| 2026-10-02 | `PIT_FILL_EFFECTS_1` | proposed/offline | proposed offline, unblocked, 1665-char spec | What a fluid does to a pit occupant: drowning at D=4, poison keyed to fill, burn |
| 2026-10-02 | `PIT_DEPTH_DRAW_OFFSET_1` | proposed/offline | proposed offline, unblocked, 1240-char spec | Pawns visibly sink and rise with canal depth; superdeep walls 20% above the head |
| 2026-10-02 | `FEVERWOOD_ANT_THEFT_RAIDBACK_1` | proposed/offline | proposed offline, unblocked, 4779-char spec | Fever Wood: kurreth carry thornbugs off alive; letter, track, column camp and hi |
| 2026-10-02 | `FEVERWOOD_DIANOGA_GIANT_MAP_1` | proposed/offline | proposed offline, unblocked, 3226-char spec | Fever Wood campaign: map the dianoga over all six sekkulaath limbs, not just the |
| 2026-10-02 | `FEVERWOOD_OIL_BOIL_WEATHER_1` | proposed/offline | proposed offline, unblocked, 4076-char spec | Fever Wood weather: the oil boil (hot still days, doubled seep oil, spark flash  |
| 2026-10-02 | `WEEPINGSTONES_CONDENSER_QUESTS_1` | proposed/offline | proposed offline, unblocked, 3581-char spec | Walking condenser quests: Hutt capture for the Arena, or Moisture Farmers keep i |
| 2026-10-02 | `WEEPINGSTONES_REFUSED_TOLL_RITE_1` | proposed/offline | proposed offline, unblocked, 3617-char spec | The Refused Toll, for Mob'Unloo: draw at an Imperial metering station and walk a |
| 2026-10-02 | `ALPHA_ANIMAL_PORTS_REHOME_1` | proposed/offline | proposed offline, unblocked, 0-char spec | Five Alpha Animals creatures have RSW_-prefixed ports (Wildpawn=RSW_Durrok, Wild |
| 2026-10-02 | `MIASMA_MOTHERS_PRICE_1` | proposed/offline | proposed offline, unblocked, 1772-char spec | Miasma giant: the mother's price (sell a stranded young and she never forgives;  |
| 2026-10-02 | `MIASMA_DECAY_CELLS_1` | proposed/offline | proposed offline, unblocked, 2211-char spec | Miasma tech: decay cells, a learned generator making power from rot; spent cells |
| 2026-10-02 | `MIASMA_ROTTING_BED_CUISINE_1` | proposed/offline | proposed offline, unblocked, 2059-char spec | Rotting bed (spent decay cell) grows a Star Wars Cuisine ingredient (mandrake.rs |
| 2026-10-03 | `STARWARS_JUNK_RESKIN_1` | proposed/offline | proposed offline, unblocked, 1112-char spec | Reskin vanilla ancient junk (cars, tanks, walkers, dropships) as Star-Wars-adjac |
| 2026-10-03 | `FEVERWOOD_HIVE_GUARD_CHAMBER_1` | proposed/offline | proposed offline, unblocked, 928-char spec | Ant hive kept guard at the chokepoints: invent the guard creature, station it wh |
| 2026-10-03 | `FLAME_STATUES_MOD_BUILD_1` | proposed/offline | proposed offline, unblocked, 0-char spec | Statue spec steps 4-7: mandrake.rm.flamestatues (three Chemfuel flame statues, R |
| 2026-10-03 | `UNFINISHED_LINE_TITHE_BEAT_1` | proposed/offline | proposed offline, unblocked, 824-char spec | Unfinished Line beat 4 The Tithe and the Hands: scaled material tithe to the sit |
| 2026-10-03 | `UNFINISHED_LINE_WORLD_FOUNDRY_1` | proposed/offline | proposed offline, unblocked, 1020-char spec | Unfinished Line runs in the world (Q1=A): Enclave regrowth, Foundry-grade frames |

## too-big (40)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-08-30 | `VAULT_DUNGEON_BUILD_1` | doing/offline | doing umbrella/kit (36053-char prose), partly built | Build the six Forsaken vaults: concentric grammar templates, LARGE maps, quickte |
| 2026-08-31 | `TILE_STRUCTURE_DESIGNS_1` | doing/offline | doing umbrella/kit (92806-char prose), partly built | Make and improve the promise/whisper structure designs per the roster (22+22): r |
| 2026-09-06 | `ANCIENT_WAR_LAB_1` | doing/offline | doing umbrella/kit (11439-char prose), partly built | The war lab beneath the propane lake over the Impact Site — submerged dungeon, l |
| 2026-09-07 | `MIASMA_MECHANICS_1` | doing/offline | doing umbrella/kit (86402-char prose), partly built | Miasma C# kit: surge/salt-line system (fresh-brine map axis, storm-driven moveme |
| 2026-09-07 | `SUMP_MECHANICS_1` | doing/offline | doing umbrella/kit (84062-char prose), partly built | Sump C# kit: poured tar moat + command ignition (smoke wall), dig-lottery tables |
| 2026-09-07 | `FORGE_MECHANICS_1` | doing/offline | doing umbrella/kit (57263-char prose), partly built | Forge C# kit: boiling-rain weather (scald, flash cycle, flash-interval growth),  |
| 2026-09-07 | `SCALD_MECHANICS_1` | doing/offline | doing umbrella/kit (43498-char prose), partly built | Scald C# kit: steam-catch industry, margin fishing + bath recreation, bubble-sai |
| 2026-09-13 | `CATHEDRAL_REGARD_BLACKBOARD_1` | doing/offline | doing umbrella/kit (14582-char prose), partly built | Cathedral Regard counter + stage machine + exposure pressure on the GM blackboar |
| 2026-09-13 | `CATHEDRAL_EXPOSURE_COMPLETION_1` | doing/offline | doing umbrella/kit (10459-char prose), partly built | The A6 pyrrhic discovery ending: witnessed fall, warzone flip, priced Hutt extra |
| 2026-09-13 | `GM_BLACKBOARD_SHADOW_M4_1` | doing/offline | doing umbrella/kit (9848-char prose), partly built | Build M4: Imperial Heat + orbital-detection timer + dark-tile pause as a Python  |
| 2026-09-14 | `GREENTIDE_MECHANICS_2` | doing/offline | doing umbrella/kit (70795-char prose), partly built | The Greentide C# kit build: wet-bulb condition+gear, dry-air blower, steam devil |
| 2026-09-14 | `SCARLANDS_MECHANICS_2` | doing/offline | doing umbrella/kit (33243-char prose), partly built | The Scarlands C# kit build: Scarlands mark hediff+severity floor, plated-grazer  |
| 2026-09-14 | `FIREHAWK_FLIGHT_BEHAVIOR_1` | doing/offline | doing umbrella/kit (17328-char prose), partly built | FireHawk and all flying fauna get donor-style flight animation |
| 2026-09-16 | `FLOWWORKS_BUILD_PROGRAM_1` | doing/offline | doing umbrella/kit (18435-char prose), partly built | FlowWorks - the phased build program for one liquid mod built on excavation dept |
| 2026-09-17 | `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` | doing/offline | doing umbrella/kit (22215-char prose), partly built | AtmosphericBase (mandrake.rm.atmosphericbase): the ambient framework the gods sp |
| 2026-09-18 | `FULL_LOAD_RESIDUE_TRIAGE_1` | doing/offline | doing umbrella/kit (26691-char prose), partly built | Full-list load residue beyond the FlowWorks water fix: RSW patch failures, RSW_* |
| 2026-09-19 | `CUT_FALLOUT_GENERATED_DATA_1` | doing/offline | doing umbrella/kit (15454-char prose), partly built | Load C fallout from the Caverns + Polluted Lands cuts (MEASURED 2026-09-19, Tran |
| 2026-09-23 | `GREENTIDE_TERROR_REPLACEMENT_1` | proposed/offline | prose 8905 chars, multi-mechanism | Something new and terrifying for the Greentide, replacing the dianoga |
| 2026-09-24 | `SUMP_TAR_NASTINESS_1` | doing/offline | doing umbrella/kit (13320-char prose), partly built | Sump nastiness mechanics: sticky tar overlay on any terrain, tarred-pawn hediffs |
| 2026-09-24 | `SUMP_WALKWAYS_1` | doing/offline | doing umbrella/kit (10197-char prose), partly built | Sump walkways, two tiers: duckboards (cheap, foul with tar, burn) and glasswalk  |
| 2026-09-25 | `SALVAGE_WRECKAGE_EVERYWHERE_1` | proposed/offline | multi-part / no spec; split before building | Salvage wreckage across the planet: wreck families (hulls, tanks, frames, speede |
| 2026-09-25 | `STATUE_ART_EXPANSION_1` | proposed/offline | multi-part / no spec; split before building | Statue expansion: assess the statue-choice mod (patch vs own), RM statues with f |
| 2026-09-27 | `SURFACE_RIVER_WEIRS_1` | proposed/offline | multi-part / no spec; split before building | Port the weir / bank-works / breach system to ordinary surface river tiles (owne |
| 2026-10-01 | `ABYSS_LIGHTFALL_BROOD_WRECK_1` | proposed/offline | prose 9751 chars, multi-mechanism | Lightfall's bottom: the dragons' brood and the wreck that repairs your ship |
| 2026-10-02 | `SUMP_SINKING_RITE_BUILD_1` | proposed/offline | prose 8270 chars, multi-mechanism | Sump Rite A, the Sinking: one valuable into the tar; Heat down, fewer raids, cla |
| 2026-10-02 | `WEBWORK_DEAD_GIANT_BUILD_1` | proposed/offline | multi-part / no spec; split before building | Webwork giant: wrapped urraveth skeleton, read bone by bone, loaded bones creak  |
| 2026-10-02 | `WEBWORK_TRACTION_LANCE_BUILD_1` | proposed/offline | multi-part / no spec; split before building | Traction lance: capstan sibling on one shared pull, learnable at Webwork or Sump |
| 2026-10-02 | `GREENTIDE_BASE_PORT_BUILD_1` | proposed/offline | prose 7861 chars, multi-mechanism | Greentide free tier gets Roil, Breaklight, wet-bulb, dry-air blower, root causew |
| 2026-10-02 | `GREENTIDE_THURROCK_HERD_BUILD_1` | proposed/offline | prose 6974 chars, multi-mechanism | The thurrock: tree-felling giant herd on the built Shatterer aura (no moult) |
| 2026-10-02 | `GREENTIDE_STELLOCK_LACE_BUILD_1` | proposed/offline | prose 6027 chars, multi-mechanism | Stellock lace: study a self-sealing branch, craft a cartridge that stops all ble |
| 2026-10-02 | `GREENTIDE_CEDED_ROOM_RITE_1` | proposed/offline | prose 7159 chars, multi-mechanism | The Ceded Room, for Ozzik: cede a room built outside the ship to the jungle; sca |
| 2026-10-02 | `WARSCAR_OPEN_BOAST_RITE_1` | proposed/offline | prose 6120 chars, multi-mechanism | The Open Boast, for Ozzik, found in the Warscar: a public boast, a warned challe |
| 2026-10-02 | `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` | proposed/offline | prose 9942 chars, multi-mechanism | Rust Cathedral: line-cycle, hum reading, living coolant eels, overhead-sun heat, |
| 2026-10-02 | `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1` | proposed/offline | prose 6615 chars, multi-mechanism | Rust Cathedral giant: the borehulk, a colossal peaceful mining droid with a worn |
| 2026-10-02 | `RUSTCATHEDRAL_WORN_BIT_ARC_1` | proposed/offline | prose 12928 chars, multi-mechanism | The Worn Bit: unbolt the borehulk's drill, Junkers refurbish it, restore the gia |
| 2026-10-02 | `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1` | proposed/offline | prose 8986 chars, multi-mechanism | Hull bolts: living bolts ride the ship for good as hull pets and the Cathedral's |
| 2026-10-02 | `RUSTCATHEDRAL_MENDING_WELD_RITE_1` | proposed/offline | prose 6844 chars, multi-mechanism | The Mending Weld, for Rekko: rebuild a broken stretch of old structure into a wh |
| 2026-10-02 | `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` | proposed/offline | prose 7912 chars, multi-mechanism | The Stranger's Overhaul, for Ohm: repair a free droid, capture it mid-repair or  |
| 2026-10-02 | `FEVERWOOD_RM_CAST_COMPLETION_1` | proposed/offline | prose 7469 chars, multi-mechanism | Fever Wood: build the seven ratified creatures; the skreth brood as the free sec |
| 2026-10-02 | `FEVERWOOD_BROOD_RANSOM_1` | proposed/offline | prose 6528 chars, multi-mechanism | Fever Wood giant story: ransom of its young (world tally, release gift, young ca |

## art-pending (12)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-14 | `BACTA_TANK_ART_1` | doing/offline | art job (generate/judge/wire) | Bacta tank art from the ESB canon image (tall 2:1 cylinder, translucent pale-blu |
| 2026-09-20 | `COMMISSION_LEDGER_CLEANUP_1` | doing/offline | art job (generate/judge/wire) | 85 genuinely-owed new-art/def commissions from the 118-row ledger |
| 2026-09-22 | `STONEBACK_BOKKA_ART_STANDARD_1` | doing/offline | art job (generate/judge/wire) | Judge the bokka's 2026-09-11 ported art against modern standards before regenera |
| 2026-09-27 | `SPECULATIVE_ART_COMMISSION_1` | proposed/offline | art job (generate/judge/wire) | Speculative art commission 2026-09-27 (owner directive, free pipeline) |
| 2026-09-30 | `WASTELAND_GPT_ENRICHMENT_1` | doing/offline | art not landed | Wasteland enrichment (GPT consult 2026-09-30, owner-picked by card): named storm |
| 2026-10-01 | `CONTAGION_GROWN_LIMBS_ART_1` | doing/offline | art job (generate/judge/wire) | Art for Pillar Arm and Lash (replace Anomaly placeholder textures) plus item ico |
| 2026-10-01 | `STILLSAND_SAND_SIEVE_CHORE_1` | doing/offline | art not landed | Stillsand sand sieve as a pawn chore: glass sand to fine sand with a carried sie |
| 2026-10-01 | `STILLSAND_GEOPHONE_1` | doing/offline | art not landed | Stillsand biosilica geophone: rumble markers from the sand-swim query |
| 2026-10-01 | `ABYSS_FREE_TIER_BODY_1` | proposed/offline | art job (generate/judge/wire) | Abyss free-tier body: own labels, wire 12 done crags art sets, guard/own 8 flora |
| 2026-10-02 | `EXCAVATION_WALL_ART_1` | proposed/offline | art job (generate/judge/wire) | Wall-face art for all four depths, spikes and ladder (Quarry perspective) |
| 2026-10-02 | `GELATINOUSSLIME_KIT_ART_1` | doing/offline | art job (generate/judge/wire) | Slime: real art for the whole free kit, replacing the vanilla tortoise/grass/bus |
| 2026-10-02 | `MIASMA_WARDEN_MOTHER_ART_1` | doing/offline | art job (generate/judge/wire) | Warden mother art, with an aged variant for her last season |

## owner-blocked (76)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-08-30 | `ASSAILANT_DUNGEON_BUILD_1` | doing/offline | blocked: re-verified 2026-09-26: design/Jawa/reconciled_lore/FUTURE_VECTORS.md still states creative lock-in owed with  | Build the Assailant flesh dungeon: frozen first-impact complex, thaw-gated, deep |
| 2026-09-01 | `TECHPRINT_FACTION_GATING_1` | doing/owner | belt skip list | Code the four research access classes: common / faction-held techprints / jawa-s |
| 2026-09-02 | `HELIX_TELLUROX_BUILD_1` | doing/offline | blocked: live spawn+corpse-gen proof done clean on canonical save (screenshot+get_cell_info confirmed); HorrorWastes wi | Build Tellurox, Ascendant Helix labour-line livestock |
| 2026-09-02 | `RIVER_STEAM_ANIMATION_1` | doing/offline | blocked: Still needs a live bridge screenshot of a Pyrelands-river map (render-void trap) or an owner glance at a real  | Animated steam rising from the rivers (Pyrelands weather visual) |
| 2026-09-05 | `PLOT_MECHANISM_MODS_WAVE_1` | doing/offline | blocked: re-confirmed 2026-09-26: rules 5/7/8 need cross-mod API reads (tributedemand/RumorHasIt/Ninefold) RimSage cann | Build wave: LLM raid-redesigner + post-battle/event hostility creation + plot-ga |
| 2026-09-06 | `TREE_GRAPHICS_OWNERSHIP_1` | doing/offline | blocked: true blocker moved and was never synced: commit c8b4ad38 (2026-09-09) found 14 recovered sweetline-tree art ca | Own tree art at our scales: generate custom tree graphics (sweetline trees first |
| 2026-09-06 | `HORRORS_RAIDING_FACTION_1` | doing/offline | blocked: owner ruled 2026-09-09: hold the WHOLE item until HORRORWASTES_BIOME_DISSOLVE_1's owner-reviewed tile-reassign | Horrors become a RAIDING faction (no settlements, nightside-gated encounters) +  |
| 2026-09-06 | `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` | ready/bridge | blocked: Step 1 census already flagged superseded (2026-09-08: checked-in world/ASHKARR_WORLDMAP_mutators.csv commit 20 | Put the unused tile mutators and Geological Landforms landforms on the frozen wo |
| 2026-09-06 | `MACRO_GENERATOR_V0_1` | ready/owner | blocked: round-4 chooser OPTIONS already produced (1664012fd, Fable design pass) and waiting on owner ruling; also gate | Macro generator v0: ONE idea per map — chooser + plan + terrain grid, graded on  |
| 2026-09-06 | `MAPGEN_GL_SHEET_1` | doing/owner | needs owner | Map generator: 8 plans through the GL emitter, quicktest screenshots beside pain |
| 2026-09-06 | `MAPGEN_CONVERGENCE_LOOP_1` | ready/bridge | blocked: own file's 2026-09-10 correction explicitly says do not resume without a fresh ruling; today's fresh MAPGEN_GL | Map generator convergence loop: painter vs GL vs corpus, iterate until the owner |
| 2026-09-06 | `MAPGEN_PAINTER_V1_1` | doing/owner | needs owner | Map generator painter v1: organic masks, elevation→terrain bands, hydrology with |
| 2026-09-06 | `DROIDWORKS_PRIMITIVE_TIER_1` | doing/offline | blocked: Mechanics/art fully built and live-verified since 2026-09-13 (re-confirmed 2026-09-18 and again today, no regr | Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats |
| 2026-09-07 | `SHOKKWEAVE_SOLE_SOURCE_1` | doing/owner | needs owner | Shokkweave economy: rename hyperweave game-wide, strip it from EVERY trader stoc |
| 2026-09-09 | `LANDMARK_NAMING_PASS_1` | doing/game-up | blocked: Fully resolved offline: rename tool (jawa/world_landmark_rename) is fixed, deployed, and proven live per 2026- | Review B2: 32 landmark names reused (worst 'Dead Sarlacc' x7) — hand-name the ~1 |
| 2026-09-09 | `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` | doing/owner | needs owner | Widen base RM Graffiti scope: punk/urban graffiti register + ideoligion-inspired |
| 2026-09-10 | `CRYPTOFORGE_HARVEST_RETIRE_1` | doing/offline | blocked: Steps 1-3 and 5 all complete; step 4's ModsConfig removal is also already done (614-mod live list, verified).  | Harvest then retire VQE Cryptoforge: (1) reproduce the 18 SALVAGE_PALETTE-cited  |
| 2026-09-11 | `FAUNA_TOLERANCE_NORMALIZATION_1` | doing/offline | blocked: Offline half DONE (Law 5 + MEASURED census, 196/297 violate). Blocked on the post-restore live harvest for con | Return to canonical-graph fauna normalization, now biome-aware: wide temperature |
| 2026-09-12 | `FASCINATING_WORLD_JUNK_1` | doing/owner | needs owner | Reskin and re-text every map-scatter wreck (tanks, trucks, cars, ancient junk) i |
| 2026-09-12 | `MOD_VALIDATION_RETROFIT_1` | doing/offline | blocked: still correctly blocked: sole gate is owner ratifying the modcheck sheet FORMAT (Transient/modcheck/Pits_20260 | modcheck full retrofit wave: every shipped mod gets a validation.steps.yaml and  |
| 2026-09-13 | `BAZAAR_DISPLACEMENT_PASS_1` | proposed/owner | blocked: precondition unmet: Bazaar slices 1-2 not live-proven yet (WINDOW_GRID needs deploy, PRICE_ENGINE BLOCKED) — p | Retire Trade UI Revised + Utility Columns + VTE from the campaign list after Baz |
| 2026-09-13 | `FLORA_LEGIBILITY_BAR_1` | doing/offline | blocked: Spec steps 1/2/4 (owner grades the flora sheet, fit the flora model from those grades, A/B borderline processi | Flora legibility bar: own grading pass + model (no keyline law), sizeBin-scaled  |
| 2026-09-13 | `CANON_CREATURE_REGEN_1` | doing/owner | needs owner | Regenerate every SW-canon creature from library guidance (gated on CANON_REFEREN |
| 2026-09-17 | `BARBSLINGER_SCORPION_REDESIGN_1` | doing/owner | needs owner | Barbslinger redesigned: yellowish large scorpion-like creature, bulbous domed bo |
| 2026-09-17 | `PIT_SUPERDEEP_COLLAPSE_1` | proposed/offline | belt skip list | Collapse the pit onto the D/F primitive: a superdeep cell you cannot climb out o |
| 2026-09-19 | `ROT_FAUNA_KIN_WIRING_1` | proposed/deploy | blocked: Owner ruled 2026-09-18: no race def is patched until BMT_FAUNA_ABSORPTION_1 renames the BMT_ rows  | Wire the ruled Rot fauna kin/alarm table onto the 16 race defs (UtinniPatches, F |
| 2026-09-19 | `REBOOT_BREAKGLASS_VERIFY_1` | proposed/offline | blocked: needs a deliberate Windows reboot + owner's phone over cellular, at a moment he chooses to lose the fleet for  | Verify the break-glass path survives a Windows reboot: WSL Keepalive must bring  |
| 2026-09-20 | `DONOR_DEFS_PORT_TO_OURS_1` | ready/owner | blocked: spec explicitly forbids starting solo: needs owner-sat plan/ordering first  | Port EVERY donor def we use to our own thing defs - owner ruling 2026-09-20; two |
| 2026-09-20 | `DESERT_FAMILY_PORT_EXECUTION_1` | proposed/offline | blocked: Nothing offline left for FOUNDRY (probe 2026-10-03): defs ported; all 218 desertport artpipe jobs are in done/ | Port all 109 desert-family species to our own defs and our own art - owner ruled |
| 2026-09-21 | `WORLD_LABEL_SIZE_HIERARCHY_1` | doing/owner | needs owner | All 71 world features sit at the maxDrawSizeInTiles floor - owner ruled size the |
| 2026-09-21 | `FEATURE_DRAWCENTER_UNVERIFIED_1` | doing/owner | needs owner | Only 2 of 71 world features have a verified drawCenter, and growing labels make  |
| 2026-09-23 | `HOSTILE_MOBILE_PLANTS_1` | doing/offline | blocked: Item's own spec (step 1) says design sitting first, author nothing before it: 2 of 5 questions still fully uns | Hostile mobile plants as animals - a new creature class |
| 2026-09-23 | `GREENTIDE_HUMMING_GROVE_1` | doing/owner | needs owner | A grove that hums at differing pitches as you walk through it |
| 2026-09-23 | `FEVERWOOD_ANT_HIVE_DUNGEON_1` | doing/offline | belt log: blocked | Ant hives are reactive procedural dungeons |
| 2026-09-24 | `FORCE_DISTURBANCE_REFLAVOR_1` | doing/owner | needs owner | Reflavor vanilla psychic assault/drone storm events as disturbances in the Force |
| 2026-09-25 | `REGROWTH_RECOLOR_MINEABLES_NRE_1` | doing/offline | blocked: Real trace (Transient/Player.log.geneticrim_ctor_nre_2026-09-25 L11288-92, and 09-24 before_bacta_swap L14377- | Every full-list save load logs 'Exception from long event: NullReferenceExceptio |
| 2026-09-26 | `SUMP_TAR_LIVING_SYSTEMS_1` | proposed/owner | blocked: needs owner: pacing numbers (growth rate/re-route delay/migration speed) explicitly unruled, item says owner-r | Living-map responders; tar rain mod-vs-scenario split |
| 2026-09-26 | `BIOME_DEFNAME_MIGRATION_WAVE_1` | proposed/offline | blocked: Re-verified 2026-09-28 on a fresh 630-mod bridge-ready load: still cannot get live tile counts, but the reason | Three biomes renamed 2026-09-26 carry defNames that no longer match their labels |
| 2026-09-26 | `SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1` | doing/offline | blocked: Owner already ruled (BENCH note 2026-09-26T23:24:03Z on this item) that this caching defect is fixed by replac | One gravship can only ever visit ONE sea floor: MapPortal caches its pocket map, |
| 2026-09-28 | `WASTELAND_MECHANICS_BUILD_1` | doing/offline | blocked: Middenshell footprint + plasma-storm gate + storm names need owner/design calls  | Build the Wasteland mechanics: 20-cell Middenshell on TitanicCreatures, processo |
| 2026-09-28 | `CRACKEDLANDS_FULL_RENAME_1` | doing/owner | blocked: owner call needed on how to handle the 44 live world tiles currently on RM_FloodedCanyon before the defName re | Full rename FloodedCanyon -> CrackedLands everywhere: defs, code, file names, do |
| 2026-09-30 | `SOLAR_HEAT_EXPOSURE_1` | doing/offline | blocked: Offline build complete; needs Long Shade quicktest (game-up) + owner-watched strictness sitting  | Planet-wide sun heat: sun exposure feeds VANILLA heat (no new heat kind), per-bi |
| 2026-09-30 | `LONGSHADE_BEDAZZLE_MECHANICS_1` | doing/offline | blocked: Offline tranches done; needs quicktest (game-up), smoke calendar, audio, owner tuning  | Long Shade bedazzle mechanics: golden-hour perpetual sunset + pinned sun angle,  |
| 2026-09-30 | `LONGSHADE_BEDAZZLE_CONTENT_1` | doing/offline | blocked: Remaining parts need art (gloomcast, 3 magenta), mechanics pairing (mirrak), owner review sheet (fills)  | Long Shade bedazzle content: wire the finished-but-unwired art (7 magenta creatu |
| 2026-09-30 | `WARCASKET_WASTE_RUN_REMAINDER_1` | proposed/owner | blocked: Needs owner rulings, nothing buildable from specs: (1) waste-run five destinations (wasteland.md s10) have no  | Cask-bay follow-ons: five waste-run destinations, Stenchlands cask item, Junker  |
| 2026-10-01 | `WATCHER_CREATURES_MOD_1` | proposed/owner | needs owner | Watchers mod: cross-biome shy creatures that sit, poke out, watch, and jerk away |
| 2026-10-01 | `CRACKEDLANDS_LEDGES_OF_MERCY_1` | proposed/owner | needs owner | Ledges of Mercy (from CRACKEDLANDS_GPT_ENRICHMENT_1 §1): refuge ledges, carvings |
| 2026-10-01 | `CRACKEDLANDS_FIVE_BEATS_AUDIO_1` | proposed/owner | needs owner | Bespoke audio for the five beats (6 SoundDefs on vanilla-clip placeholders) + th |
| 2026-10-01 | `CRACKEDLANDS_THREE_HEIGHT_FLORA_1` | proposed/owner | needs owner | Qirra mats + talus clasps (names swept clean): art to review sheet before defs;  |
| 2026-10-01 | `CRACKEDLANDS_SALVAGE_CLAIM_CREW_1` | proposed/owner | needs owner | Floodline salvage claim stakes + rival crew visitor lord (scatter already built) |
| 2026-10-01 | `CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1` | proposed/owner | needs owner | Peakstorm Light: dust briefly reverses (no WeatherDef field; overlay vs mote eve |
| 2026-10-01 | `CRACKEDLANDS_WOOLAMANDER_FLIGHT_1` | proposed/owner | needs owner | RSW_Woolamander is a ruled Cracked Lands flier-commuter but has no MaxFlightTime |
| 2026-10-01 | `CAULDRON_ENRICHMENT_VISUALS_1` | proposed/owner | needs owner | Cauldron enrichment visuals: dewfall chemical beads, dewfall plant saturation, a |
| 2026-10-01 | `FORGE_KEELWORK_REMAINDER_1` | doing/owner | needs owner | Floatstone keelwork remainder: glassy ring at launch, brace art, and whether pay |
| 2026-10-01 | `FORGE_VOICES_AUDIO_1` | ready/offline | blocked: placeholder retints already in place; bespoke clips need owner audio source  | Bespoke audio for the four voices of the Forge (vanilla clips retinted as placeh |
| 2026-10-01 | `FORGE_WHITE_PLUME_FRONTS_1` | doing/owner | needs owner | White plume fronts: moving quench-steam fronts that obscure shooters, soak groun |
| 2026-10-01 | `FORGE_SKY_PASTURES_1` | doing/owner | needs owner | Sky pastures: render the vapour-column grid, ash spirals, column-aware hunting a |
| 2026-10-01 | `FORGE_DHOKKUR_WAYS_1` | proposed/owner | needs owner | Dhokkur ways: outcrop disguise clues, rain-wake groan, path memory on glass-poli |
| 2026-10-01 | `FORGE_DHUVVOX_SWARM_REMAINDER_1` | doing/owner | needs owner | Dhuvvox clock remainder: nodules as Things vs sealed pawns, swarm aggregation, s |
| 2026-10-02 | `NINEFOLD_FAVOUR_ODDS_BUILD_1` | proposed/offline | a found-rite: no rite machinery in src; SALVATION_RITES_UNIFICATION_1 needs owner | Build Nine Faults (fresh-find rite, Rekko to Zizzik), the Left Behind transfer ( |
| 2026-10-02 | `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` | proposed/offline | a found-rite: no rite machinery in src; SALVATION_RITES_UNIFICATION_1 needs owner | Lantern Deeps: The Answering, Ohm's found settlement rite (campaign) |
| 2026-10-02 | `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` | proposed/offline | a found-rite: no rite machinery in src; SALVATION_RITES_UNIFICATION_1 needs owner | Pyrelands: The Struck Glass rite for Zizzik (stamped lightning-glass ring, rando |
| 2026-10-02 | `SUMP_EFFIGY_RITE_BUILD_1` | proposed/offline | a found-rite: no rite machinery in src; SALVATION_RITES_UNIFICATION_1 needs owner | Sump Rite B, Mob'Unloo's Price: good thing + hated effigy; Empire held off 5x on |
| 2026-10-02 | `WEBWORK_FELLED_NOON_RITE_1` | proposed/offline | a found-rite: no rite machinery in src; SALVATION_RITES_UNIFICATION_1 needs owner | Rite: The Felled Noon for Sh'kaar (found in Webwork; fell tallest tree at noon,  |
| 2026-10-02 | `ROT_UNJOINING_RITE_1` | proposed/offline | blocked: found-rite machinery does not exist yet: no RUT_ResearchMod_GrantRite, no inscription/found-rites row anywhere | The Unjoining, for Ta'Baa: a symbiont-joined colonist purged until it dies, just |
| 2026-10-02 | `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` | doing/owner | needs owner | A titanoslime chunk opens a Forsaken vault blocked by an Assailant seal (seal do |
| 2026-10-02 | `GELATINOUSSLIME_JOINING_WATER_RITE_1` | proposed/owner | needs owner | The Joining Water rite: join hands holding slime, one person's permanent hediffs |
| 2026-10-02 | `MIASMA_RECALL_WRITTEN_OFF_RITE_1` | proposed/offline | a found-rite: no rite machinery in src; SALVATION_RITES_UNIFICATION_1 needs owner | The Recall of the Written-Off rite (Rekko): a struck-out disposal order calls a  |
| 2026-10-03 | `CHILL_DIVE_DENSITY_SAMPLER_1` | doing/owner | needs owner | Chill dive spawns obey density (not one-of-each); number set on a live walk with |
| 2026-10-03 | `SCALD_WALKING_PASTURE_1` | doing/offline | blocked: Herd, grazing exposure and crew follow/stop/back-off are built (DivingInteraction+TerminalBiomes, unproven liv | Scald bottom-walkers: a grazing herd creature first, then the Walking Pasture (c |
| 2026-10-03 | `UTINNI_DISCOVERY_ACHIEVEMENTS_1` | proposed/owner | needs owner | Utinni discovery achievements mod: surfaces every discoverable and unique mod ca |
| 2026-10-03 | `SCALD_GALLERY_SCHEMATIC_UNLOCK_1` | proposed/owner | blocked: Owner decision: the schematic must unlock something (e.g. immersion cooler recipe or Berth heat reduction) and | Return Gallery: what the immersion-engineering schematic unlocks (RM_ImmersionSc |
| 2026-10-03 | `FALL_LINE_WRECKAGE_CREATURES_PORT_1` | proposed/owner | needs owner | BMT_BunkerBug and BMT_Megapleura (Fall wreckage creatures) are absent: load Biom |
| 2026-10-03 | `GREENTIDE_ILLISK_BUILD_1` | proposed/owner | blocked: owner design: one pawn or many, how 'nearly unkillable' is expressed, commonality/band, Odyssey water interact | Build the Illisk shoal (fast, nearly unkillable except explosives); open: one pa |
| 2026-10-03 | `UNFINISHED_LINE_SITE_CHOICE_1` | proposed/owner | blocked: Q1=A (no player-owned line) vs design site B 'your colony gets the building': BENCH/owner must say whether sit | Unfinished Line site choice (where the line stands, A-D) offered at the end of b |
| 2026-10-03 | `MINDSTONE_MATRIX_KINDLED_BUILD_1` | proposed/offline | belt skip list | Mindstone matrix + the Kindled's first making: RUT_Mindstone + head casing at th |

## blocked-on-item (43)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-06 | `KYBER_TRADE_PLOT_1` | doing/offline | blocked: stale premise fixed: GM_BLACKBOARD_SHADOW_M4_1/CATHEDRAL_REGARD_BLACKBOARD_1 built the external Heat/Hutt-Inte | Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi fro |
| 2026-09-08 | `WAR_LAB_CRATER_HOOK_1` | doing/offline | blocked: wired RUT_WarLabReactorCore (CompIgniteCraterOnDestroy) + deployed; live ignition/save-load/world_commit quick | Ignition->crater world-tile mutation C# hook for the war lab, blocked on LIQUID_ |
| 2026-09-09 | `MOVING_DUNES_BUILD_1` | doing/offline | blocked: Engine is already built (~1,900 lines, dotnet build 0W/0E 2026-09-09, selftest 13/13) and not deployable-alone | Build the dunes engine per MOVING_DUNES_DESIGN.md v2 (model=opus, ~1.1-1.4k line |
| 2026-09-12 | `MOD_OPTIONS_RETROFIT_1` | doing/offline | blocked: 52 mods now carry real, compile-verified Mod Settings (was 46+3; +ShokkweaveEconomy/EggReckoning/WildsteamEggB | Superb mod-options support across ALL our mods: retrofit every shipped RimMandra |
| 2026-09-12 | `SARLACC_HABITAT_BUILD_1` | doing/offline | blocked: advanced items 4+7 of Owed list this pass (DBH thirst wiring, water_doctrine amend), commit ed5134abf; still o | Build the accepted sarlacc design (sarlacc_native_habitat_draft.md, ACCEPTED + a |
| 2026-09-13 | `CATHEDRAL_MISSION_BOON_OFFERS_1` | doing/offline | blocked: Genuinely blocked, not just offline-stuck: spec depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, still doing  | Deniably-sourced Assailant missions + Heat-gated gravtech boons |
| 2026-09-13 | `CATHEDRAL_STAGE_COMMENTARY_POOLS_1` | doing/offline | blocked: Verified offline: no RUT_HumCommentary RulePack exists anywhere in src/ yet (grep clean) — RUST_CATHEDRAL_MECH | Stage-keyed RUT_HumCommentary pools + the bans-2/6 linter gate every arc item ru |
| 2026-09-13 | `CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1` | doing/offline | blocked: Verified offline: depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, still doing — real §2 inputs unbuilt) and  | The A4 Imperial-survey misdirection quest, three branches, K2 anti-laundering |
| 2026-09-13 | `CATHEDRAL_DESCENT_REVEAL_SITE_1` | doing/offline | blocked: Verified offline: depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, still doing) and item 3 (CATHEDRAL_STAGE_C | The A7 real under-plate descent site + reveal beat + A1 Utinni-receiver lore pro |
| 2026-09-13 | `CATHEDRAL_MECHANOID_PASS_VERBS_1` | doing/offline | blocked: Verified offline: depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1) for stage+verbs source, still doing/unship | GRANT/REVOKE mechanoid-pass instrument, scoped Harmony hostility exception (C#,  |
| 2026-09-13 | `MODCHECK_DONOR_ENVIRONMENTS_1` | doing/offline | blocked: Armoury half fully resolved offline (kaitorisenkou.ModularWeapons2 + guy762.MM.KotORCore, recorded in src/RimS | MODCHECK_DONOR_ENVIRONMENTS_1 Armoury and WreckedMachines modcheck environments: |
| 2026-09-13 | `LIQUID_BOTTLE_LOOP_1` | doing/deploy | blocked: live: fill job never produces a filled bottle (4 tries, 3 pawns); revert/rot timers unbuilt so verify bar cann | Bottles as real items: fill/use/dirty/wash loop (dirty behind a toggle, default  |
| 2026-09-13 | `LIQUID_THIRST_CHAIN_1` | doing/deploy | blocked: Own spec's Watch-out: 'Depends on LIQUID_BOTTLE_LOOP_1.' Verified this session: LIQUID_REGISTRY_CORE_1 now has | Water cleaning chain crude/household/industrial wired to DBH thirst (DBHThirst M |
| 2026-09-13 | `DEBUG_ACTION_ENUM_CRASH_1` | doing/bridge | blocked: jawa/debug_action_yielders built and compiles clean (0 errors) -- root cause confirmed via RimSage: vanilla De | search_debug_actions/list_debug_action_children(Actions) crash on any broad quer |
| 2026-09-13 | `BAZAAR_PRICE_ENGINE_1` | doing/deploy | blocked: The item's own Watch-out names BAZAAR_WINDOW_GRID_1 as a dependency, and its two read-side consumers (session- | The Bazaar slice 2: read-side RM_BazaarEconomy (worldTag-seeded buckets, history |
| 2026-09-13 | `BAZAAR_HAGGLE_DUEL_1` | doing/deploy | blocked: Real dependency chain still open: BAZAAR_WINDOW_GRID_1 is 'doing' (no WindowStack.Add intercept/session object | The Bazaar slice 3: WHOLE-DEAL patience-meter haggle duel (owner: per-item rejec |
| 2026-09-13 | `BAZAAR_BANTER_LINES_1` | doing/deploy | blocked: Part A's event pool (push won/lost/crit/lockout/greeting/closing) and personality set (stingy/desperate/gullib | The Bazaar slice 5: authored banter pools (day one) + dormant claude -p Oracle c |
| 2026-09-13 | `BAZAAR_BROKER_TAB_1` | doing/deploy | blocked: Same open Bazaar dependency chain as the other two slices I checked this pass: BAZAAR_WINDOW_GRID_1 is still d | The Bazaar slice 4: bulk-liquid Broker tab — renders Liquid Logistics' tank API  |
| 2026-09-14 | `BACTA_REVIVAL_MECHANIC_1` | doing/deploy | blocked: live: toggle/window/laws pass, but heart-destroyed corpse revives into re-death (design call) and WorkGiver ne | Bacta revival of the recently dead (owner ruling: works on dead bodies IF retrie |
| 2026-09-18 | `FISH_BESTIARY_BUILD_1` | doing/offline | blocked: WS+Greentide real catches pass; Twilight tile map is 100% deep brine (unfishable), Cracked Lands/Wasteland not | Build the fish bestiary: 32 RUT_ species across 8 registers on 7 waters, per-bio |
| 2026-09-24 | `SUMP_GASLIGHT_1` | doing/offline | blocked: live: RUT_ScrubTarred consumes solvent but leaves RUT_Tarred and spawns no Sumpgas (2 runs); lamp animation/st | Sump gaslight: tar+acid reaction makes green gas (Helixien integration OK), warb |
| 2026-09-25 | `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1` | doing/offline | blocked: Blocked on FALL_LINE_ARRIVAL_MECHANISM_1's Band B flee/lurker think-tree insert, which has not landed (still u | Feral-race crash-survivor pawnkind + permanent mental-scar hediff + capture-to-s |
| 2026-09-26 | `WEBWORK_EGG_BROKER_CHANNEL_1` | doing/offline | blocked: Re-verified 2026-09-26: RM_Window_Bazaar is still an inert Dialog_Trade subclass with no WindowStack.Add Harmo | Add the egg black-market broker channel as a Bazaar tab, once Bazaar has tabs |
| 2026-09-28 | `CONTAGION_MECHANICS_BUILD_1` | doing/offline | blocked: Remaining: limbs need per-limb design + art + Monstrous sample grade; sound assets; live verify  | Build the Contagion mechanics: Burn/Bloom weather + tells, the Coalescence (one  |
| 2026-09-28 | `WARLAB_CRATER_ACCIDENTAL_TRIGGER_1` | proposed/offline | blocked: needs the Route-1 arming design first, per its own title -- a deliberate arming sequence is a creative/gamepla | RUT_WarLabReactorCore's CompIgniteCraterOnDestroy fires the planet-wide Chill cr |
| 2026-09-28 | `BLUEDESERT_MECHANICS_BUILD_1` | doing/offline | blocked: Offline tranches done; remaining parts need valve decision, quarry tableaus, Horrors item, Harmony tint, audio | Build the Blue Desert mechanics: vhaulk trigger-gated detonation (EMP-on-hit tra |
| 2026-09-28 | `CRACKEDLANDS_RULED_CONTENT_1` | doing/offline | blocked: defs+roster complete and validated (0 errors); remaining is a live quicktest verify pass (needs deploy+bridge) | Build the Cracked Lands ruled content: roster surgery (vanilla zoo out, RM_ migr |
| 2026-09-28 | `CRACKEDLANDS_MECHANICS_BUILD_1` | doing/offline | blocked: Remaining parts need FlowWorks changes, art, audio; tranche 1 landed  | Build the Cracked Lands mechanics: the Swale (FlowWorks-normal, Utinni-locked bi |
| 2026-09-29 | `CAULDRON_MECHANICS_BUILD_1` | doing/offline | blocked: Remaining parts need design calls (gas grid, falter tell foreknowledge) or unbuilt FlowWorks/ruins; not offlin | Build the Cauldron mechanics: engine-underfoot soundscape + falter tell, four ra |
| 2026-09-29 | `SWALE_CANAL_ART_REFERENCE_1` | doing/bridge | blocked: Waiting on the RM_Swale_v2 render and its review  | Swale art from live reference: build a real FlowWorks canal in game, screenshot  |
| 2026-09-29 | `FORGE_CYCLE_MECHANICS_1` | doing/offline | blocked: Tranche 1 landed; remaining needs live check (lava-less Forge terrain), audio, art  | Build the Forge fire-and-water grand cycle: gas-wash ignition, boiling rain + Fl |
| 2026-09-29 | `LEANINGSCRUB_MECHANICS_BUILD_1` | doing/offline | blocked: Remaining parts need art/audio/scene layouts or Part 6 cover system; tranche 1 landed  | Build the Leaning Scrub mechanics: Stall+Gale wind calendar, the Lean scent/fire |
| 2026-09-30 | `JOSSUR_FLIGHT_FRAMES_1` | doing/offline | blocked: Artpipe lacks frame-sequence jobs; needs pipeline work first  | Flight flip-book frames for RM_Jossur (optional; flight stat already set) |
| 2026-09-30 | `FORGE_MISSING_ART_1` | doing/offline | blocked: RM_CinderCrust identity unwritten (design line owed before art)  | No render anywhere: RM_CinderCrust (identity unwritten), RUT_TibannaGas, RUT_Fou |
| 2026-09-30 | `WARCASKET_CASK_ART_1` | doing/offline | blocked: Jobs queued; waiting on daemon renders, then wire  | Art for RM_CaskBay (building) and RM_HalfExtractedCore (item); texPaths wired un |
| 2026-09-30 | `CONTAGION_GPT_ENRICHMENT_1` | doing/offline | blocked: Stopped for handoff 2026-09-30; not started - pick up fresh  | Contagion enrichment (GPT consult 2026-09-30, owner-picked by card): Draftprints |
| 2026-09-30 | `SEA_DIVE_FLOOR_TERRAIN_1` | doing/offline | blocked: Scald/Chill floor plants unmeasured: needs a dive from a real Scald/Chill-temperature tile  | Gravship dive floors ignore the seas' terrain bands: GenStep_SeaFloorTerrain pai |
| 2026-09-30 | `SUBSTRUCTURE_PROPS_LAYER_OOB_1` | doing/offline | blocked: Stopped for handoff 2026-09-30; not started - pick up fresh  | Live 2026-09-30b: 'Could not regenerate layer RimWorld.SectionLayer_Substructure |
| 2026-10-01 | `WARSCAR_AEROSOL_SCREEN_1` | ready/offline | blocked: 11-point build; depends on WARSCAR_RAINBOW_POOLS_1 and WARSCAR_OLD_TONGUE_1; needs split a-d (see Transient/wo | Warscar projectors and aerosol screen: lift ShipShields particulate core to RM,  |
| 2026-10-01 | `WARSCAR_RAINBOW_POOLS_1` | doing/offline | blocked: Standalone slice built offline (registry row, pools, cycle+icons, tap, 4 reagents, journal, reader, catalyst,  | Warscar rainbow pools: reaction-liquor registry row, phase cycle with colour-bli |
| 2026-10-02 | `GELATINOUSSLIME_PIT_SOLVENT_1` | doing/offline | blocked: Free slice built (3 pit recipes, toggle, validation) uncommitted; remaining: spec 3 Rot's finest input patch i | Slime pit as a solvent: renders toxic or indigestible food safe (Rot's finest in |
| 2026-10-03 | `SEABED_PER_SEA_FLOORS_1` | doing/offline | blocked: Built: per-sea floor biomes+mapping+plant guard (4 RM_ seas). Remaining: Propane Lake floor (biome is RUT_Prop | Sea-floor planet layer Phases 3+4: guard the FinalizeInit plant crash, then a re |
| 2026-10-03 | `WARSCAR_CHOTRIX_SIGNS_1` | proposed/offline | blocked: Prints and drag marks record through the track grid, which is mid-build in CreatureBehaviors (RM_TrackGridPatc | Chotrix readable signs: track-grid prints and dragged-kill marks (needs FOOTPRIN |

## bridge/live-only (158)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-01 | `SETTLEMENT_VERBS_WAVE_1` | doing/deploy | needs deploy | v1 interaction verbs: crime suite, salvage-law gray zone, walkable commerce, soc |
| 2026-09-02 | `MASS_VALIDATION_LADDER_1` | doing/bridge | needs bridge | Batched validation ladder: get_defs deep-serialize, manifest runner, hot-reload  |
| 2026-09-02 | `SHIELD_MODS_LEVERAGE_1` | doing/bridge | needs bridge | Find existing shield mods, study and make compatible; tuned-plasma-field model p |
| 2026-09-03 | `DIRTY_CODE_REVIEW_STANDING_LOOP_1` | doing/offline | doing, offline part built; remaining is live/judgement | Standing FOUNDRY code-review loop in progress per owner (keep going, bit by bit) |
| 2026-09-05 | `INHABITED_AUGMENTATION_BUILD_1` | doing/bridge | needs bridge | Build the tile-augmentation content: rimplace templates + Inhabited wiring for t |
| 2026-09-05 | `VAULT_THAW_QUEST_FAMILY_1` | doing/bridge | needs bridge | Six Forsaken vault layouts exist but nothing makes them play - no QuestScriptDef |
| 2026-09-06 | `OCULAR_OVERDRIVE_SITE_1` | doing/offline | doing, offline part built; remaining is live/judgement | Ocular Forest stays as a named site (the Overdrive, 3 Ashfall Range tiles) + cus |
| 2026-09-06 | `COLD_LOAD_RUN_SHEET_4` | doing/game-up | needs game-up | Run sheet for the next full-list load: three readings owed from the 2026-09-06 o |
| 2026-09-06 | `DROIDWORKS_FORMAT_TIERS_1` | doing/bridge | needs bridge | Format tiers blank/mindless/programmable/sapient with needs by tier (ruling 4),  |
| 2026-09-06 | `DROIDWORKS_WIPE_SEVERITY_1` | doing/deploy | needs deploy | Memory wipe: 7-day severe relearning debuff, service-record reset, permanent acc |
| 2026-09-07 | `RUST_CATHEDRAL_MECHANICS_1` | doing/bridge | needs bridge | Rust Cathedral C# kit: hum-mood system (attitude value, layered tones, bolt-danc |
| 2026-09-09 | `DESERT_WRAPS_ART_COMMISSION_1` | doing/offline | built; live proof owed | Original desert-wrap apparel art (full body-type matrix) + devolved Tusken head  |
| 2026-09-09 | `BIOME_ENRICHMENT_DESERT_WASTELAND_1` | doing/bridge | needs bridge | Enrichment wave (review B1): Desert (53% zero-mutator) + Wasteland (63%) — the t |
| 2026-09-12 | `WORLDMAP_AUDIT_LIVE_CHECKS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Four worldmap audit checks needing the live game — batch into next game-up windo |
| 2026-09-12 | `BIOME_WORLD_SWITCH_WAVE_1` | doing/bridge | needs bridge | World-switch every donor/vanilla-painted tile to its owned RUT_ successor: MEASU |
| 2026-09-12 | `UTINNI_WORLDMAP_FLIGHT_ICON_1` | doing/deploy | needs deploy | Replace the gravship's world-map flight icon with a Utinni-specific sprite: vani |
| 2026-09-13 | `CATHEDRAL_STAGE_HUM_BRIDGE_1` | doing/bridge | needs bridge | Stage-to-hum-baseline bridge lane into RM_BiomeAttitudeDef (C#, row-3) |
| 2026-09-13 | `MODCHECK_SUITE_CORRECTIONS_1` | doing/offline | doing, offline part built; remaining is live/judgement | MODCHECK_SUITE_CORRECTIONS_1 first-live-run corrections for the 12 RED + 2 abort |
| 2026-09-13 | `WRECKED_DISTILLATION_MODULE_1` | doing/offline | doing, offline part built; remaining is live/judgement | WreckedMachines ship Distillation module: clean water from distillable rows (not |
| 2026-09-13 | `WORLDMAP_LIQUID_TAGS_1` | doing/deploy | needs deploy | worldTag authoring pass on the frozen map (builds on LIQUID_BIOMES_MAP_1) + land |
| 2026-09-13 | `LIQUID_INDUSTRY_SETPIECES_1` | doing/deploy | needs deploy | Found industrial liquid works via the shared scatterer: desal, detox, tar refine |
| 2026-09-13 | `BAZAAR_WINDOW_GRID_1` | doing/deploy | needs deploy | The Bazaar slice 1: Dialog_Trade replacement via WindowStack.Add intercept + vir |
| 2026-09-13 | `WYYYSCHOKK_FANG_PENDANT_1` | doing/deploy | needs deploy | Wyyyschokk fang pendant: hunt trophy apparel, bravery social thoughts with Wilds |
| 2026-09-14 | `BACTA_TANK_CORE_1` | doing/bridge | needs bridge | Bacta Tank core: RSW mod skeleton, tank building, trade-scarce fluid on the Liqu |
| 2026-09-14 | `BIOME_KITS_PUSH_TO_TEST_1` | doing/offline | doing, offline part built; remaining is live/judgement | Push every biome mechanics kit (Forge/Scald/Miasma/Sump/FeverWood/RustCathedral/ |
| 2026-09-17 | `NINEFOLD_LOUDNESS_FRONT_1` | doing/offline | doing, offline part built; remaining is live/judgement | Ninefold owes LOUDNESS and THE FRONT, which canon rules exist and no code comput |
| 2026-09-18 | `AQUATIC_WATER_BREATHING_GENE_1` | doing/bridge | needs bridge | Design and build a real water-breathing mechanism (gene or hediff) for the 4 aqu |
| 2026-09-18 | `DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1` | doing/offline | doing, offline part built; remaining is live/judgement | Droidworks races (G2 included) show a default human face despite RSW_DW_HeadType |
| 2026-09-19 | `DEEPS_FAUNA_MECHANICS_1` | doing/bridge | needs bridge | Deeps creature mechanics from the fauna verdicts: Grabber hold-and-crush, Soulch |
| 2026-09-19 | `DEEPS_FAUNA_MECHANICS_2` | proposed/bridge | belt skip list | Deeps fauna mechanics, second pass on DEEPS_FAUNA_MECHANICS_1: grabber-side crus |
| 2026-09-20 | `MYCOID_COLOSSUS_LIVE_LOOK_1` | doing/game-up | needs game-up | MYCOID_COLOSSUS_LIVE_LOOK_1 |
| 2026-09-23 | `FEVERWOOD_BOUGH_SOIL_TERRAIN_1` | doing/game-up | needs game-up | The crown cannot grow anything: boughway is fertility 0, so bough-soil is owed |
| 2026-09-24 | `VANILLA_BEAST_EXCISION_1` | doing/offline | doing, offline part built; remaining is live/judgement | No vanilla beasts in the Utinni scenario: cut every vanilla/DLC animal at the sc |
| 2026-09-25 | `JAWA_SWIM_HOOD_KEEP_1` | doing/deploy | needs deploy | URGENT (owner, chat 2026-09-25: Jawa must never be seen without a hood): swimmin |
| 2026-09-25 | `SCALD_WATER_AGITATION_FLECKS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Scald wreck shadowData fix + ambient water-agitation ripple mechanism (margin ca |
| 2026-09-26 | `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` | doing/offline | doing, offline part built; remaining is live/judgement | Two-front lure numbers, prey-quality gate, and a free-tier second raider |
| 2026-09-26 | `SUMP_TAR_FIRE_NETWORK_1` | doing/bridge | needs bridge | Network fire with gate firebreaks; wire belch to glass-cooling |
| 2026-09-26 | `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Every fishable in EVERY sea owes a living creature swimming the floor map, not j |
| 2026-09-27 | `TERMINALBIOMES_REVIEW_FIXES_1` | doing/offline | built; live proof owed | TerminalBiomes 29-file review fix wave: 2 dead tickerType mechanisms (vaulisk lu |
| 2026-09-28 | `CONTAGION_RULED_CONTENT_1` | doing/offline | built; live proof owed | Build the Contagion grotesque cast: 35 RM_ defs replacing the donor roster outri |
| 2026-09-30 | `BLUEDESERT_GPT_ENRICHMENT_1` | doing/offline | built; live proof owed | Blue Desert enrichment (GPT consult 2026-09-30, owner-picked by card): blue-ice  |
| 2026-09-30 | `GRAVSHIP_ACOUSTIC_SCANNER_1` | doing/offline | built; live proof owed | Gravship acoustic scanner (owner, 2026-09-30, from the Cracked Lands Belly Sound |
| 2026-10-01 | `FOOTPRINT_TRACK_GRID_1` | doing/offline | built; live proof owed | One footprint grid for the planet: capped TrackGrid + section layer + cell-entry |
| 2026-10-01 | `WARSCAR_HOSPICE_DESERTERS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Warscar hospice: kneeling chassis rings, deserter histories, five-stage cradle r |
| 2026-10-01 | `WARSCAR_TOTCHAK_WAKES_1` | doing/offline | doing, offline part built; remaining is live/judgement | Warscar totchak: dormant in the Last Line, demolition wake, eats ruin walls then |
| 2026-10-01 | `WARSCAR_OLD_TONGUE_1` | doing/offline | doing, offline part built; remaining is live/judgement | Warscar old tongue: inscribed panel sets read by Intellectual 8 unlock hospice p |
| 2026-10-01 | `WARSCAR_TURRETS_TRACK_1` | doing/offline | doing, offline part built; remaining is live/judgement | Warscar turrets still track: verbless aim comp on broken turrets, refit into a w |
| 2026-10-01 | `STILLSAND_SAND_SWIM_REMAINDER_1` | doing/offline | built; live proof owed | Sand-swim kit remainder: thumper, sand fishing, the Listening, wake track record |
| 2026-10-01 | `PYRELANDS_NORTHSTAR_TRIAL_1` | proposed/bridge | needs bridge | Pyrelands north-star trial: carry the biome template to SHIPPED (parent; depends |
| 2026-10-01 | `NORTHSTAR_FAST_DRIVER_1` | proposed/bridge | needs bridge | Ultra-fast Python bridge driver for north-star validation (core built, live proo |
| 2026-10-01 | `PYRELANDS_GREEN_MINIMAL_1` | proposed/bridge | needs bridge | Pyrelands north star GREEN on the pyrelands tier (pre-flight gates, 2-ring scrat |
| 2026-10-01 | `PYRELANDS_GREEN_FULL_1` | proposed/bridge | needs bridge | Pyrelands north star GREEN on the full list (fresh full-list mapgen on a scratch |
| 2026-10-01 | `STILLSAND_SUN_LIVE_VERIFY_1` | proposed/game-up | needs game-up | Live-verify Stillsand sun from latitude on quicktest maps at two latitudes: no n |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_TRIAL_1` | proposed/bridge | needs bridge | FlowWorks north-star trial: VALIDATED -> WIRED -> GREEN-minimal -> GREEN-full -> |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_SITE_PREP_1` | proposed/bridge | needs bridge | FlowWorks trial site: golden save, manifest, preflight that refuses a dirty site |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` | proposed/bridge | needs bridge | FlowWorks trial: first live BASELINE run on the minimal tier, timed, verify reco |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | proposed/bridge | needs bridge | FlowWorks north star GREEN on the minimal tier |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` | proposed/bridge | needs bridge | FlowWorks north star GREEN on the full mod list |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_TRIAL_1` | proposed/bridge | needs bridge | Graffiti north-star trial: pipeline pilot to first GREEN (parent of WIRED/GREEN_ |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1` | proposed/bridge | needs bridge | Graffiti: GREEN on MINIMAL+graffiti via fast driver, owner sheet review |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_GREEN_FULL_1` | proposed/bridge | needs bridge | Graffiti: GREEN on the owner's FULL list (fresh launch, full-list driver mode) |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_SHIP_1` | proposed/deploy | needs deploy | Graffiti: SHIPPED - art complete, settings superb, CLEAN, stamped, deployed |
| 2026-10-01 | `STILLSAND_CONTENT_LIVE_PROOF_1` | proposed/game-up | needs game-up | Prove the built Stillsand cast live (atlas, zuurrik on blood) and swap four plac |
| 2026-10-01 | `STILLSAND_EVENT_CREATURES_LIVE_1` | proposed/game-up | needs game-up | Live-prove the krayt attack and muurrok on a Stillsand quicktest, and live-fire  |
| 2026-10-01 | `ABYSS_HIDDEN_SHIP_PROBES_1` | doing/offline | doing, offline part built; remaining is live/judgement | The Abyss: hidden-ship cover; probe droids still come and must be avoided |
| 2026-10-01 | `STILLSAND_PRECIOUS_CAVES_LIVE_1` | proposed/game-up | needs game-up | Precious caves: ten live Stillsand quicktest maps |
| 2026-10-01 | `STILLSAND_CAVE_AS_PLACE_1` | doing/offline | doing, offline part built; remaining is live/judgement | Stillsand cave: preservation, drip, biosilica walls, tribal mark |
| 2026-10-01 | `STILLSAND_SOLAR_STILL_1` | doing/offline | doing, offline part built; remaining is live/judgement | Stillsand solar still and wringing still: sun-gated lens condenser distilling br |
| 2026-10-01 | `STILLSAND_SUN_LANCE_1` | doing/offline | doing, offline part built; remaining is live/judgement | Stillsand sun lance: heliostat mirror turret that heats and never ignites |
| 2026-10-01 | `STILLSAND_GLASS_CHAIN_REMAINDER_1` | doing/game-up | needs game-up | Stillsand glass chain remainder: krayt lens, goggles recipe, fulgurite art, art  |
| 2026-10-01 | `STILLSAND_RETURN_REMAINDER_1` | proposed/game-up | needs game-up | Stillsand Return remainder: live proof, the visible Return line, cave debt stone |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1` | proposed/bridge | needs bridge | JawaBench tools the Graffiti trial cannot fake: thing_graphic, spawn_variant, ru |
| 2026-10-01 | `STILLSAND_DUNE_GALE_LIVE_1` | proposed/game-up | needs game-up | Stillsand dune gale: live proof (mass delta, sun off, one emergence, carry lette |
| 2026-10-01 | `CRACKEDLANDS_ENRICHMENT_QUICKTEST_1` | proposed/bridge | needs bridge | Quicktest-prove the Cracked Lands enrichment tranche by state reads: five beats, |
| 2026-10-01 | `STILLSAND_FIXES_LIVE_PROOF_1` | proposed/game-up | needs game-up | Live proof for the five 2026-10-01 live-session fixes |
| 2026-10-01 | `CAULDRON_VENT_ENRICHMENT_HOOKS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Cauldron enrichment pieces that hang on vents: weather vent multipliers + vent-l |
| 2026-10-01 | `CAULDRON_ENRICHMENT_LIVE_PROOF_1` | proposed/game-up | needs game-up | Quicktest-prove the offline-built Cauldron enrichment: assay grade line, vexxiss |
| 2026-10-01 | `LEANINGSCRUB_SWEETLINE_VISITORS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Sweetline travellers camp and pilgrims leave tokens: who, mapgen or incident, to |
| 2026-10-01 | `LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1` | doing/offline | doing, offline part built; remaining is live/judgement | Shed vissler arms draw real scavengers: which species, food or lure job |
| 2026-10-01 | `LEANINGSCRUB_ENRICHMENT_QUICKTEST_1` | proposed/bridge | needs bridge | Quicktest-prove dripping regrow, crown mob, runway bloom, named sweetline trees  |
| 2026-10-01 | `FORGE_ENRICHMENT_QUICKTEST_1` | proposed/game-up | needs game-up | Quicktest-prove the Forge enrichment tranche on a Forge map: keel brace fuel sav |
| 2026-10-01 | `LONGSHADE_ENRICHMENT_QUICKTEST_1` | proposed/game-up | needs game-up | Quicktest the Long Shade enrichment: gloomcast moving shade, camera heat soundsc |
| 2026-10-01 | `SOORRAK_INSTANT_JOB_LOOP_1` | doing/bridge | needs bridge | Wild soorrak sits in Wait_MaintainPosture forever: its next job succeeds instant |
| 2026-10-01 | `LIVE_ROUND2_FIXES_PROOF_1` | proposed/game-up | needs game-up | Prove the three live-round-2 fixes in game (beam, soorrak loop log, rimplace stu |
| 2026-10-01 | `NORTHSTAR_EVERYWHERE_PROGRAM_1` | proposed/bridge | needs bridge | North-star scripts for every mod; new-content pause until done |
| 2026-10-01 | `ABYSS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: Abyss |
| 2026-10-01 | `ACOUSTIC_SCANNER_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: AcousticScanner |
| 2026-10-01 | `ASSAILANT_SALVAGE_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: AssailantSalvage |
| 2026-10-01 | `BLUE_DESERT_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: BlueDesert |
| 2026-10-01 | `CAULDRON_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: Cauldron |
| 2026-10-01 | `CONTAGION_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: Contagion |
| 2026-10-01 | `CREATURE_BEHAVIORS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: CreatureBehaviors |
| 2026-10-01 | `DIVING_INTERACTION_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: DivingInteraction |
| 2026-10-01 | `ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: EnvironmentalHazards |
| 2026-10-01 | `EXPLOSIVE_GROWTH_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: ExplosiveGrowth |
| 2026-10-01 | `FEVER_WOOD_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: FeverWood |
| 2026-10-01 | `FLOODED_CANYON_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: FloodedCanyon |
| 2026-10-01 | `GELATINOUS_SLIME_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: GelatinousSlime |
| 2026-10-01 | `GRAVSHIP_LANDING_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: GravshipLanding |
| 2026-10-01 | `GREENTIDE_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Greentide |
| 2026-10-01 | `HOSTILE_FLORA_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: HostileFlora |
| 2026-10-01 | `LEANING_SCRUB_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: LeaningScrub |
| 2026-10-01 | `LONG_SHADE_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: LongShade |
| 2026-10-01 | `LORE_STAGES_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: LoreStages |
| 2026-10-01 | `LUMINOUS_PIGMENT_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: LuminousPigment |
| 2026-10-01 | `MIASMA_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: Miasma |
| 2026-10-01 | `MOVING_DUNES_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: MovingDunes |
| 2026-10-01 | `NIGHTSIDE_ICE_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: NightsideIce |
| 2026-10-01 | `OASIS_MAKER_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: OasisMaker |
| 2026-10-01 | `PROXIMITY_HATCH_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: ProximityHatch |
| 2026-10-01 | `PYRINTH_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Pyrinth |
| 2026-10-01 | `RUST_CATHEDRAL_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: RustCathedral |
| 2026-10-01 | `SCARLANDS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: Scarlands |
| 2026-10-01 | `SHIP_VERMIN_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: ShipVermin |
| 2026-10-01 | `STILLSAND_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: Stillsand |
| 2026-10-01 | `TERMINAL_BIOMES_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: TerminalBiomes |
| 2026-10-01 | `THE_BAZAAR_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: TheBazaar |
| 2026-10-01 | `THE_FORGE_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: TheForge |
| 2026-10-01 | `THE_ROT_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: TheRot |
| 2026-10-01 | `THE_SUMP_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: TheSump |
| 2026-10-01 | `TITANIC_CREATURES_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: TitanicCreatures |
| 2026-10-01 | `WARCASKET_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Warcasket |
| 2026-10-01 | `WASTELAND_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Wasteland |
| 2026-10-01 | `WEBWORK_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Webwork |
| 2026-10-01 | `WEEPING_STONES_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: WeepingStones |
| 2026-10-01 | `BACTA_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Bacta |
| 2026-10-01 | `BRAIN_WORMS_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: BrainWorms |
| 2026-10-01 | `GIZKA_STOWAWAY_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: GizkaStowaway |
| 2026-10-01 | `GRAFFITI_IMPERIAL_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: GraffitiImperial |
| 2026-10-01 | `SARLACC_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Sarlacc |
| 2026-10-01 | `SHOKK_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: Shokk |
| 2026-10-01 | `TROPHY_CRAFT_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: TrophyCraft |
| 2026-10-01 | `DROID_REPAIR_JOBS_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: DroidRepairJobs |
| 2026-10-01 | `EGG_RECKONING_FIRST_SCRIPT_1` | doing/bridge | needs bridge | First north-star script: EggReckoning |
| 2026-10-01 | `FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: FungalSoilTrade |
| 2026-10-01 | `GREENTIDE_RAID_ANT_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: GreentideRaidAnt |
| 2026-10-01 | `KYBER_TRADE_PLOT_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: KyberTradePlot |
| 2026-10-01 | `PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: PropaneLakeMechanics |
| 2026-10-01 | `PYRELANDS_MECHANICS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: PyrelandsMechanics |
| 2026-10-01 | `RIVER_COLORS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: RiverColors |
| 2026-10-01 | `RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: RustCathedralRoaches |
| 2026-10-01 | `SCARLANDS_LADDER_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: ScarlandsLadder |
| 2026-10-01 | `SCAVENGER_EVENTS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: ScavengerEvents |
| 2026-10-01 | `SHIP_SHIELDS_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: ShipShields |
| 2026-10-01 | `SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: ShokkweaveEconomy |
| 2026-10-01 | `WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1` | proposed/bridge | needs bridge | First north-star script: WildsteamEggBounty |
| 2026-10-01 | `ART_OVERRIDE_FAMILY_SCRIPT_1` | proposed/bridge | needs bridge | One parametrized north-star script for the 48 *ArtOverride mods |
| 2026-10-01 | `BIOME_TIER_CLEANUP_1` | proposed/game-up | needs game-up | Biome tier cleanup: move twin-only features to RM_, scrub Star Wars IP, move RUT |
| 2026-10-02 | `NORTHSTAR_SITUATIONAL_ROLLOUT_1` | proposed/bridge | needs bridge | Flip modcheck --situational to default after an abort-only pass over every suite |
| 2026-10-02 | `NORTHSTAR_COMPANION_GAPS_1` | proposed/deploy | needs deploy | Companion tools: pawn census (mental state+job), incident-queue peek/selective r |
| 2026-10-02 | `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1` | proposed/bridge | needs bridge | Prove a gravship can land in a non-hostile settlement (Hutt test site first) wit |
| 2026-10-02 | `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` | doing/offline | doing, offline part built; remaining is live/judgement | Slime giant: a chunk of the titanoslime is a terrible thrown bioweapon |
| 2026-10-02 | `NORTHSTAR_ISHKO_PILOT_1` | proposed/bridge | needs bridge | Northstar pilot on IshkoDarkLandmarks: walk arrows, ishko tier, mock clean, reco |
| 2026-10-03 | `SCALD_BATHING_RITE_1` | doing/offline | doing, offline part built; remaining is live/judgement | Scald rite: water pilgrims bathe at the cool margins (design; register entry; wa |
| 2026-10-03 | `GRAFFITI_WALL_LINKED_CROP_1` | proposed/game-up | needs game-up | Graffiti wall marks may draw only a 1/16 crop of their art: wall-linked graphics |
| 2026-10-03 | `WEEPINGSTONES_NET_FLEEING_FLIER_1` | proposed/bridge | needs bridge | NET job cannot catch a wild skarrin: it flies off-map before the handler arrives |
| 2026-10-03 | `FALL_LINE_MUTATOR_PLACEMENT_1` | proposed/bridge | needs bridge | Place the RUT_FallLine tile mutator on the 308 Fall Line + The Breaks tiles of t |
| 2026-10-03 | `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1` | proposed/offline | belt skip list | Abyss: the Dark muffles every map sound (Harmony on sample creation) |

## stale (0)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
