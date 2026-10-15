# Release gap list - GimmeSomeSlack / FlowWorks / Pyrelands (BENCH inventory, 2026-10-15)

Read-only inventory. Sources: `rimflow show` on every candidate (state/needs/owes), the ledger, the three mods' source and defs,
design docs, `infrastructure/state/modcheck_status.json`. Newest live evidence: round r6 at ONE HEAD `902b565c93`
(`Transient/bench_live_20261015_r6/SITTING.md`) and the r9 river probes (`Transient/bench_live_20261015_r9/SITTING.md`).
Size: S under 1h, M 1-3h, L over 3h. Blocker: build / live proof / owner look / owner decision / art.
Items dropped as not in-mod (only mention the mod in passing): all `*_FIRST_SCRIPT_1` for other mods, other biome mods' items, BACTA_*,
GLASS_TO_TRANSPARISTEEL_1, SUMP_*, VAULT_DUNGEON_BUILD_1, WARSCAR_RAINBOW_POOLS_1, LIQUID_INDUSTRY_SETPIECES_1, STILLSAND_*, FORGE_* (Forge is its
own biome mod), PYRELANDS_STRUCK_GLASS_RITE_BUILD_1 (campaign-tier rite, `mandrake.rut.rites`, not in the Pyrelands folder).

## 0. Release mechanics: what "release" means today

**There is no documented Steam Workshop publish procedure and none of the three mods has a Workshop page.** Measured:

| fact | GimmeSomeSlack | FlowWorks | Pyrelands |
|---|---|---|---|
| packageId | `mandrake.rm.gimmesomeslack` | `mandrake.rm.flowworks` | `mandrake.rm.pyrelands` (but ships COMPOSED inside `mandrake.rm.biomes`; `src/RimMandrake/BiomesShell`, `Biomes.compose.json`) |
| About.xml | yes, Harmony dep only, supportedVersions 1.6 | yes, Harmony + Odyssey-aware, loadAfter list | yes; description says "self-contained, no other mod required" |
| Preview.png / publishedFileId / modVersion tag | NONE (About folder holds About.xml only) | NONE | NONE |
| LICENSE file | none in folder | `FlowWorks/LICENSE` | `Pyrelands/LICENSE` |
| Deployed game copy | `Mods\GimmeSomeSlack` | `Mods\FlowWorks` | `Mods\RimMandrake.Biomes` (+ a `Mods\PyrelandsMechanics` folder, likely stale) |
| modcheck record (`modcheck_status.json`) | GREEN-shape: 110 PASS, 0 not_ok, record ACCEPTED at hash fa3a10f36596 (r5 note) | 61 PASS, record REFUSED only for "step 4 UNMEASURED: no extension_proof result supplied (--extensions)" | status RED, ts 1789295372 (stale, pre-pilot); r5/r6 notes say `modcheck floor --all` VALIDATED 21/21 bar met, but no passing recorded run |

- `design/MOD_CONSOLIDATION_PLAN.md` §5 defines per-engine release-readiness columns (`standalone_loads`, `generic_defaults_present`,
  `zero_cross_tier_refs`, `workshop_page_drafted`) but **no manifest carries them yet for these three** (grep found no data file). Workshop-name
  collision check for "FlowWorks" was "no collision, moderate confidence, NOT conclusive" (`design/RimMandrake/flowworks_mod_definition.md:998-1010`).
- The only written definition of the SHIPPED rung is the northstar ladder: VALIDATED -> WIRED -> GREEN-minimal -> GREEN-full -> SHIPPED, where SHIPPED =
  deployed, Mod Settings "superb" (2026-09-12 ruling), art complete, code review CLEAN (`design/RimMandrake/northstar_trials/{FlowWorks,Pyrelands}_trial_plan.md`;
  items `FLOWWORKS_NORTHSTAR_SHIP_1`, `PYRELANDS_SHIP_READINESS_1`). GSS has no trial/ship item at all.
- The pilot's own finish line is `design/RimMandrake/ratchet_workflow_and_token_burst_design_2026-10-11.md` §H (six criteria at ONE HEAD on the 22/23-mod tier). Status at r6
  `902b565c93` (ledger note 2026-10-15T11:08Z + 11:16Z): C1 GSS 110/110 MET (3 maps) - C2 FlowWorks v2 61/61 + river 0 FAIL MET - C3 Pyrelands 34 PASS 0 FAIL MET (regrow INFERRED,
  furnace warmth tool gap labelled) - C4 machine half MET, owner gates remain (grass look, POND_ELEVATION deferred) - C5 review 93/93 CLEAN, 5 failing nightly selftests fixed, green full sweep owed from the 03:00 run -
  C6 owner review queue (`Transient/ratchet_owner_review_2026-10-12.md`) not yet answered.
