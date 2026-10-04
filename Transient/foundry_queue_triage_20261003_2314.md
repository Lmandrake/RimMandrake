# FOUNDRY queue triage 20261003_2314 (belt builder r39)

Same inline-script family as `foundry_queue_triage_20261003_2101.md` (r34): model.replay(), open FOUNDRY items, heuristic buckets. NEW: skip list + every ID in `owner_unblock_list_20261003.md` bucketed `skip`. Heuristic; compare totals.

**Total open: 399** (r34: 399) · offline-buildable 79 · too-big 65 · art-pending 1 · owner-blocked 11 · blocked-on-item 20 · blocked-other 2 · bridge/live-only 117 · skip 64 · stale 40


## offline-buildable (79)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-03 | `DIRTY_CODE_REVIEW_STANDING_LOOP_1` | doing/offline | doing offline, unblocked, 2558-char spec | Standing FOUNDRY code-review loop in progress per owner (keep going, bit by bit) |
| 2026-09-12 | `UTINNI_WORLDMAP_FLIGHT_ICON_1` | doing/deploy | doing deploy, unblocked, 2882-char spec | Replace the gravship's world-map flight icon with a Utinni-specific sprite: vani |
| 2026-09-13 | `MODCHECK_SUITE_CORRECTIONS_1` | doing/offline | doing offline, unblocked, 1928-char spec | MODCHECK_SUITE_CORRECTIONS_1 first-live-run corrections for the 12 RED + 2 abort |
| 2026-09-13 | `WRECKED_DISTILLATION_MODULE_1` | doing/offline | doing offline, unblocked, 1102-char spec | WreckedMachines ship Distillation module: clean water from distillable rows (not |
| 2026-09-13 | `LIQUID_INDUSTRY_SETPIECES_1` | doing/deploy | doing deploy, unblocked, 1458-char spec | Found industrial liquid works via the shared scatterer: desal, detox, tar refine |
| 2026-09-13 | `BAZAAR_WINDOW_GRID_1` | doing/deploy | doing deploy, unblocked, 1815-char spec | The Bazaar slice 1: Dialog_Trade replacement via WindowStack.Add intercept + vir |
| 2026-09-13 | `WYYYSCHOKK_FANG_PENDANT_1` | doing/deploy | doing deploy, unblocked, 3771-char spec | Wyyyschokk fang pendant: hunt trophy apparel, bravery social thoughts with Wilds |
| 2026-09-18 | `DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1` | doing/offline | doing offline, unblocked, 1204-char spec | Droidworks races (G2 included) show a default human face despite RSW_DW_HeadType |
| 2026-09-24 | `VANILLA_BEAST_EXCISION_1` | doing/offline | doing offline, unblocked, 2910-char spec | No vanilla beasts in the Utinni scenario: cut every vanilla/DLC animal at the sc |
| 2026-09-26 | `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1` | proposed/offline | proposed offline, unblocked, 4901-char spec | The greatbole's song, thermal sanctuary, pilgrims, and the two opt-in crossovers |
| 2026-09-26 | `WYYYSCHOKK_IDENTITY_COLLISION_1` | proposed/owner | proposed owner, unblocked, 4915-char spec | Decide fate of RSW_Wyyyschokk (MLIE_FAUNA_ABSORPTION_1's full port) now that RM_ |
| 2026-09-26 | `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` | doing/offline | doing offline, unblocked, 3880-char spec | Every fishable in EVERY sea owes a living creature swimming the floor map, not j |
| 2026-09-27 | `EMPIRE_ESCALATION_LADDER_1` | proposed/offline | proposed offline, unblocked, 1611-char spec | Empire escalation ladder: evadable probes first, new raid kinds per rung, until  |
| 2026-09-28 | `CONTAGION_RULED_CONTENT_1` | doing/offline | doing offline, unblocked, 2368-char spec | Build the Contagion grotesque cast: 35 RM_ defs replacing the donor roster outri |
| 2026-09-30 | `WASTELAND_GPT_ENRICHMENT_1` | doing/offline | doing offline, unblocked, 3132-char spec | Wasteland enrichment (GPT consult 2026-09-30, owner-picked by card): named storm |
| 2026-09-30 | `BLUEDESERT_GPT_ENRICHMENT_1` | doing/offline | doing offline, unblocked, 2937-char spec | Blue Desert enrichment (GPT consult 2026-09-30, owner-picked by card): blue-ice  |
| 2026-09-30 | `GRAVSHIP_ACOUSTIC_SCANNER_1` | doing/offline | doing offline, unblocked, 1836-char spec | Gravship acoustic scanner (owner, 2026-09-30, from the Cracked Lands Belly Sound |
| 2026-10-01 | `WATCHER_CREATURES_MOD_1` | proposed/owner | proposed owner, unblocked, 2759-char spec | Watchers mod: cross-biome shy creatures that sit, poke out, watch, and jerk away |
| 2026-10-01 | `WARSCAR_HOSPICE_DESERTERS_1` | doing/offline | doing offline, unblocked, 3842-char spec | Warscar hospice: kneeling chassis rings, deserter histories, five-stage cradle r |
| 2026-10-01 | `WARSCAR_TOTCHAK_WAKES_1` | doing/offline | doing offline, unblocked, 2232-char spec | Warscar totchak: dormant in the Last Line, demolition wake, eats ruin walls then |
| 2026-10-01 | `WARSCAR_OLD_TONGUE_1` | doing/offline | doing offline, unblocked, 1990-char spec | Warscar old tongue: inscribed panel sets read by Intellectual 8 unlock hospice p |
| 2026-10-01 | `WARSCAR_TURRETS_TRACK_1` | doing/offline | doing offline, unblocked, 1401-char spec | Warscar turrets still track: verbless aim comp on broken turrets, refit into a w |
| 2026-10-01 | `STILLSAND_SAND_SWIM_REMAINDER_1` | doing/offline | doing offline, unblocked, 3931-char spec | Sand-swim kit remainder: thumper, sand fishing, the Listening, wake track record |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_SHIP_1` | proposed/deploy | proposed deploy, unblocked, 791-char spec | Graffiti: SHIPPED - art complete, settings superb, CLEAN, stamped, deployed |
| 2026-10-01 | `ABYSS_HIDDEN_SHIP_PROBES_1` | doing/offline | doing offline, unblocked, 2436-char spec | The Abyss: hidden-ship cover; probe droids still come and must be avoided |
| 2026-10-01 | `STILLSAND_CAVE_AS_PLACE_1` | doing/offline | doing offline, unblocked, 1310-char spec | Stillsand cave: preservation, drip, biosilica walls, tribal mark |
| 2026-10-01 | `STILLSAND_SAND_SIEVE_CHORE_1` | doing/offline | doing offline, unblocked, 1986-char spec | Stillsand sand sieve as a pawn chore: glass sand to fine sand with a carried sie |
| 2026-10-01 | `STILLSAND_SOLAR_STILL_1` | doing/offline | doing offline, unblocked, 1358-char spec | Stillsand solar still and wringing still: sun-gated lens condenser distilling br |
| 2026-10-01 | `STILLSAND_SUN_LANCE_1` | doing/offline | doing offline, unblocked, 985-char spec | Stillsand sun lance: heliostat mirror turret that heats and never ignites |
| 2026-10-01 | `STILLSAND_GEOPHONE_1` | doing/offline | doing offline, unblocked, 565-char spec | Stillsand biosilica geophone: rumble markers from the sand-swim query |
| 2026-10-01 | `STILLSAND_SKELETONS_REMAINDER_1` | proposed/offline | proposed offline, unblocked, 2451-char spec | Stillsand skeletons remainder: tracks on the footprint grid + dune eraser, dune  |
| 2026-10-01 | `CAULDRON_VENT_ENRICHMENT_HOOKS_1` | doing/offline | doing offline, unblocked, 1715-char spec | Cauldron enrichment pieces that hang on vents: weather vent multipliers + vent-l |
| 2026-10-01 | `CAULDRON_ENRICHMENT_VISUALS_1` | proposed/owner | proposed owner, unblocked, 851-char spec | Cauldron enrichment visuals: dewfall chemical beads, dewfall plant saturation, a |
| 2026-10-01 | `VEXXITH_CLOSED_LOOP_BUILD_1` | proposed/owner | proposed owner, unblocked, 1357-char spec | Vexxith closed loop: acid immunity hook, plate-only recipes, poor-walls/weapons  |
| 2026-10-01 | `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` | proposed/owner | proposed owner, unblocked, 1282-char spec | Pitch further venomvine forms to the owner (he typed "Might need even more"); ru |
| 2026-10-01 | `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1` | proposed/owner | proposed owner, unblocked, 908-char spec | Sweetline tree naming register (current RM_NamerSweetlineTree vocabulary is a pl |
| 2026-10-01 | `LEANINGSCRUB_SWEETLINE_VISITORS_1` | doing/offline | doing offline, unblocked, 1168-char spec | Sweetline travellers camp and pilgrims leave tokens: who, mapgen or incident, to |
| 2026-10-01 | `LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1` | doing/offline | doing offline, unblocked, 1144-char spec | Shed vissler arms draw real scavengers: which species, food or lure job |
| 2026-10-01 | `NORTHSTAR_ADVERSARIAL_REVIEW_1` | proposed/offline | proposed offline, unblocked, 631-char spec | Standing: periodic adversarial and GPT review of north-star scripts |
| 2026-10-01 | `NORTHSTAR_BRIDGE_UTILIZATION_1` | proposed/offline | proposed offline, unblocked, 1359-char spec | Track live bridge utilization (active driving time over held time) as the progra |
| 2026-10-02 | `NINEFOLD_FAVOUR_ODDS_BUILD_1` | proposed/offline | proposed offline, unblocked, 880-char spec | Build Nine Faults (fresh-find rite, Rekko to Zizzik), the Left Behind transfer ( |
| 2026-10-02 | `HUTT_SLAVE_PIT_TEST_SITE_1` | proposed/offline | proposed offline, unblocked, 1912-char spec | Hutt slave pit at a small stand-alone test site: sell slaves, prisoners and down |
| 2026-10-02 | `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` | proposed/offline | proposed offline, unblocked, 984-char spec | Lantern Deeps: The Answering, Ohm's found settlement rite (campaign) |
| 2026-10-02 | `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` | proposed/offline | proposed offline, unblocked, 1963-char spec | Pyrelands: The Struck Glass rite for Zizzik (stamped lightning-glass ring, rando |
| 2026-10-02 | `PIT_DEPTH_DRAW_OFFSET_1` | proposed/offline | proposed offline, unblocked, 1240-char spec | Pawns visibly sink and rise with canal depth; superdeep walls 20% above the head |
| 2026-10-02 | `EXCAVATION_WALL_ART_1` | proposed/offline | proposed offline, unblocked, 1233-char spec | Wall-face art for all four depths, spikes and ladder (Quarry perspective) |
| 2026-10-02 | `WEEPINGSTONES_CONDENSER_QUESTS_1` | proposed/offline | proposed offline, unblocked, 3581-char spec | Walking condenser quests: Hutt capture for the Arena, or Moisture Farmers keep i |
| 2026-10-02 | `WEEPINGSTONES_REFUSED_TOLL_RITE_1` | proposed/offline | proposed offline, unblocked, 3617-char spec | The Refused Toll, for Mob'Unloo: draw at an Imperial metering station and walk a |
| 2026-10-02 | `GELATINOUSSLIME_KIT_ART_1` | doing/offline | doing offline, unblocked, 1882-char spec | Slime: real art for the whole free kit, replacing the vanilla tortoise/grass/bus |
| 2026-10-02 | `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` | doing/offline | doing offline, unblocked, 2766-char spec | Slime giant: a chunk of the titanoslime is a terrible thrown bioweapon |
| 2026-10-02 | `MIASMA_RECALL_WRITTEN_OFF_RITE_1` | proposed/offline | proposed offline, unblocked, 2168-char spec | The Recall of the Written-Off rite (Rekko): a struck-out disposal order calls a  |
| 2026-10-03 | `STARWARS_JUNK_RESKIN_1` | proposed/offline | proposed offline, unblocked, 1112-char spec | Reskin vanilla ancient junk (cars, tanks, walkers, dropships) as Star-Wars-adjac |
| 2026-10-03 | `UNFINISHED_LINE_TITHE_BEAT_1` | proposed/offline | proposed offline, unblocked, 824-char spec | Unfinished Line beat 4 The Tithe and the Hands: scaled material tithe to the sit |
| 2026-10-03 | `UNFINISHED_LINE_WORLD_FOUNDRY_1` | proposed/offline | proposed offline, unblocked, 1020-char spec | Unfinished Line runs in the world (Q1=A): Enclave regrowth, Foundry-grade frames |
| 2026-10-04 | `CREATUREBEHAVIORS_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 997-char spec | CreatureBehaviors north-star script is THIN: add asserting bars for its uncovere |
| 2026-10-04 | `PLANETPRESETPRIME_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 957-char spec | PlanetPresetPrime north-star script is THIN: add asserting bars for its uncovere |
| 2026-10-04 | `DIVINGINTERACTION_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 980-char spec | DivingInteraction north-star script is THIN: add asserting bars for its uncovere |
| 2026-10-04 | `ENVIRONMENTALHAZARDS_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1063-char spec | EnvironmentalHazards north-star script is THIN: add asserting bars for its uncov |
| 2026-10-04 | `GIZKASTOWAWAY_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1013-char spec | GizkaStowaway north-star script is THIN: add asserting bars for its uncovered be |
| 2026-10-04 | `GRAVSHIPLANDING_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 817-char spec | GravshipLanding north-star script is THIN: add asserting bars for its uncovered  |
| 2026-10-04 | `KEELHOIST_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1207-char spec | KeelHoist north-star script is THIN: add asserting bars for its uncovered behavi |
| 2026-10-04 | `LONGSHADE_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1031-char spec | LongShade north-star script is THIN: add asserting bars for its uncovered behavi |
| 2026-10-04 | `MANDRAKEPATCHES_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1582-char spec | MandrakePatches north-star script is THIN: add asserting bars for its uncovered  |
| 2026-10-04 | `MOVINGDUNES_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1046-char spec | MovingDunes north-star script is THIN: add asserting bars for its uncovered beha |
| 2026-10-04 | `PAWNFLAVOR_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1278-char spec | PawnFlavor north-star script is THIN: add asserting bars for its uncovered behav |
| 2026-10-04 | `PYRINTH_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1169-char spec | Pyrinth north-star script is THIN: add asserting bars for its uncovered behaviou |
| 2026-10-04 | `RAIDREDESIGNER_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 990-char spec | RaidRedesigner north-star script is THIN: add asserting bars for its uncovered b |
| 2026-10-04 | `RESEARCHRETAG_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1495-char spec | ResearchRetag north-star script is THIN: add asserting bars for its uncovered be |
| 2026-10-04 | `RESTRAININGBOLTS_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 896-char spec | RestrainingBolts north-star script is THIN: add asserting bars for its uncovered |
| 2026-10-04 | `RIMPROPERTY_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1005-char spec | RimProperty north-star script is THIN: add asserting bars for its uncovered beha |
| 2026-10-04 | `RUSTCHROME_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 871-char spec | RustChrome north-star script is THIN: add asserting bars for its uncovered behav |
| 2026-10-04 | `SEASHORES_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 981-char spec | SeaShores north-star script is THIN: add asserting bars for its uncovered behavi |
| 2026-10-04 | `STARWARSPATCHES_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1038-char spec | StarWarsPatches north-star script is THIN: add asserting bars for its uncovered  |
| 2026-10-04 | `STRUCTUREINJECTIONSRUT_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 995-char spec | StructureInjectionsRUT north-star script is THIN: add asserting bars for its unc |
| 2026-10-04 | `UTINNIPATCHES_COVERAGE_GAPS_1` | proposed/offline | proposed offline, unblocked, 1091-char spec | UtinniPatches north-star script is THIN: add asserting bars for its uncovered be |
| 2026-10-04 | `NORTHSTAR_PARTIAL_GAPS_FILL_1` | proposed/offline | proposed offline, unblocked, 504-char spec | Fill the coverage gaps of the 67 PARTIAL north-star scripts, a mod at a time bes |
| 2026-10-04 | `FEVERWOOD_OIL_FLASH_BARE_GROUND_1` | proposed/offline | proposed offline, unblocked, 1149-char spec | Oil-haze flash lights no fire on bare ground (TryStartFireIn needs ground fuel) |
| 2026-10-04 | `ARMOURY_PROJECTILE_DAMAGE_TOOL_1` | proposed/deploy | proposed deploy, unblocked, 3436-char spec | Bridge tool reading projectile damageAmountBase (private) so Armoury's ranged la |
| 2026-10-04 | `ARMOURY_KOTOR_BOLT_GUARD_1` | proposed/offline | proposed offline, unblocked, 2331-char spec | Armoury ranged patch: 5 absorbed KotOR bolt ops sit under the inactive donor's F |

## too-big (65)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-08-30 | `VAULT_DUNGEON_BUILD_1` | doing/offline | 36053-char spec | Build the six Forsaken vaults: concentric grammar templates, LARGE maps, quickte |
| 2026-08-31 | `TILE_STRUCTURE_DESIGNS_1` | doing/offline | 92806-char spec | Make and improve the promise/whisper structure designs per the roster (22+22): r |
| 2026-09-01 | `SETTLEMENT_VERBS_WAVE_1` | doing/deploy | 38245-char spec | v1 interaction verbs: crime suite, salvage-law gray zone, walkable commerce, soc |
| 2026-09-06 | `OCULAR_OVERDRIVE_SITE_1` | doing/offline | 5842-char spec | Ocular Forest stays as a named site (the Overdrive, 3 Ashfall Range tiles) + cus |
| 2026-09-06 | `ANCIENT_WAR_LAB_1` | doing/offline | 11439-char spec | The war lab beneath the propane lake over the Impact Site — submerged dungeon, l |
| 2026-09-06 | `DROIDWORKS_WIPE_SEVERITY_1` | doing/deploy | 26017-char spec | Memory wipe: 7-day severe relearning debuff, service-record reset, permanent acc |
| 2026-09-07 | `SHOKKWEAVE_SOLE_SOURCE_1` | doing/owner | 27817-char spec | Shokkweave economy: rename hyperweave game-wide, strip it from EVERY trader stoc |
| 2026-09-07 | `MIASMA_MECHANICS_1` | doing/offline | 86402-char spec | Miasma C# kit: surge/salt-line system (fresh-brine map axis, storm-driven moveme |
| 2026-09-07 | `SUMP_MECHANICS_1` | doing/offline | 84062-char spec | Sump C# kit: poured tar moat + command ignition (smoke wall), dig-lottery tables |
| 2026-09-07 | `FORGE_MECHANICS_1` | doing/offline | 57263-char spec | Forge C# kit: boiling-rain weather (scald, flash cycle, flash-interval growth),  |
| 2026-09-07 | `SCALD_MECHANICS_1` | doing/offline | 43498-char spec | Scald C# kit: steam-catch industry, margin fishing + bath recreation, bubble-sai |
| 2026-09-09 | `DESERT_WRAPS_ART_COMMISSION_1` | doing/offline | 7875-char spec | Original desert-wrap apparel art (full body-type matrix) + devolved Tusken head  |
| 2026-09-09 | `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` | doing/owner | 11200-char spec | Widen base RM Graffiti scope: punk/urban graffiti register + ideoligion-inspired |
| 2026-09-12 | `WORLDMAP_AUDIT_LIVE_CHECKS_1` | doing/offline | 5425-char spec | Four worldmap audit checks needing the live game — batch into next game-up windo |
| 2026-09-12 | `FASCINATING_WORLD_JUNK_1` | doing/owner | 12543-char spec | Reskin and re-text every map-scatter wreck (tanks, trucks, cars, ancient junk) i |
| 2026-09-13 | `CATHEDRAL_REGARD_BLACKBOARD_1` | doing/offline | 14582-char spec | Cathedral Regard counter + stage machine + exposure pressure on the GM blackboar |
| 2026-09-13 | `CATHEDRAL_EXPOSURE_COMPLETION_1` | doing/offline | 10459-char spec | The A6 pyrrhic discovery ending: witnessed fall, warzone flip, priced Hutt extra |
| 2026-09-13 | `GM_BLACKBOARD_SHADOW_M4_1` | doing/offline | 9848-char spec | Build M4: Imperial Heat + orbital-detection timer + dark-tile pause as a Python  |
| 2026-09-13 | `WORLDMAP_LIQUID_TAGS_1` | doing/deploy | 7163-char spec | worldTag authoring pass on the frozen map (builds on LIQUID_BIOMES_MAP_1) + land |
| 2026-09-13 | `CANON_CREATURE_REGEN_1` | doing/owner | 23778-char spec | Regenerate every SW-canon creature from library guidance (gated on CANON_REFEREN |
| 2026-09-14 | `GREENTIDE_MECHANICS_2` | doing/offline | 70795-char spec | The Greentide C# kit build: wet-bulb condition+gear, dry-air blower, steam devil |
| 2026-09-14 | `BIOME_KITS_PUSH_TO_TEST_1` | doing/offline | 6997-char spec | Push every biome mechanics kit (Forge/Scald/Miasma/Sump/FeverWood/RustCathedral/ |
| 2026-09-14 | `SCARLANDS_MECHANICS_2` | doing/offline | 33243-char spec | The Scarlands C# kit build: Scarlands mark hediff+severity floor, plated-grazer  |
| 2026-09-14 | `FIREHAWK_FLIGHT_BEHAVIOR_1` | doing/offline | 17328-char spec | FireHawk and all flying fauna get donor-style flight animation |
| 2026-09-15 | `RAKATAN_ARCHOTECH_MACHINES_1` | proposed/owner | 17931-char spec | Design session with the owner: extend Wrecked Machines into the core Rakatan tec |
| 2026-09-16 | `FLOWWORKS_BUILD_PROGRAM_1` | doing/offline | 18435-char spec | FlowWorks - the phased build program for one liquid mod built on excavation dept |
| 2026-09-17 | `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` | doing/offline | 22215-char spec | AtmosphericBase (mandrake.rm.atmosphericbase): the ambient framework the gods sp |
| 2026-09-17 | `NINEFOLD_LOUDNESS_FRONT_1` | doing/offline | 5596-char spec | Ninefold owes LOUDNESS and THE FRONT, which canon rules exist and no code comput |
| 2026-09-17 | `BARBSLINGER_SCORPION_REDESIGN_1` | doing/owner | 9748-char spec | Barbslinger redesigned: yellowish large scorpion-like creature, bulbous domed bo |
| 2026-09-18 | `FULL_LOAD_RESIDUE_TRIAGE_1` | doing/offline | 26691-char spec | Full-list load residue beyond the FlowWorks water fix: RSW patch failures, RSW_* |
| 2026-09-19 | `CUT_FALLOUT_GENERATED_DATA_1` | doing/offline | 15454-char spec | Load C fallout from the Caverns + Polluted Lands cuts (MEASURED 2026-09-19, Tran |
| 2026-09-20 | `COMMISSION_LEDGER_CLEANUP_1` | doing/offline | 73536-char spec | 85 genuinely-owed new-art/def commissions from the 118-row ledger |
| 2026-09-21 | `WORLD_LABEL_SIZE_HIERARCHY_1` | doing/owner | 6644-char spec | All 71 world features sit at the maxDrawSizeInTiles floor - owner ruled size the |
| 2026-09-21 | `FEATURE_DRAWCENTER_UNVERIFIED_1` | doing/owner | 7355-char spec | Only 2 of 71 world features have a verified drawCenter, and growing labels make  |
| 2026-09-22 | `STONEBACK_BOKKA_ART_STANDARD_1` | doing/offline | 8220-char spec | Judge the bokka's 2026-09-11 ported art against modern standards before regenera |
| 2026-09-23 | `FEVERWOOD_ANT_HIVE_DUNGEON_1` | doing/offline | 8160-char spec | Ant hives are reactive procedural dungeons |
| 2026-09-23 | `GREENTIDE_TERROR_REPLACEMENT_1` | proposed/offline | 8905-char spec | Something new and terrifying for the Greentide, replacing the dianoga |
| 2026-09-24 | `SUMP_TAR_NASTINESS_1` | doing/offline | 13320-char spec | Sump nastiness mechanics: sticky tar overlay on any terrain, tarred-pawn hediffs |
| 2026-09-24 | `SUMP_WALKWAYS_1` | doing/offline | 10197-char spec | Sump walkways, two tiers: duckboards (cheap, foul with tar, burn) and glasswalk  |
| 2026-09-24 | `FORCE_DISTURBANCE_REFLAVOR_1` | doing/owner | 5890-char spec | Reflavor vanilla psychic assault/drone storm events as disturbances in the Force |
| 2026-09-25 | `SCALD_WATER_AGITATION_FLECKS_1` | doing/offline | 5491-char spec | Scald wreck shadowData fix + ambient water-agitation ripple mechanism (margin ca |
| 2026-09-26 | `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` | doing/offline | 6088-char spec | Two-front lure numbers, prey-quality gate, and a free-tier second raider |
| 2026-09-27 | `TERMINALBIOMES_REVIEW_FIXES_1` | doing/offline | 5480-char spec | TerminalBiomes 29-file review fix wave: 2 dead tickerType mechanisms (vaulisk lu |
| 2026-10-01 | `FOOTPRINT_TRACK_GRID_1` | doing/offline | 6935-char spec | One footprint grid for the planet: capped TrackGrid + section layer + cell-entry |
| 2026-10-01 | `ABYSS_LIGHTFALL_BROOD_WRECK_1` | proposed/offline | 9751-char spec | Lightfall's bottom: the dragons' brood and the wreck that repairs your ship |
| 2026-10-02 | `SUMP_EFFIGY_RITE_BUILD_1` | proposed/offline | 5739-char spec | Sump Rite B, Mob'Unloo's Price: good thing + hated effigy; Empire held off 5x on |
| 2026-10-02 | `SUMP_SINKING_RITE_BUILD_1` | proposed/offline | 8270-char spec | Sump Rite A, the Sinking: one valuable into the tar; Heat down, fewer raids, cla |
| 2026-10-02 | `LIQUID_BODY_FLUID_IDENTITY_1` | proposed/offline | 6327-char spec | Fluid identity per liquid body (retire per-map ActiveFluid); the merge rule |
| 2026-10-02 | `WEBWORK_DEAD_GIANT_BUILD_1` | proposed/offline | 5644-char spec | Webwork giant: wrapped urraveth skeleton, read bone by bone, loaded bones creak  |
| 2026-10-02 | `WEBWORK_FELLED_NOON_RITE_1` | proposed/offline | 5923-char spec | Rite: The Felled Noon for Sh'kaar (found in Webwork; fell tallest tree at noon,  |
| 2026-10-02 | `WEBWORK_TRACTION_LANCE_BUILD_1` | proposed/offline | 5911-char spec | Traction lance: capstan sibling on one shared pull, learnable at Webwork or Sump |
| 2026-10-02 | `GREENTIDE_BASE_PORT_BUILD_1` | proposed/offline | 7861-char spec | Greentide free tier gets Roil, Breaklight, wet-bulb, dry-air blower, root causew |
| 2026-10-02 | `GREENTIDE_THURROCK_HERD_BUILD_1` | proposed/offline | 6974-char spec | The thurrock: tree-felling giant herd on the built Shatterer aura (no moult) |
| 2026-10-02 | `GREENTIDE_CEDED_ROOM_RITE_1` | proposed/offline | 7159-char spec | The Ceded Room, for Ozzik: cede a room built outside the ship to the jungle; sca |
| 2026-10-02 | `GREENTIDE_STELLOCK_LACE_BUILD_1` | proposed/offline | 6027-char spec | Stellock lace: study a self-sealing branch, craft a cartridge that stops all ble |
| 2026-10-02 | `WARSCAR_OPEN_BOAST_RITE_1` | proposed/offline | 6120-char spec | The Open Boast, for Ozzik, found in the Warscar: a public boast, a warned challe |
| 2026-10-02 | `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` | proposed/offline | 9942-char spec | Rust Cathedral: line-cycle, hum reading, living coolant eels, overhead-sun heat, |
| 2026-10-02 | `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1` | proposed/offline | 6615-char spec | Rust Cathedral giant: the borehulk, a colossal peaceful mining droid with a worn |
| 2026-10-02 | `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1` | proposed/offline | 8986-char spec | Hull bolts: living bolts ride the ship for good as hull pets and the Cathedral's |
| 2026-10-02 | `RUSTCATHEDRAL_WORN_BIT_ARC_1` | proposed/offline | 12928-char spec | The Worn Bit: unbolt the borehulk's drill, Junkers refurbish it, restore the gia |
| 2026-10-02 | `RUSTCATHEDRAL_MENDING_WELD_RITE_1` | proposed/offline | 6844-char spec | The Mending Weld, for Rekko: rebuild a broken stretch of old structure into a wh |
| 2026-10-02 | `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` | proposed/offline | 7912-char spec | The Stranger's Overhaul, for Ohm: repair a free droid, capture it mid-repair or  |
| 2026-10-02 | `FEVERWOOD_RM_CAST_COMPLETION_1` | proposed/offline | 7469-char spec | Fever Wood: build the seven ratified creatures; the skreth brood as the free sec |
| 2026-10-02 | `FEVERWOOD_BROOD_RANSOM_1` | proposed/offline | 6528-char spec | Fever Wood giant story: ransom of its young (world tally, release gift, young ca |
| 2026-10-03 | `UTINNI_DISCOVERY_ACHIEVEMENTS_1` | proposed/owner | 5725-char spec | Utinni discovery achievements mod: surfaces every discoverable and unique mod ca |

## art-pending (1)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-29 | `SWALE_CANAL_ART_REFERENCE_1` | doing/bridge | blocked: Waiting on the RM_Swale_v2 render and its review | Swale art from live reference: build a real FlowWorks canal in game, screenshot  |

## owner-blocked (11)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-08-30 | `ASSAILANT_DUNGEON_BUILD_1` | doing/offline | blocked: re-verified 2026-09-26: design/Jawa/reconciled_lore/FUTURE_VECTORS.md still states creative lock-in owed with  | Build the Assailant flesh dungeon: frozen first-impact complex, thaw-gated, deep |
| 2026-09-02 | `HELIX_TELLUROX_BUILD_1` | doing/offline | blocked: live spawn+corpse-gen proof done clean on canonical save (screenshot+get_cell_info confirmed); HorrorWastes wi | Build Tellurox, Ascendant Helix labour-line livestock |
| 2026-09-02 | `RIVER_STEAM_ANIMATION_1` | doing/offline | blocked: Still needs a live bridge screenshot of a Pyrelands-river map (render-void trap) or an owner glance at a real  | Animated steam rising from the rivers (Pyrelands weather visual) |
| 2026-09-05 | `PLOT_MECHANISM_MODS_WAVE_1` | doing/offline | blocked: re-confirmed 2026-09-26: rules 5/7/8 need cross-mod API reads (tributedemand/RumorHasIt/Ninefold) RimSage cann | Build wave: LLM raid-redesigner + post-battle/event hostility creation + plot-ga |
| 2026-09-06 | `HORRORS_RAIDING_FACTION_1` | doing/offline | blocked: owner ruled 2026-09-09: hold the WHOLE item until HORRORWASTES_BIOME_DISSOLVE_1's owner-reviewed tile-reassign | Horrors become a RAIDING faction (no settlements, nightside-gated encounters) +  |
| 2026-09-06 | `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` | ready/bridge | blocked: Step 1 census already flagged superseded (2026-09-08: checked-in world/ASHKARR_WORLDMAP_mutators.csv commit 20 | Put the unused tile mutators and Geological Landforms landforms on the frozen wo |
| 2026-09-11 | `FAUNA_TOLERANCE_NORMALIZATION_1` | doing/offline | blocked: Offline half DONE (Law 5 + MEASURED census, 196/297 violate). Blocked on the post-restore live harvest for con | Return to canonical-graph fauna normalization, now biome-aware: wide temperature |
| 2026-09-12 | `MOD_VALIDATION_RETROFIT_1` | doing/offline | blocked: still correctly blocked: sole gate is owner ratifying the modcheck sheet FORMAT (Transient/modcheck/Pits_20260 | modcheck full retrofit wave: every shipped mod gets a validation.steps.yaml and  |
| 2026-09-20 | `DONOR_DEFS_PORT_TO_OURS_1` | ready/owner | blocked: spec explicitly forbids starting solo: needs owner-sat plan/ordering first | Port EVERY donor def we use to our own thing defs - owner ruling 2026-09-20; two |
| 2026-09-26 | `BIOME_DEFNAME_MIGRATION_WAVE_1` | proposed/offline | blocked: Re-verified 2026-09-28 on a fresh 630-mod bridge-ready load: still cannot get live tile counts, but the reason | Three biomes renamed 2026-09-26 carry defNames that no longer match their labels |
| 2026-09-28 | `WASTELAND_MECHANICS_BUILD_1` | doing/offline | blocked: Middenshell footprint + plasma-storm gate + storm names need owner/design calls | Build the Wasteland mechanics: 20-cell Middenshell on TitanicCreatures, processo |

## blocked-on-item (20)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-06 | `KYBER_TRADE_PLOT_1` | doing/offline | blocked: stale premise fixed: GM_BLACKBOARD_SHADOW_M4_1/CATHEDRAL_REGARD_BLACKBOARD_1 built the external Heat/Hutt-Inte | Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi fro |
| 2026-09-09 | `MOVING_DUNES_BUILD_1` | doing/offline | blocked: Engine is already built (~1,900 lines, dotnet build 0W/0E 2026-09-09, selftest 13/13) and not deployable-alone | Build the dunes engine per MOVING_DUNES_DESIGN.md v2 (model=opus, ~1.1-1.4k line |
| 2026-09-13 | `CATHEDRAL_MISSION_BOON_OFFERS_1` | doing/offline | blocked: Genuinely blocked, not just offline-stuck: spec depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, still doing  | Deniably-sourced Assailant missions + Heat-gated gravtech boons |
| 2026-09-13 | `CATHEDRAL_STAGE_COMMENTARY_POOLS_1` | doing/offline | blocked: Verified offline: no RUT_HumCommentary RulePack exists anywhere in src/ yet (grep clean) — RUST_CATHEDRAL_MECH | Stage-keyed RUT_HumCommentary pools + the bans-2/6 linter gate every arc item ru |
| 2026-09-13 | `CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1` | doing/offline | blocked: Verified offline: depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, still doing — real §2 inputs unbuilt) and  | The A4 Imperial-survey misdirection quest, three branches, K2 anti-laundering |
| 2026-09-13 | `CATHEDRAL_DESCENT_REVEAL_SITE_1` | doing/offline | blocked: Verified offline: depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, still doing) and item 3 (CATHEDRAL_STAGE_C | The A7 real under-plate descent site + reveal beat + A1 Utinni-receiver lore pro |
| 2026-09-13 | `CATHEDRAL_MECHANOID_PASS_VERBS_1` | doing/offline | blocked: Verified offline: depends on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1) for stage+verbs source, still doing/unship | GRANT/REVOKE mechanoid-pass instrument, scoped Harmony hostility exception (C#,  |
| 2026-09-13 | `MODCHECK_DONOR_ENVIRONMENTS_1` | doing/offline | blocked: Armoury half fully resolved offline (kaitorisenkou.ModularWeapons2 + guy762.MM.KotORCore, recorded in src/RimS | MODCHECK_DONOR_ENVIRONMENTS_1 Armoury and WreckedMachines modcheck environments: |
| 2026-09-13 | `LIQUID_THIRST_CHAIN_1` | doing/deploy | blocked: Own spec's Watch-out: 'Depends on LIQUID_BOTTLE_LOOP_1.' Verified this session: LIQUID_REGISTRY_CORE_1 now has | Water cleaning chain crude/household/industrial wired to DBH thirst (DBHThirst M |
| 2026-09-13 | `DEBUG_ACTION_ENUM_CRASH_1` | doing/bridge | blocked: jawa/debug_action_yielders built and compiles clean (0 errors) -- root cause confirmed via RimSage: vanilla De | search_debug_actions/list_debug_action_children(Actions) crash on any broad quer |
| 2026-09-13 | `BAZAAR_PRICE_ENGINE_1` | doing/deploy | blocked: The item's own Watch-out names BAZAAR_WINDOW_GRID_1 as a dependency, and its two read-side consumers (session- | The Bazaar slice 2: read-side RM_BazaarEconomy (worldTag-seeded buckets, history |
| 2026-09-13 | `BAZAAR_HAGGLE_DUEL_1` | doing/deploy | blocked: Real dependency chain still open: BAZAAR_WINDOW_GRID_1 is 'doing' (no WindowStack.Add intercept/session object | The Bazaar slice 3: WHOLE-DEAL patience-meter haggle duel (owner: per-item rejec |
| 2026-09-13 | `BAZAAR_BANTER_LINES_1` | doing/deploy | blocked: Part A's event pool (push won/lost/crit/lockout/greeting/closing) and personality set (stingy/desperate/gullib | The Bazaar slice 5: authored banter pools (day one) + dormant claude -p Oracle c |
| 2026-09-13 | `BAZAAR_BROKER_TAB_1` | doing/deploy | blocked: Same open Bazaar dependency chain as the other two slices I checked this pass: BAZAAR_WINDOW_GRID_1 is still d | The Bazaar slice 4: bulk-liquid Broker tab — renders Liquid Logistics' tank API  |
| 2026-09-25 | `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1` | doing/offline | blocked: Blocked on FALL_LINE_ARRIVAL_MECHANISM_1's Band B flee/lurker think-tree insert, which has not landed (still u | Feral-race crash-survivor pawnkind + permanent mental-scar hediff + capture-to-s |
| 2026-09-26 | `WEBWORK_EGG_BROKER_CHANNEL_1` | doing/offline | blocked: Re-verified 2026-09-26: RM_Window_Bazaar is still an inert Dialog_Trade subclass with no WindowStack.Add Harmo | Add the egg black-market broker channel as a Bazaar tab, once Bazaar has tabs |
| 2026-09-28 | `CRACKEDLANDS_RULED_CONTENT_1` | doing/offline | blocked: defs+roster complete and validated (0 errors); remaining is a live quicktest verify pass (needs deploy+bridge) | Build the Cracked Lands ruled content: roster surgery (vanilla zoo out, RM_ migr |
| 2026-10-01 | `WARSCAR_AEROSOL_SCREEN_1` | ready/offline | blocked: 11-point build; depends on WARSCAR_RAINBOW_POOLS_1 and WARSCAR_OLD_TONGUE_1; needs split a-d (see Transient/wo | Warscar projectors and aerosol screen: lift ShipShields particulate core to RM,  |
| 2026-10-01 | `WARSCAR_RAINBOW_POOLS_1` | doing/offline | blocked: Standalone slice built offline (registry row, pools, cycle+icons, tap, 4 reagents, journal, reader, catalyst,  | Warscar rainbow pools: reaction-liquor registry row, phase cycle with colour-bli |
| 2026-10-04 | `ABYSS_CRAGS_ART_ON_PORTED_DEFS_1` | proposed/offline | blocked: no ported Abyss donor-cast defs exist yet | Wire the 12 done crags_* art sets (+ the dusk rat redo when commissioned) onto t |

## blocked-other (2)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-29 | `CAULDRON_MECHANICS_BUILD_1` | doing/offline | blocked: Remaining parts need design calls (gas grid, falter tell foreknowledge) or unbuilt FlowWorks/ruins; not offlin | Build the Cauldron mechanics: engine-underfoot soundscape + falter tell, four ra |
| 2026-09-30 | `CONTAGION_GPT_ENRICHMENT_1` | doing/offline | blocked: Stopped for handoff 2026-09-30; not started - pick up fresh | Contagion enrichment (GPT consult 2026-09-30, owner-picked by card): Draftprints |

## bridge/live-only (117)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-02 | `MASS_VALIDATION_LADDER_1` | doing/bridge | needs bridge | Batched validation ladder: get_defs deep-serialize, manifest runner, hot-reload  |
| 2026-09-02 | `SHIELD_MODS_LEVERAGE_1` | doing/bridge | needs bridge | Find existing shield mods, study and make compatible; tuned-plasma-field model p |
| 2026-09-05 | `INHABITED_AUGMENTATION_BUILD_1` | doing/bridge | needs bridge | Build the tile-augmentation content: rimplace templates + Inhabited wiring for t |
| 2026-09-05 | `VAULT_THAW_QUEST_FAMILY_1` | doing/bridge | needs bridge | Six Forsaken vault layouts exist but nothing makes them play - no QuestScriptDef |
| 2026-09-06 | `COLD_LOAD_RUN_SHEET_4` | doing/game-up | needs game-up | Run sheet for the next full-list load: three readings owed from the 2026-09-06 o |
| 2026-09-06 | `DROIDWORKS_FORMAT_TIERS_1` | doing/bridge | needs bridge | Format tiers blank/mindless/programmable/sapient with needs by tier (ruling 4),  |
| 2026-09-07 | `RUST_CATHEDRAL_MECHANICS_1` | doing/bridge | needs bridge | Rust Cathedral C# kit: hum-mood system (attitude value, layered tones, bolt-danc |
| 2026-09-08 | `WAR_LAB_CRATER_HOOK_1` | doing/offline | blocked: wired RUT_WarLabReactorCore (CompIgniteCraterOnDestroy) + deployed; live ignition/save-load/world_commit quick | Ignition->crater world-tile mutation C# hook for the war lab, blocked on LIQUID_ |
| 2026-09-09 | `BIOME_ENRICHMENT_DESERT_WASTELAND_1` | doing/bridge | needs bridge | Enrichment wave (review B1): Desert (53% zero-mutator) + Wasteland (63%) — the t |
| 2026-09-12 | `MOD_OPTIONS_RETROFIT_1` | doing/offline | blocked: 52 mods now carry real, compile-verified Mod Settings (was 46+3; +ShokkweaveEconomy/EggReckoning/WildsteamEggB | Superb mod-options support across ALL our mods: retrofit every shipped RimMandra |
| 2026-09-12 | `SARLACC_HABITAT_BUILD_1` | doing/offline | blocked: advanced items 4+7 of Owed list this pass (DBH thirst wiring, water_doctrine amend), commit ed5134abf; still o | Build the accepted sarlacc design (sarlacc_native_habitat_draft.md, ACCEPTED + a |
| 2026-09-12 | `BIOME_WORLD_SWITCH_WAVE_1` | doing/bridge | needs bridge | World-switch every donor/vanilla-painted tile to its owned RUT_ successor: MEASU |
| 2026-09-13 | `CATHEDRAL_STAGE_HUM_BRIDGE_1` | doing/bridge | needs bridge | Stage-to-hum-baseline bridge lane into RM_BiomeAttitudeDef (C#, row-3) |
| 2026-09-13 | `LIQUID_BOTTLE_LOOP_1` | doing/deploy | blocked: live: fill job never produces a filled bottle (4 tries, 3 pawns); revert/rot timers unbuilt so verify bar cann | Bottles as real items: fill/use/dirty/wash loop (dirty behind a toggle, default  |
| 2026-09-13 | `BAZAAR_DISPLACEMENT_PASS_1` | proposed/owner | blocked: precondition unmet: Bazaar slices 1-2 not live-proven yet (WINDOW_GRID needs deploy, PRICE_ENGINE BLOCKED) — p | Retire Trade UI Revised + Utility Columns + VTE from the campaign list after Baz |
| 2026-09-14 | `BACTA_REVIVAL_MECHANIC_1` | doing/deploy | blocked: live: toggle/window/laws pass, but heart-destroyed corpse revives into re-death (design call) and WorkGiver ne | Bacta revival of the recently dead (owner ruling: works on dead bodies IF retrie |
| 2026-09-14 | `BACTA_TANK_CORE_1` | doing/bridge | needs bridge | Bacta Tank core: RSW mod skeleton, tank building, trade-scarce fluid on the Liqu |
| 2026-09-18 | `AQUATIC_WATER_BREATHING_GENE_1` | doing/bridge | needs bridge | Design and build a real water-breathing mechanism (gene or hediff) for the 4 aqu |
| 2026-09-18 | `FISH_BESTIARY_BUILD_1` | doing/offline | blocked: WS+Greentide real catches pass; Twilight tile map is 100% deep brine (unfishable), Cracked Lands/Wasteland not | Build the fish bestiary: 32 RUT_ species across 8 registers on 7 waters, per-bio |
| 2026-09-19 | `DEEPS_FAUNA_MECHANICS_1` | doing/bridge | needs bridge | Deeps creature mechanics from the fauna verdicts: Grabber hold-and-crush, Soulch |
| 2026-09-23 | `FEVERWOOD_BOUGH_SOIL_TERRAIN_1` | doing/game-up | needs game-up | The crown cannot grow anything: boughway is fertility 0, so bough-soil is owed |
| 2026-09-24 | `SUMP_GASLIGHT_1` | doing/offline | blocked: live: RUT_ScrubTarred consumes solvent but leaves RUT_Tarred and spawns no Sumpgas (2 runs); lamp animation/st | Sump gaslight: tar+acid reaction makes green gas (Helixien integration OK), warb |
| 2026-09-25 | `REGROWTH_RECOLOR_MINEABLES_NRE_1` | doing/offline | blocked: Real trace (Transient/Player.log.geneticrim_ctor_nre_2026-09-25 L11288-92, and 09-24 before_bacta_swap L14377- | Every full-list save load logs 'Exception from long event: NullReferenceExceptio |
| 2026-09-26 | `SUMP_TAR_FIRE_NETWORK_1` | doing/bridge | needs bridge | Network fire with gate firebreaks; wire belch to glass-cooling |
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
| 2026-10-01 | `STILLSAND_CONTENT_LIVE_PROOF_1` | proposed/game-up | needs game-up | Prove the built Stillsand cast live (atlas, zuurrik on blood) and swap four plac |
| 2026-10-01 | `STILLSAND_EVENT_CREATURES_LIVE_1` | proposed/game-up | needs game-up | Live-prove the krayt attack and muurrok on a Stillsand quicktest, and live-fire  |
| 2026-10-01 | `STILLSAND_PRECIOUS_CAVES_LIVE_1` | proposed/game-up | needs game-up | Precious caves: ten live Stillsand quicktest maps |
| 2026-10-01 | `STILLSAND_GLASS_CHAIN_REMAINDER_1` | doing/game-up | needs game-up | Stillsand glass chain remainder: krayt lens, goggles recipe, fulgurite art, art  |
| 2026-10-01 | `STILLSAND_RETURN_REMAINDER_1` | proposed/game-up | needs game-up | Stillsand Return remainder: live proof, the visible Return line, cave debt stone |
| 2026-10-01 | `STILLSAND_DUNE_GALE_LIVE_1` | proposed/game-up | needs game-up | Stillsand dune gale: live proof (mass delta, sun off, one emergence, carry lette |
| 2026-10-01 | `CRACKEDLANDS_ENRICHMENT_QUICKTEST_1` | proposed/bridge | needs bridge | Quicktest-prove the Cracked Lands enrichment tranche by state reads: five beats, |
| 2026-10-01 | `STILLSAND_FIXES_LIVE_PROOF_1` | proposed/game-up | needs game-up | Live proof for the five 2026-10-01 live-session fixes |
| 2026-10-01 | `CAULDRON_ENRICHMENT_LIVE_PROOF_1` | proposed/game-up | needs game-up | Quicktest-prove the offline-built Cauldron enrichment: assay grade line, vexxiss |
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
| 2026-10-02 | `GELATINOUSSLIME_PIT_SOLVENT_1` | doing/offline | blocked: Free slice built (3 pit recipes, toggle, validation) uncommitted; remaining: spec 3 Rot's finest input patch i | Slime pit as a solvent: renders toxic or indigestible food safe (Rot's finest in |
| 2026-10-02 | `NORTHSTAR_ISHKO_PILOT_1` | proposed/bridge | needs bridge | Northstar pilot on IshkoDarkLandmarks: walk arrows, ishko tier, mock clean, reco |

## skip (64)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-01 | `TECHPRINT_FACTION_GATING_1` | doing/owner | skip list / owner unblock list | Code the four research access classes: common / faction-held techprints / jawa-s |
| 2026-09-06 | `TREE_GRAPHICS_OWNERSHIP_1` | doing/offline | skip list / owner unblock list | Own tree art at our scales: generate custom tree graphics (sweetline trees first |
| 2026-09-06 | `MACRO_GENERATOR_V0_1` | ready/owner | skip list / owner unblock list | Macro generator v0: ONE idea per map — chooser + plan + terrain grid, graded on  |
| 2026-09-06 | `MAPGEN_GL_SHEET_1` | doing/owner | skip list / owner unblock list | Map generator: 8 plans through the GL emitter, quicktest screenshots beside pain |
| 2026-09-06 | `MAPGEN_CONVERGENCE_LOOP_1` | ready/bridge | skip list / owner unblock list | Map generator convergence loop: painter vs GL vs corpus, iterate until the owner |
| 2026-09-06 | `MAPGEN_PAINTER_V1_1` | doing/owner | skip list / owner unblock list | Map generator painter v1: organic masks, elevation→terrain bands, hydrology with |
| 2026-09-06 | `DROIDWORKS_PRIMITIVE_TIER_1` | doing/offline | skip list / owner unblock list | Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats |
| 2026-09-09 | `LANDMARK_NAMING_PASS_1` | doing/game-up | skip list / owner unblock list | Review B2: 32 landmark names reused (worst 'Dead Sarlacc' x7) — hand-name the ~1 |
| 2026-09-10 | `CRYPTOFORGE_HARVEST_RETIRE_1` | doing/offline | skip list / owner unblock list | Harvest then retire VQE Cryptoforge: (1) reproduce the 18 SALVAGE_PALETTE-cited  |
| 2026-09-13 | `FLORA_LEGIBILITY_BAR_1` | doing/offline | skip list / owner unblock list | Flora legibility bar: own grading pass + model (no keyline law), sizeBin-scaled  |
| 2026-09-17 | `PIT_SUPERDEEP_COLLAPSE_1` | proposed/offline | skip list / owner unblock list | Collapse the pit onto the D/F primitive: a superdeep cell you cannot climb out o |
| 2026-09-19 | `DEEPS_FAUNA_MECHANICS_2` | proposed/bridge | skip list / owner unblock list | Deeps fauna mechanics, second pass on DEEPS_FAUNA_MECHANICS_1: grabber-side crus |
| 2026-09-19 | `REBOOT_BREAKGLASS_VERIFY_1` | proposed/offline | skip list / owner unblock list | Verify the break-glass path survives a Windows reboot: WSL Keepalive must bring  |
| 2026-09-20 | `DESERT_FAMILY_PORT_EXECUTION_1` | proposed/offline | skip list / owner unblock list | Port all 109 desert-family species to our own defs and our own art - owner ruled |
| 2026-09-23 | `HOSTILE_MOBILE_PLANTS_1` | doing/offline | skip list / owner unblock list | Hostile mobile plants as animals - a new creature class |
| 2026-09-23 | `GREENTIDE_HUMMING_GROVE_1` | doing/owner | skip list / owner unblock list | A grove that hums at differing pitches as you walk through it |
| 2026-09-26 | `SUMP_TAR_LIVING_SYSTEMS_1` | proposed/offline | skip list / owner unblock list | Living-map responders; tar rain mod-vs-scenario split |
| 2026-09-28 | `CONTAGION_MECHANICS_BUILD_1` | doing/offline | skip list / owner unblock list | Build the Contagion mechanics: Burn/Bloom weather + tells, the Coalescence (one  |
| 2026-09-28 | `BLUEDESERT_MECHANICS_BUILD_1` | doing/offline | skip list / owner unblock list | Build the Blue Desert mechanics: vhaulk trigger-gated detonation (EMP-on-hit tra |
| 2026-09-28 | `CRACKEDLANDS_FULL_RENAME_1` | doing/owner | skip list / owner unblock list | Full rename FloodedCanyon -> CrackedLands everywhere: defs, code, file names, do |
| 2026-09-28 | `CRACKEDLANDS_MECHANICS_BUILD_1` | doing/offline | skip list / owner unblock list | Build the Cracked Lands mechanics: the Swale (FlowWorks-normal, Utinni-locked bi |
| 2026-09-29 | `FORGE_CYCLE_MECHANICS_1` | doing/offline | skip list / owner unblock list | Build the Forge fire-and-water grand cycle: gas-wash ignition, boiling rain + Fl |
| 2026-09-29 | `LEANINGSCRUB_MECHANICS_BUILD_1` | doing/offline | skip list / owner unblock list | Build the Leaning Scrub mechanics: Stall+Gale wind calendar, the Lean scent/fire |
| 2026-09-30 | `SOLAR_HEAT_EXPOSURE_1` | doing/offline | skip list / owner unblock list | Planet-wide sun heat: sun exposure feeds VANILLA heat (no new heat kind), per-bi |
| 2026-09-30 | `LONGSHADE_BEDAZZLE_MECHANICS_1` | doing/offline | skip list / owner unblock list | Long Shade bedazzle mechanics: golden-hour perpetual sunset + pinned sun angle,  |
| 2026-09-30 | `LONGSHADE_BEDAZZLE_CONTENT_1` | doing/offline | skip list / owner unblock list | Long Shade bedazzle content: wire the finished-but-unwired art (7 magenta creatu |
| 2026-09-30 | `WARCASKET_WASTE_RUN_REMAINDER_1` | proposed/owner | skip list / owner unblock list | Cask-bay follow-ons: five waste-run destinations, Stenchlands cask item, Junker  |
| 2026-10-01 | `REPO_RENAME_SYMLINK_RETIRE_1` | proposed/offline | skip list / owner unblock list | Retire the Rimworld -> RimMandrake symlink: repoint every old-path reference, th |
| 2026-10-01 | `PYRELANDS_SHIP_READINESS_1` | proposed/offline | skip list / owner unblock list | Pyrelands SHIPPED rung: Ashwallow/Emberscythe art, code review CLEAN, settings g |
| 2026-10-01 | `FLOWWORKS_NORTHSTAR_SHIP_1` | proposed/offline | skip list / owner unblock list | FlowWorks SHIPPED: settings superb, art complete, code review CLEAN, deployed |
| 2026-10-01 | `CRACKEDLANDS_LEDGES_OF_MERCY_1` | proposed/owner | skip list / owner unblock list | Ledges of Mercy (from CRACKEDLANDS_GPT_ENRICHMENT_1 §1): refuge ledges, carvings |
| 2026-10-01 | `CRACKEDLANDS_FIVE_BEATS_AUDIO_1` | proposed/game-up | skip list / owner unblock list | Bespoke audio for the five beats (6 SoundDefs on vanilla-clip placeholders) + th |
| 2026-10-01 | `CRACKEDLANDS_THREE_HEIGHT_FLORA_1` | proposed/owner | skip list / owner unblock list | Qirra mats + talus clasps (names swept clean): art to review sheet before defs;  |
| 2026-10-01 | `CRACKEDLANDS_SALVAGE_CLAIM_CREW_1` | proposed/owner | skip list / owner unblock list | Floodline salvage claim stakes + rival crew visitor lord (scatter already built) |
| 2026-10-01 | `CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1` | proposed/owner | skip list / owner unblock list | Peakstorm Light: dust briefly reverses (no WeatherDef field; overlay vs mote eve |
| 2026-10-01 | `FORGE_KEELWORK_REMAINDER_1` | doing/owner | skip list / owner unblock list | Floatstone keelwork remainder: glassy ring at launch, brace art, and whether pay |
| 2026-10-01 | `FORGE_SPUNSTONE_SOURCES_1` | proposed/owner | skip list / owner unblock list | Spunstone bonding remainder: foundry salvage as a study source, and what the hig |
| 2026-10-01 | `FORGE_WHITE_PLUME_FRONTS_1` | doing/owner | skip list / owner unblock list | White plume fronts: moving quench-steam fronts that obscure shooters, soak groun |
| 2026-10-01 | `FORGE_SKY_PASTURES_1` | doing/owner | skip list / owner unblock list | Sky pastures: render the vapour-column grid, ash spirals, column-aware hunting a |
| 2026-10-01 | `FORGE_DHOKKUR_WAYS_1` | proposed/owner | skip list / owner unblock list | Dhokkur ways: outcrop disguise clues, rain-wake groan, path memory on glass-poli |
| 2026-10-01 | `FORGE_DHUVVOX_SWARM_REMAINDER_1` | doing/owner | skip list / owner unblock list | Dhuvvox clock remainder: nodules as Things vs sealed pawns, swarm aggregation, s |
| 2026-10-01 | `LONGSHADE_MIDDENS_DESIGN_1` | proposed/owner | skip list / owner unblock list | Lee-side middens: owner to rule what a midden is, what searching yields, the cle |
| 2026-10-01 | `SHADECRAFT_LESSONS_DESIGN_1` | proposed/owner | skip list / owner unblock list | Shade gear learned by study: lesson-to-piece mapping, and Long-Shade-only lesson |
| 2026-10-01 | `GLOOMCAST_WAKE_RIDERS_1` | proposed/owner | skip list / owner unblock list | Gloomcast shadow: which small grazers actively follow it, and whether feeding le |
| 2026-10-02 | `LASSO_CHERRYPICKER_REMOVAL_1` | proposed/offline | skip list / owner unblock list | Remove lassos: Cherry Picker cut AM_LassoCloth + Melee Animation lasso spawning  |
| 2026-10-02 | `PIT_TEMPERATURE_SOFTENING_1` | proposed/offline | skip list / owner unblock list | Pit temperature couples hard to ambient and wears down resistance; Exposed Priso |
| 2026-10-02 | `SUPERDEEP_PRISON_ROOM_1` | proposed/offline | skip list / owner unblock list | An enclosed superdeep area is a room; a prisoner bed makes it a prison; capture  |
| 2026-10-02 | `PIT_FILL_EFFECTS_1` | proposed/offline | skip list / owner unblock list | What a fluid does to a pit occupant: drowning at D=4, poison keyed to fill, burn |
| 2026-10-02 | `ROT_UNJOINING_RITE_1` | proposed/offline | skip list / owner unblock list | The Unjoining, for Ta'Baa: a symbiont-joined colonist purged until it dies, just |
| 2026-10-02 | `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` | doing/owner | skip list / owner unblock list | A titanoslime chunk opens a Forsaken vault blocked by an Assailant seal (seal do |
| 2026-10-02 | `GELATINOUSSLIME_JOINING_WATER_RITE_1` | proposed/owner | skip list / owner unblock list | The Joining Water rite: join hands holding slime, one person's permanent hediffs |
| 2026-10-02 | `MIASMA_WARDEN_MOTHER_ART_1` | doing/offline | skip list / owner unblock list | Warden mother art, with an aged variant for her last season |
| 2026-10-03 | `CHILL_DIVE_DENSITY_SAMPLER_1` | doing/game-up | skip list / owner unblock list | Chill dive spawns obey density (not one-of-each); number set on a live walk with |
| 2026-10-03 | `SCALD_WALKING_PASTURE_1` | doing/offline | skip list / owner unblock list | Scald bottom-walkers: a grazing herd creature first, then the Walking Pasture (c |
| 2026-10-03 | `SCALD_GALLERY_SCHEMATIC_UNLOCK_1` | proposed/owner | skip list / owner unblock list | Return Gallery: what the immersion-engineering schematic unlocks (RM_ImmersionSc |
| 2026-10-03 | `FEVERWOOD_HIVE_GUARD_CHAMBER_1` | proposed/offline | skip list / owner unblock list | Ant hive kept guard at the chokepoints: invent the guard creature, station it wh |
| 2026-10-03 | `GREENTIDE_ILLISK_BUILD_1` | proposed/owner | skip list / owner unblock list | Build the Illisk shoal (fast, nearly unkillable except explosives); open: one pa |
| 2026-10-03 | `UNFINISHED_LINE_SITE_CHOICE_1` | proposed/owner | skip list / owner unblock list | Unfinished Line site choice (where the line stands, A-D) offered at the end of b |
| 2026-10-03 | `MINDSTONE_MATRIX_KINDLED_BUILD_1` | proposed/offline | skip list / owner unblock list | Mindstone matrix + the Kindled's first making: RUT_Mindstone + head casing at th |
| 2026-10-03 | `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1` | proposed/offline | skip list / owner unblock list | Abyss: the Dark muffles every map sound (Harmony on sample creation) |
| 2026-10-03 | `SEABED_DESCENT_ASCENT_1` | proposed/bridge | skip list / owner unblock list | Gravship flies from a sea tile down to its RM_SeabedLayer floor and back up (sea |
| 2026-10-03 | `SEA_DIVE_HATCH_REMOVE_1` | proposed/offline | skip list / owner unblock list | Delete RM_SeaDiveHatch, RM_SeaDiveExit and their genstep/anchors once descent an |
| 2026-10-04 | `RUSTCATHEDRAL_GOODWILL_FLOOR_1` | proposed/bridge | skip list / owner unblock list | Rust Cathedral hum reads a permanent-enemy faction's goodwill: calm bands may be |
| 2026-10-04 | `VANILLA_XENOTYPE_DEFCUT_1` | proposed/offline | skip list / owner unblock list | Xenotype cut slice 2: typed Cherry Picker cuts of the 11 (XenotypeDef/Neandertha |

## stale (40)

| filed | id | state/needs | why | title |
|---|---|---|---|---|
| 2026-09-14 | `BACTA_TANK_ART_1` | doing/offline | no item prose file | Bacta tank art from the ESB canon image (tall 2:1 cylinder, translucent pale-blu |
| 2026-09-15 | `EVENT_TRACE_PROPS_LIBRARY_1` | proposed/offline | no item prose file | Design a props library of event traces: blaster marks, burn/scorch marks, floor  |
| 2026-09-19 | `ROT_FAUNA_KIN_WIRING_1` | proposed/deploy | no item prose file | Wire the ruled Rot fauna kin/alarm table onto the 16 race defs (UtinniPatches, F |
| 2026-09-20 | `MYCOID_COLOSSUS_LIVE_LOOK_1` | doing/game-up | no item prose file | MYCOID_COLOSSUS_LIVE_LOOK_1 |
| 2026-09-25 | `SALVAGE_WRECKAGE_EVERYWHERE_1` | proposed/offline | no item prose file | Salvage wreckage across the planet: wreck families (hulls, tanks, frames, speede |
| 2026-09-25 | `STATUE_ART_EXPANSION_1` | proposed/offline | no item prose file | Statue expansion: assess the statue-choice mod (patch vs own), RM statues with f |
| 2026-09-25 | `JAWA_SWIM_HOOD_KEEP_1` | doing/deploy | no item prose file | URGENT (owner, chat 2026-09-25: Jawa must never be seen without a hood): swimmin |
| 2026-09-25 | `MINERALS_WHERE_THEY_BELONG_1` | proposed/owner | no item prose file | Design (later): minerals where they belong — per-biome allocation of every miner |
| 2026-09-26 | `SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1` | doing/offline | no item prose file | One gravship can only ever visit ONE sea floor: MapPortal caches its pocket map, |
| 2026-09-27 | `SURFACE_RIVER_WEIRS_1` | proposed/offline | no item prose file | Port the weir / bank-works / breach system to ordinary surface river tiles (owne |
| 2026-09-27 | `SPECULATIVE_ART_COMMISSION_1` | proposed/offline | no item prose file | Speculative art commission 2026-09-27 (owner directive, free pipeline) |
| 2026-09-28 | `WARLAB_CRATER_ACCIDENTAL_TRIGGER_1` | proposed/offline | no item prose file | RUT_WarLabReactorCore's CompIgniteCraterOnDestroy fires the planet-wide Chill cr |
| 2026-09-30 | `JOSSUR_FLIGHT_FRAMES_1` | doing/offline | no item prose file | Flight flip-book frames for RM_Jossur (optional; flight stat already set) |
| 2026-09-30 | `FORGE_MISSING_ART_1` | doing/offline | no item prose file | No render anywhere: RM_CinderCrust (identity unwritten), RUT_TibannaGas, RUT_Fou |
| 2026-09-30 | `WARCASKET_CASK_ART_1` | doing/offline | no item prose file | Art for RM_CaskBay (building) and RM_HalfExtractedCore (item); texPaths wired un |
| 2026-09-30 | `SEA_DIVE_FLOOR_TERRAIN_1` | doing/offline | no item prose file | Gravship dive floors ignore the seas' terrain bands: GenStep_SeaFloorTerrain pai |
| 2026-09-30 | `SUBSTRUCTURE_PROPS_LAYER_OOB_1` | doing/offline | no item prose file | Live 2026-09-30b: 'Could not regenerate layer RimWorld.SectionLayer_Substructure |
| 2026-10-01 | `CONTAGION_GROWN_LIMBS_ART_1` | doing/offline | no item prose file | Art for Pillar Arm and Lash (replace Anomaly placeholder textures) plus item ico |
| 2026-10-01 | `GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1` | proposed/bridge | no item prose file | JawaBench tools the Graffiti trial cannot fake: thing_graphic, spawn_variant, ru |
| 2026-10-02 | `NORTHSTAR_SITUATIONAL_ROLLOUT_1` | proposed/bridge | no item prose file | Flip modcheck --situational to default after an abort-only pass over every suite |
| 2026-10-02 | `NORTHSTAR_COMPANION_GAPS_1` | proposed/deploy | no item prose file | Companion tools: pawn census (mental state+job), incident-queue peek/selective r |
| 2026-10-02 | `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1` | proposed/bridge | no item prose file | Prove a gravship can land in a non-hostile settlement (Hutt test site first) wit |
| 2026-10-02 | `NORTHSTAR_VALIDATION_SKILL_1` | proposed/offline | no item prose file | Carve a northstar-validation skill out of rimworld-debug-testing: bland saved wo |
| 2026-10-02 | `ALPHA_ANIMAL_PORTS_REHOME_1` | proposed/offline | no item prose file | Five Alpha Animals creatures have RSW_-prefixed ports (Wildpawn=RSW_Durrok, Wild |
| 2026-10-03 | `SEABED_PER_SEA_FLOORS_1` | doing/offline | no item prose file | Sea-floor planet layer Phases 3+4: guard the FinalizeInit plant crash, then a re |
| 2026-10-03 | `SCALD_BATHING_RITE_1` | doing/offline | no item prose file | Scald rite: water pilgrims bathe at the cool margins (design; register entry; wa |
| 2026-10-03 | `GRAFFITI_WALL_LINKED_CROP_1` | proposed/game-up | no item prose file | Graffiti wall marks may draw only a 1/16 crop of their art: wall-linked graphics |
| 2026-10-03 | `WARSCAR_CHOTRIX_SIGNS_1` | proposed/offline | no item prose file | Chotrix readable signs: track-grid prints and dragged-kill marks (needs FOOTPRIN |
| 2026-10-03 | `WEEPINGSTONES_NET_FLEEING_FLIER_1` | proposed/bridge | no item prose file | NET job cannot catch a wild skarrin: it flies off-map before the handler arrives |
| 2026-10-03 | `FALL_LINE_MUTATOR_PLACEMENT_1` | proposed/bridge | no item prose file | Place the RUT_FallLine tile mutator on the 308 Fall Line + The Breaks tiles of t |
| 2026-10-03 | `FALL_LINE_WRECKAGE_CREATURES_PORT_1` | proposed/owner | no item prose file | BMT_BunkerBug and BMT_Megapleura (Fall wreckage creatures) are absent: load Biom |
| 2026-10-03 | `FLAME_STATUES_MOD_BUILD_1` | proposed/offline | no item prose file | Statue spec steps 4-7: mandrake.rm.flamestatues (three Chemfuel flame statues, R |
| 2026-10-03 | `WARSCAR_PILGRIM_CAMP_SITES_1` | proposed/owner | no item prose file | Pilgrim camps as world SitePartDefs at authored locations on the fixed planet (W |
| 2026-10-03 | `WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1` | proposed/offline | no item prose file | Pilgrim journals as Antiquities artifacts: catalogue at the Reading Station also |
| 2026-10-03 | `FLOWWORKS_QUARRY_DIGGING_1` | proposed/offline | no item prose file | Design pass: extend FlowWorks with the quarry concept - digging a canal can unco |
| 2026-10-04 | `SUMP_CAPSTAN_DRAWJOINT_RESEARCH_1` | proposed/offline | no item prose file | Capstan turret spec 4: hidden research taught by studying two preserved draw-joi |
| 2026-10-04 | `BELT_WATER_HARNESS_1` | proposed/bridge | no item prose file | Bland-map water cell helper: Miasma return proof and Greentide vurrak need water |
| 2026-10-04 | `BLUEDESERT_FLORA_PLANT_REFUSAL_1` | proposed/bridge | no item prose file | BlueDesert flora_spawns still refuses 8 plants at tile temp -5 (retile read back |
| 2026-10-04 | `DEEP_LAYER_BELT_HARNESS_1` | proposed/bridge | no item prose file | LanternDeeps Deep-layer proofs say comp only on a Deep: harness needs a Deep map |
| 2026-10-04 | `CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1` | proposed/offline | no item prose file | Utinni lock for RM_Swale: locked in the campaign until discovered in the Cracked |