- **Decision needed from the owner (not yet made anywhere): does "release/deploy" mean (a) deployed composed into the campaign mod list (what the ladder's SHIPPED means), or (b) a public Steam Workshop upload?** (b) needs, per mod: Preview.png, About description/title polish, a publish tool (none exists in repo), a Workshop-name check, a versioning scheme, a standalone-load proof on a clean list.
- Per-mod standalone-load proof: Pyrelands ships inside the biomes composite, so "Pyrelands alone" is not a deployable unit today unless the composite is the release unit.

## 1. GimmeSomeSlack (GSS)

### 1.1 Open ledger items in-mod
| ID | state | needs | what is left | size | blocker |
|---|---|---|---|---|---|
| FALLEN_WIRE_SHOCK_1 | validated | bridge | A5 FlowWorks-caldera half (chemfuel half PASS 10-11); H1 owner judges knockback/knock-out/ignition | S live + owner | live proof; owner look |
| GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 | validated | bridge | A3 joint live gravship flight, owner watching, span stays drawn | M | owner look (joint session) |
| CORD_GRAPH_TOPOLOGY_REVISION_1 | built | bridge | A2 live hash/draw-counter match on a busy map for the DrawMotion half | S | live proof |
| MESSYCONDUIT_CABLE_PILE_LOOK_1 | built | bridge | A2/A3 hose-fitting and crossing-joiner probes; A4 owner rules the pile look | M | live proof; owner look |
| MESSYCONDUIT_REVIEW_ROUND1_1 | built | bridge | A1 live bracket/pileArt/poleTex; A2 modcheck passing (likely already met by the accepted 110/110 record); A3 wall-bracket art eval; A4 owner re-review of round 2 | M | live proof; art; owner look |
| POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK | doing | bridge | A2+A3 PASSED live 2026-10-11, A4 answered by owner card; record the pass and close | S | bookkeeping |
| UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS | built | owner | A2 owner looks at a cord diving through a wall | S | owner look |
| TAPCLAMP_REDRAW_BITES_DOWN_AT_LAST | proposed | deploy | v3 clamp installed (737b796e6f) and seen live L2 PASS; close it | S | bookkeeping |
| SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST | built | bridge | A2/A3 live: GSS both tabs master-off greys dependents, Reset-all confirm; same item owes Pyrelands + FlowWorks windows | S | live proof (screenshots) |
| GIMMESOMESLACK_NORTHSTAR_VALIDATE_1 | proposed | offline | owner validates the seeded north star and views the sheet once; "conditionally accepted 2026-10-06", its blocking evidence (9 FAIL MX_H* rows) is stale vs 110/110 | S | owner decision |
| TESTSITE_SAVES_BUILD_ONE_CALM_MAP | proposed | bridge | one cleared calm saved map per suite (shared harness, makes reruns deterministic; not a ship gate) | M | build + live |
| RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP | doing | offline | the umbrella: C5 green sweep + C6 owner rows | S machine, owner rest | owner gate |

GSS has no `*_NORTHSTAR_TRIAL/SHIP` ladder items: nobody has filed the SHIPPED rung for it (code review is 93/93 CLEAN, settings exist on two tabs).

### 1.2 Withheld / provisional functionality (file:line)
- `src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialSettings.cs:66` `dripLoops = false` - design 2.5 insulator drip loops built 2026-10-10, OFF by default, owner walk W1b judges it (`design/RimMandrake/owner_walk_gss_flowworks_2026-10-11.md:47`). Withheld feature: decide ship ON/OFF/remove.
- `.../Source/GimmeSomeSlackMod.cs:84` `floorRipple = false` - floor ripple motion off by default (CORD_GRAPH_TOPOLOGY_REVISION_1 A2 is its live proof).
- `.../Source/GimmeSomeSlackMod.cs:72` `sparksOnlyOverlay = false`, `:63` `debugDraw = false` (debug, fine).
- `.../Source/Aerial/RM_FallenWireShock.cs:28,33`, `AerialSettings.cs:58`, `Defs/Aerial/RM_FallenWireShock.xml:9` shock numbers (knockback cells, fuel-ignition chance) PROVISIONAL until H1 owner judgement.
- `.../Source/Aerial/AerialMaterials.cs:37` ribbon width per look PROVISIONAL; `.../Source/Core/CordBuilder.cs:808` PowerStrip socket layout PROVISIONAL "read off the PNG"; `.../Source/Aerial/RM_MapComponent_Aerial.cs:128` tap clamp size PROVISIONAL; `.../Source/Aerial/AerialMath.cs:486` fallen-wire gap PROVISIONAL.
- `.../Defs/Aerial/RM_AerialStyles.xml:7` bracket per-facing draw offsets are placeholders overwritten by StylePicker at startup (likely benign, confirm).
- `design/validation_walks/RimMandrake/GimmeSomeSlack.md:32-33` bars E2 (mod-mod compat with other conduit/wire render mods) and E3 (About.xml declares incompatibilities) are UNBUILT: no check exists. Release-relevant for a public Workshop upload.
- `CORD_GRAPH_TOPOLOGY_REVISION_1`: the topology-revision half is deliberately NOT built (ledger note 2026-10-11).
- Art: Wall-bracket art per look evaluated only at L3 (MESSYCONDUIT_REVIEW_ROUND1_1 A3). No Preview.png.

### 1.3 Release mechanics for GSS
See section 0. Missing: Preview.png, version tag, Workshop page, license file, E2/E3 compat bars, ship item. Machine gate state: proof_all 110/110 x3 maps at ONE HEAD, modcheck record ACCEPTED.

## 2. FlowWorks (FW)

### 2.1 Open ledger items in-mod
| ID | state | needs | what is left | size | blocker |
|---|---|---|---|---|---|
| FLOWWORKS_NORTHSTAR_SHIP_1 | proposed | offline | SHIPPED rung: 195/195 .cs CLEAN; owner-parked gaps (ladder art, doors, pit collapse bars) closed by his word | S + owner | owner decision |
| FLOWWORKS_NORTHSTAR_TRIAL_1 | built | bridge | parent: A1 GREEN-MIN record, A2 GREEN-FULL, A3 ship gaps closed/parked | M | live proof; owner |
| FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1 | proposed | bridge | v2 61/61 GREEN done at 902b565c93; record with `--extensions` step-4 result so modcheck stops REFUSING | S | live proof (record) |
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1 | built | bridge | cold load on the full 550-640 mod list (~25 min) then modcheck GREEN; list restore | L | live proof (long) |
| FLOWWORKS_CHECKOUT_SCOPE_1 | built | bridge | one full extension_proof (54 chains, only 5 ever ran) right after a v2 GREEN, recorded | M | live proof |
| FLOWWORKS_BUILD_PROGRAM_1 | validated | bridge | A4 wall/pit art evaluated (L3), A5 owner accepts the FlowWorks result in game | M | art; owner look |
| FLOWWORKS_VISUAL_PRINCIPLES_1 | validated | bridge | A2 rows for face material/liquid surface/pit shading; A3 Opus visual eval; A4 owner look | M | live proof; owner look |
| EXCAVATION_WALL_ART_1 | validated | bridge | A1 L1, A3/A4 frames D1..D4 and spikes legible; A5 owner keeps wall faces/spikes/ladder | M | live proof; art; owner look |
| FLOWWORKS_LADDER_RAISE_LOWER_1 | validated | owner | A2 owner confirms raised/lowered ladder art (RAISED VARIANT ART OWED) | S build-art + owner | art; owner look |
| PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS | validated | owner | H1 owner approves ramp art via art ledger (placeholder art now); build-menu placement verdicts not staged | S-M | art; owner look |
| PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP | doing | offline | offline core built (ae8d38f27c, selftest 306/306), NOT deployed; `climb_proof.py` live owed (ramp rows PASS 10-15) | M | live proof |
| PIT_SUPERDEEP_COLLAPSE_1 | doing | bridge | no unbuilt child left; verify bars 1-3 hold; remaining = children's live rows + owner | S | live proof / bookkeeping |
| PIT_TEMPERATURE_SOFTENING_1 | validated | bridge | A2-A4 live (roofed/unroofed twin, resistance, Exposed Prisoner thought), A5 GREEN-MIN, A6 owner mood strength | M | live proof; owner decision |
| PIT_LIP_OCCLUDES_OUTSIDE_1 | built | bridge | A1 live: depth-4 pawn stays in opening, lip cover spans sprite | S | live proof |
| LIQUID_LEDGER_BUILD_NO_UNIT_LOST | validated | bridge | A3-A7 NS rows (dump tank drain, intake needs pump, ship tank fill, hose off spill, hose theft goodwill) have no live result; A9 owner judges spill art + "Fitting:" relabel | M | live proof; owner look |
| HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD | validated | bridge | A2 pipe look menu survives blueprint->frame->building; A5 rides LEDGER A2-A8; A4 owner judges four pipe atlases | S live + owner | live proof; owner look |
| LIQUID_BOTTLE_LOOP_1 | built (BLOCKED) | bridge | fill job never yields a filled bottle live (4 tries); revert/rot unbuilt (blood deferred); A1-A3 live | M-L | build; live proof |
| FLOWWORKS_CONTAINER_MATERIALS_1 | validated | bridge | A2 material survives fill/wash/pour, acid refusal live (~10 min chain); A3 owner judges stuff-tinted art | S + owner | live proof; art; owner look |
| LIQUID_THIRST_CHAIN_1 | built (BLOCKED) | bridge | blocked on the bottle loop; needs DBH Lite+Thirst tier for A1-A3; DBH not in live list so patch inert | M | build (dep); live proof |
| TANK_TALL_BUILD_TWICE_THE_DRINK | doing | offline | tall tanks, all four tanks x four GSS looks via PipeLook picker; short tanks regen; def comment says tall ART is placeholder (stacked drums) | L | art; build |
| GLOW_TANK_LIQUID_FEED_1 | validated | bridge | A2 salt-water tank drawn down 1 unit at a time + setting off; H1 owner judges drink rate | S + owner | live proof; owner decision |
| MISSION_TANK_GOAL_REWIRE_TO_DEST | built | bridge | A2 live mission report reads dest tank units by ThingID | S | live proof |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1 | built | bridge | A1 looks on/off x3 with tar+propane | S | live proof |
| LIQUID_FIRE_QUEUE_ORIGIN_1 | built | bridge | A1-A3 asserts (reach cap, torch lights pending cell, save reload with pending front) have no row | M | build (rows) + live |
| FLOW_ORDER_EXTERNAL_INPUT_1 | built | bridge | A3 load with maxNetworkCells slider; A4 >6000-cell network wets end to end, pulse cost timed | M | live proof |
| FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO | validated | bridge | A2 live: write into dry cut never re-stamps an unkeyable liquid | S | live proof |
| HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE | validated | bridge | A2 live: late-listed hot cell warms room past budget | S | live proof |
| NATURAL_HEAT_CACHE_PROVE_STALE_DAYS | validated | bridge | A2 live: draining roofed hot pool stops warming within 250 ticks | S | live proof |
| STATION_REACH_CENTRE_RETHINK_FOOTPRINT | validated | bridge | A2 live: pump station draws 4 cells off long side not 5 | S | live proof |
| TAR_COOLING_GLASS_MEND_ENGINE_CELLS | validated | bridge | A2 live: tar release leaves base depth terrain intact | S | live proof |
| EXCAVATION_LEGACY_MIGRATION_FLAG_1 | built | bridge | A1/A2 live: filled channels reload not as excavations; fallback terrain PROVISIONAL | S | live proof |
| EXCAVATION_LOAD_SANITY_REPAIR_1 | built | bridge | A1 L1 load with canals logs no repair warning | S | live proof |
| HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1 | built | bridge | A1 live check on a tar plot (~3 min) | S | live proof |
| LAVA_LIQUID_BUILD_PROMISED_BY_CARD | validated | bridge | A4 on a Forge map no wrecked pumping station spawns with lava as only liquid (startup read clean) | S | live proof |
| RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED | built | bridge | A1-A6 live toggle chains (11 toggles, flood, sweep bruise, pathing, weir catch, stake-line); A7 owner | M | live proof; owner look |
| SURFACE_RIVER_WEIRS_1 | validated | bridge | A3 RiverWorks walk GREEN-MIN (ext river 20 PASS 0 FAIL r6; record it) | S | live proof (record) |
| TAKEN_BY_LAND_SERVICE_1 | validated | bridge | A3 letter + drag mark live for swept pawn and gale carry | S | live proof |
| FLOWWORKS_QUARRY_DIGGING_1 | validated | bridge | A3 drain/refill leaves stock at cap; A4 panning job; A5 first-find letter (rock chunk sends none by design) | M | live proof |
| RIVER_STEAM_ANIMATION_1 | built (BLOCKED) | bridge | no steam-state predicate in extensions.py (`toggle_river_steam` UNMEASURED); needs Pyrelands river map + screenshot; A3 owner | M | build (predicate); owner look |
| SETTINGS_SCREEN_KIT_1 | built | bridge | A5 live screenshot of FW settings screen | S | live proof |
| FLOWWORKS_SETTINGS_WIRE_AFTER_TANKS | built | bridge | A2 live: FW master-off shades dependents, Reset-all asks | S | live proof |
| WORLDMAP_LIQUID_TAGS_1 | built | bridge | A1 landing quicktest of Ash'karr save, 4 tagged biomes repaint shores (~15 min); authoring waits on one-time world paint | M | live proof (partly gated by world paint) |
| FLOWWORKS_REVIEW_LOOKS_ROUND_1 | proposed | offline | owner approved scorch round 4; remaining: depth-only water labels, more fluids online | M | build; owner look |
| FLOWWORKS_PLAYTEST_CAMPAIGN_1 | proposed | offline | method-per-bug-class campaign; not a ship gate | L | owner decision (priority) |
| POND_ELEVATION_BUILD_LAKES_RUN_DEEP | proposed | offline | deep (>4) lakes, head-based kernel, lift 4000-cell cap; OWNER CARD: build next week after account reset | L | owner decision (timing) |
| TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS | doing | bridge | 861b31c03e longest-crossing fix NOT deployed/run; one wide-river run | S | live proof |
| TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ | proposed | offline | loadedMaps read-back PASS run 1 of 2; one more river run then close | S | live proof |
| TESTENV_HIVES_/FLOODS_/MEGAPEDE_/TRIALSITE_ (4 items) | built | bridge | harness hardening, A1 L1 each owes a live receipt | S each | live proof |
| TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES, TESTENV_QUICKTEST_DIAGNOSE_SPIKES_UNINVITED | proposed | bridge | not reproduced r4/r5; close or leave | S | live proof |
| RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID | proposed | offline | modcheck detector fires on 'Seasonal flooding' letter | S | build |
| DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS | proposed | offline | ProofResetRect does not reset rolledDepth (proof-only) | S | build |
| DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL | proposed | offline | owner-filed: digging machine, digger droid (depth >4); a post-1.0 extension, not a ship gate | L | owner decision |
| SWALE_CANAL_ART_REFERENCE_1, VEXXITH_USES_1 | doing/proposed | offline | cross-mod (Cracked Lands Swale art; acid-proof material); not FW ship gates | M | art; owner |

### 2.2 Withheld / provisional functionality (file:line)
- `src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs:64-65` `liquidCorrosionEnabled = false`, `liquidIgnitionEnabled = false` - **both default OFF**; `About/About.xml:53-54` says burning liquids are "built but not yet proven in a live game" (the live fire rows plot_E_fire/fire_explosion PASS 3/3 on 10-13, but About text is now stale either way). Decide: ship ON, or ship OFF and say so.
- `.../RimMandrakeFlowWorksMod.cs:222` `pitSinkClampEnabled = false` (owner "try without" 2026-10-07); `:163` `superdeepCapturesOwnFaction = false`.
- `.../Source/Machinery/RM_MachinerySettings.cs:41` `industrialWorksBuildAnywhere = false` (campaign law: industrial works FOUND not built; wave switch).
- `.../Defs/Machinery/RM_LiquidLogistics.xml:169` TANK_TALL art is a placeholder (stacked drums) until real tall art lands.
- `.../Defs/Rivers/RM_BankWorks.xml:9` bank stake and ferry post are "earlier placeholders" art; `Defs/Rivers/RM_PlacerWorks.xml:6` ALL placer numbers PROVISIONAL.
- `.../Defs/LiquidTypes/ThingDefs/RM_Filth_Tar.xml:68` tar filth = three simple placeholder blob sprites; `Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml:97` deep-sand pool texture OWED; `Defs/ManyWaters/TerrainDefs/RM_ColoredWater.xml:58` explicitly deferred.
- `.../Defs/LiquidTypes/ThingDefs/RM_LiquidBottles_Base.xml:32` + `RM_LiquidBottles.xml:34` blood bottle row NOT built (blood deferred); `Source/LiquidTypes/RM_LiquidBottleUtility.cs:21-26` "minifiable, any liquid, pump/hose interop is still unbuilt".
- `.../Source/Designator_FillInCanal.cs:92` a fill-in job text says "is not built yet" (player-visible string, check which path).
- `.../Source/Swale/RM_Swale.cs:31` survey/cistern loop NOT built (belongs to Cracked Lands mod); `Source/Quarry/RM_PlacerWorks.cs:18` placer swap point, "its C# mod is unbuilt".
- `.../Source/Machinery/Kits/RM_HotLiquid.cs:16`, `.../Defs/LiquidTypes/ThingDefs/RM_LiquidPump.xml:8`, `Source/RM_WallFaceMath.cs:18` numbers PROVISIONAL; `Source/Pits/Trigger/PitCoverTier.cs:9` spec's placeholder ratings; `Source/LiquidTypes/LiquidCorrosion.cs:91` TODO proxy.
- `Source/Pits/RM_PitTrapMath.cs:470-471` terrain base cost "wired ... by the connectivity-mask item, not yet" (PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP offline core, undeployed).
- Walk bars E1 (removal), E2 (mod-mod compat with `sarg.alphabiomes`, DBH Lite), E3 (declared incompatibilities; old GSS hose-reel defs) UNBUILT (`design/validation_walks/RimMandrake/FlowWorks.md:49-51`).
- `design/RimMandrake/flowworks_remaining_2026-10-05.md`: row 11 ladder art A/B unpicked (OWNER, placeholder stays); row 13 sluice box + panning DEP on MINERALS_WHERE_THEY_BELONG_1 (0 of 37 rows owner-approved); row 14 DBH patch inert (DBH not in live list); row 19 Workshop name check OUT (web).
- Ratchet note: `canal_fill_front` fix and `flood_refill` is UNMEASURED by design ("no predicate") on every river run.

### 2.3 Release mechanics for FW
Machine state at 902b565c93: v2 GREEN 61/61 (x2 consecutive), river extension 20 PASS 0 FAIL 1 UNMEASURED (flood_refill, owed no predicate), works chain 11/11; code review .cs 195/195 CLEAN; modcheck record REFUSED only for missing extension result (fixable by a recorded run with `--extensions`). Missing: GREEN-FULL on full list, owner looks (wall art, ladder art, pipe atlases, tank art), About text refresh, Preview.png, Workshop name check.

## 3. Pyrelands

### 3.1 Open ledger items in-mod
| ID | state | needs | what is left | size | blocker |
|---|---|---|---|---|---|
| PYRELANDS_NORTHSTAR_TRIAL_1 | proposed | bridge | parent; re-measure note 2026-10-03 superseded by r3-r6 runs; close when children close | S | bookkeeping |
| PYRELANDS_GREEN_MINIMAL_1 | built | bridge | 34 PASS / 0 FAIL r6 (36 rows); owes the 30 C CONTROL site run, `rimflow verify` record, and a passing `modcheck record` (status still RED/stale) | M | live proof |
| PYRELANDS_GREEN_FULL_1 | built | bridge | fresh full-list mapgen scratch save, census bars 1/2/4, `rimflow verify --config full-latest`; no short check (cold load ~25 min) | L | live proof (long) |
| PYRELANDS_SHIP_READINESS_1 | doing | offline | art installed 10-15 (all 9 rulings), code review CLEAN, settings gate census, composed deploy 0 diff done; remaining: a deploy of the 10-15 art/defs + live gate proof (waits on unification wave 2); FireHawk line is stale (FIREHAWK_FLIGHT_BEHAVIOR_1 is done) | S-M | live proof (gate) |
| PYRELANDS_GRASS_SATURATION_1 | ready (BLOCKED) | owner | machine half DONE live r5 (0 Bush/Pincushion of 58052 things); owner looks at the two-species ground | S | owner look |
| STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY | proposed | deploy | `jawa/static_call` cannot take Thing/Pawn args by ThingID -> `furnacebeast_warmth` bar is a labelled gap; needs companion DLL build + deploy with game down | M | build; deploy window |
| ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE | proposed | offline | owner card: assume dome stance when heat-attacked + dome pose art | M | build; art |
| RIVER_STEAM_ANIMATION_1 | built (BLOCKED) | bridge | (see FW) needs predicate + Pyrelands river screenshot + owner judge | M | build; owner look |
| BIOME_ARRIVAL_LETTERS_ALL_1 | validated | bridge | A2 landing letter once (Fever Wood first; Pyrelands text is one of ten placeholders); H1 owner edits ten texts | S | owner decision |
| SOLAR_HEAT_EXPOSURE_1 | built (BLOCKED) | bridge | planet-wide sun heat incl. Pyrelands heat kind; needs Long Shade quicktest + owner-watched sitting | M | live proof; owner look |
| SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST | built | bridge | (see GSS) Pyrelands settings window live check | S | live proof |
| TESTENV_BURROW_HEAT_/COLD_ (2 items) | proposed | bridge | burrow probe now reloads fixture per trial (26 cold trials); diag chain still a scratch copy outside repo | S | build (commit chain) |
| OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN | proposed | deploy | health-profile companion redeploy; not a ship gate | S | deploy |

All PYRE_* / ANIMA_* / ash-build / regrow items are DONE. Owner-answer rows from `Transient/ratchet_owner_review_2026-10-12.md` are listed in section 4.

### 3.2 Withheld / provisional functionality (file:line)
- `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:145-146` `crossBiomeEnabled = false`, `crossBiomeEverywhere = false` - cross-biome ash mechanic is opt-in OFF by design; `:133` `ambientAshHeavy = false`.
- `.../Source/RM_PyrelandsMod.cs:120` all 13 ash-redesign numbers PROVISIONAL (owner queue row 1 asks him to name any that feel wrong); `Defs/ThingDefs_Races/RM_Ashwallow.xml:57-60` Ashwallow resistance numbers PROVISIONAL "tune after a live fire test".
- `.../Defs/ThingDefs_Races/RM_Emberscythe.xml:44-45,56` fire-hardening comp "nicer v2 - OWED"; per-creature spawn toggle in RM_PyrelandsSettings "OWED, not built". Same pattern: `RM_PyrelandsFauna.xml:44` (flip-book flight owed), `RM_PyrelandsPortedFauna.xml:54` (flamefang/sytheclaw/barbslinger donor abilities dropped, all OWED).
- `.../Defs/LightningBreaker/RM_LightningBreaker.xml:7` and `Source/RM_LightningBreaker.cs:46-47` breaker `_Off` frame owed art (art pass 10-15 says breaker core + tripped frame installed; verify the XML comment and fallback code are now stale).
- `.../Defs/WorldObjectDefs/WorldObjects_Pyrelands.xml:14` world-object icon borrows vanilla Caravan texture.
- `.../Defs/ThingDefs_Items/RM_FurnaceHide.xml:9` placeholder item on RM_FurnaceBeast.
- `.../Source/FireEcologyHook.cs:53` `MinFireSizeForAshDusting = 1` "reserved for a future fire-size check".
- `.../Defs/BiomeDefs/Pyrelands.xml:295` a quicktest "not yet done"; `:84` owed worldgen-tile-count quicktest (0 tiles on Ash'karr is EXPECTED, painted once at the end - not a gap).
- North-star gaps (labelled, not hidden): `embergrass_regrows` INFERRED (compressed 0.1 day: 256 -> 0 -> 34 -> 71), `furnacebeast_warmth` tool gap, `fulgurite_after_lightning` needs a site with sand.
- `design/validation_walks/RimStarWars/FireEcology.md`: two ash-ladder goal lines describe the RETIRED ladder (owner queue row 2).
- Composition: Pyrelands ships standalone-capable per its About but is released inside `mandrake.rm.biomes` (per-biome toggle must gate mechanics: census done file-level, live gate proof waits on unification wave 2).

### 3.3 Release mechanics for Pyrelands
Machine state: north star 34 PASS / 0 FAIL / 36 (r6, fresh site, 8 short pieces, ~25 min wall), `modcheck floor --all` VALIDATED 21/21; selftests green except the nightly full sweep owed at 03:00; code review 93/93 CLEAN. Missing: recorded passing modcheck run (status file still RED from 1789295372), 30 C control, GREEN-FULL on full list, owner looks, Preview.png/Workshop page for the composite.

## 4. Owner gates (only he can clear)

Decisions
1. **What "release" means** (composite deploy vs public Workshop upload) - nothing records this; blocks Preview/About/version/publish-tool work (section 0).
2. POND_ELEVATION_BUILD_LAKES_RUN_DEEP: his card says "build next week after account reset". Not a ship blocker unless he pulls it forward (L).
3. Pilot verdict C6: accept §H once rows below are answered (`RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP`).
4. Ship ON/OFF/remove for withheld toggles: GSS `dripLoops`, `floorRipple`; FW `liquidIgnitionEnabled`/`liquidCorrosionEnabled`, `pitSinkClampEnabled`; Pyrelands `crossBiomeEnabled`.
5. Regrow thresholds (owner queue row 3: 26.2%/59.8% measured vs 25%/60% targets; the 50% survivor cut-off is an agent guess).
6. GIMMESOMESLACK_NORTHSTAR_VALIDATE_1 (validate the seeded GSS north star; conditionally accepted 10-06).
7. FireEcology walk replacement text approval (queue row 2); BIOME_ARRIVAL_LETTERS_ALL_1 ten texts (H1).
8. PIT_TEMPERATURE_SOFTENING_1 A6 mood strength; GLOW_TANK_LIQUID_FEED_1 H1 drink rate; FALLEN_WIRE_SHOCK_1 H1 shock numbers.
9. FLOWWORKS_NORTHSTAR_SHIP_1 A3: close or park each shipped gap by his word (ladder art A/B pick, doors, pit collapse bars).

Looks (each needs complete native paths and a staged save; he does not run live game state)
- GSS: UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS A2; MESSYCONDUIT_CABLE_PILE_LOOK_1 A4; MESSYCONDUIT_REVIEW_ROUND1_1 A4 + A3 bracket art; GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 A3 joint flight (he must be present); drip loops W1b.
- FlowWorks: FLOWWORKS_BUILD_PROGRAM_1 A5; FLOWWORKS_VISUAL_PRINCIPLES_1 A4; EXCAVATION_WALL_ART_1 A5; FLOWWORKS_LADDER_RAISE_LOWER_1 A2 (raised art); PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS H1 ramp art; HOSE_RULINGS A4 pipe atlases; LIQUID_LEDGER A9 spill art; FLOWWORKS_CONTAINER_MATERIALS_1 A3 tinted art; RIVER_TOGGLE_PROOFS A7; RIVER_STEAM_ANIMATION_1 A3; canal wet-front look (queue row 5); tall tank art.
- Pyrelands: ash ground look (queue row 1, deep ash/fertile/black rain/drift); PYRELANDS_GRASS_SATURATION_1 ground fill; creature art of 10-11 + 10-15 dessicated corpses (queue row 4); SOLAR_HEAT rest-dash (A3).
- Walk W8 joint flights (`gss_gravship`, `fw_flyer_river`) owner present ONLY.

## 5. Summary (10 lines)
1. GSS: 12 open in-mod items (S 7, M 4, L 0); build items ~0 (all built, proof/look owed); live proofs owed 6; owner gates 7; no ship item filed; E2/E3 compat bars unbuilt.
2. FlowWorks: ~50 open in-mod items (S ~27, M ~16, L 4: GREEN_FULL, TANK_TALL, POND_ELEVATION, PLAYTEST); real build items ~8 (bottle loop fill-job bug, LIQUID_FIRE rows, river-steam predicate, thirst chain dep, tall art, review looks, ferry deploy); live proofs owed ~32 (mostly S); owner gates ~12.
3. Pyrelands: 13 open in-mod items (S 6, M 5, L 1: GREEN_FULL); build items 2 (static_call tool, Ashwallow dome); live proofs owed 5; owner gates 6 (ash look, grass look, regrow thresholds, art, FireEcology walk, letters).
4. Machine green at ONE HEAD 902b565c93: GSS 110/110 x3, FW v2 61/61 + river 0 FAIL, Pyrelands 34/36 PASS 0 FAIL; the gap to ship is mostly records, owner looks and long runs, not mod bugs.
5. Risk 1: nobody has defined release (composite deploy vs Workshop); no Preview.png, version, publish tool or Workshop page exists for any mod, so "all the way to release" cannot be scoped until he rules.
6. Risk 2: the long/full-list runs (FW GREEN_FULL, Pyrelands GREEN_FULL, ~25 min cold load each, owner said "no more long runs" 10-13) and modcheck records (Pyrelands status RED stale, FW REFUSED for step 4) are the gates the ladder actually checks.
7. Risk 3: owner looks are about 25 items and need staged saves/joint sessions (gravship flight, art); with the account-budget tightness he sets the pace for every L4 criterion.
8. FW's shipped About text and default-OFF liquid ignition/corrosion toggles contradict the "no withheld functionality" goal unless ruled ON; GSS dripLoops/floorRipple likewise.
9. Cheapest wins today (S, no owner): record FW with --extensions, record Pyrelands modcheck, close POWER_THEFT/TAPCLAMP/NORTHSTAR_TRIAL/SHIP_READINESS, run the ~20 S live proofs as short chains on the 22-mod tier.
10. Needs a build: LIQUID_BOTTLE_LOOP fill job, river-steam predicate, `static_call` ThingID args, Ashwallow dome, LIQUID_FIRE rows, tall-tank art, TESTENV commits.
