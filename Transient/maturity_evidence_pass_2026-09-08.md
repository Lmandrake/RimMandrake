# Maturity registry evidence pass — 2026-09-08

Read-only evidence mining against the 78-system capability registry (seeded 2026-09-08 from
folder evidence only, every system capped at `implemented`). Sources: `infrastructure/state/items/*.md`
(401 files), `infrastructure/state/ledger/events.jsonl` (5767 lines), `infrastructure/state/modlists/*.xml`
+ `Transient/ModsConfig_*.xml` (61 snapshots), `Transient/Player_log_*.log` (14 captures, 2026-09-04..08).
Never proposes `played` or any content-rung change (owner-only). No writes made to the registry.

**Modlist method** (used for the "ACTIVE-51 + clean log" rows below): `mandrake.*` packageIds active in
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (605 `<li>` entries, matches `[JawaBench] context:
modSet 599/dab482d5` etc.) cross-checked against three independent full-list Player.log sessions this week —
`Transient/Player_log_before_droidworks_coexist_2026-09-08.log`, `Transient/Player_log_v4_session_2026-09-07.log`,
`Transient/Player_log_worldmap_v2_session_2026-09-07.log` — each reaching `[RimBridge] Bridge token:` +
`[JawaBench] context:` + real world/map generation, each with only 15-17 total `Config error in` lines,
none of them fatal to any of our packages except `mandrake.rut.shell` (see caveat below). Per this item's rule,
a package **absent from every captured snapshot cannot be promoted this way**, whatever an item file claims —
several `implemented`-rung systems (Oracle, RaidRedesigner, RustChrome, SWBestiary, etc.) are explicitly
"deployed, not enabled" per their own items and are excluded here for exactly that reason.

## Table

| System | Current rung | Proposed rung | Mark | Evidence ref |
|---|---|---|---|---|
| Antiquities | implemented | validated | CONFIRMED | `ANTIQUITIES_TREE_BUILD_1` — "pawn hauled the urn... Find.ResearchManager.GetProgress(RUT_Antiq_Language) read back exactly 125.0... via jawa/research_progress — an independent channel" |
| Armoury | implemented | validated | CONFIRMED | `LIGHTSABER_RECIPE_GATE_1` — "fresh full-589-mod restart... jawa/get_defs on RecipeDef/Force_CraftLightsaberSingle reads recipeUsers: null... confirmed on the resolved live game" |
| BirthHatchDemo | designed | validated | CONFIRMED | `LIVE_BIRTH_AND_HATCH_DEMO_1` — "RUT_DemoEggJawa52081 spawned at (110,110). jawa/inspect_string tracked it honestly" (jump past `implemented` — texture/def mod, folder scan under-counted; see note) |
| Droidworks | implemented | validated | CONFIRMED | `DROIDWORKS_POWEREDDOWN_NOT_WIRED_1` — "Stepped 250 ticks... RSW_DW_PoweredDown appeared... confirmed live (2251 ticks, no change)"; `DROIDWORKS_FULL_LIST_COEXIST_1` — "Load landed clean... 600 mods held" |
| FireEcology (RSW) | implemented | validated | CONFIRMED | `FIRE_ECOLOGY_LOOP_1` — "ash-ladder chain climbed all the way to RSW_FE_Ash_Heavy AND RSW_FE_Ash_Deep... fired correctly through repeated re-burns" |
| FluidCanals | implemented | validated | CONFIRMED | `FLUID_CANAL_FLOOD_TUNING_GAPS_1` — "RESULT 2026-09-04 — all three readings PASS, live" (recoverable / rate / boxed-in expiry, each with tick numbers); also active in `ModsConfig.MINIMAL.xml` |
| Graffiti | implemented | validated | CONFIRMED | `GRAFFITI_FRAMEWORK_BUILD_1` — "Live-forced the vandal spree... 10 RM_Graffiti_Vandal marks appeared across the map within ~9000 ticks" |
| Inhabited | implemented | validated | CONFIRMED | `INHABITED_SETTLEMENT_MAPPARENT_GAP_1` — "jawa/world_tile_map_generate {tile: 20000...} -> success: true... pawnCount: 14, thingCount: 16955" |
| JawaIonWeapons | implemented | validated | CONFIRMED | `VEHICLE_ION_TIER_1` — "RE-VERIFY 2026-08-30 — 9/9 at the predicted ticks. CLOSED" |
| Livestock | implemented | validated | CONFIRMED | ledger note under `FORSAKEN_CRAGS_PREDATORS_BUILD_1` (2026-09-07) — "Live-verified on a minimal-list restart... both PawnKindDefs spawn via debug action... jawa/pawn_get + inspect_string succeeded on all 6 spawned pawns" |
| LoadTracer | implemented | validated | CONFIRMED | `COLD_LOAD_STALL_INTERMITTENT_1` — "showed all 1531 static ctors completing, atlases baked, bridge up"; corroborated directly — `[LoadTracer] ctor N/1577` lines appear in every captured Player.log this week |
| Ninefold | implemented | validated | CONFIRMED | `NINEFOLD_RUNTIME_PROOF_BLOCKED_1` "PROVEN 2026-09-05" — before/after satiation table, all 5 gods; independently corroborated by this pass in **two** separate full-list Player.log sessions (`Transient/Player_log_stale_ninefold_session_2026-09-05.log`, 40 `[Ninefold]` lines, modSet 594; `Transient/Player_log_ninefold_crash_598mod_2026-09-07.log`, 47 lines, modSet 598) — research-completed and downed-in-battle triggers all firing correctly. **Caution, do not drop**: `NINEFOLD_DEBUG_GAME_READY_CRASH_1` records repeated OOM-pattern crashes (18-18.7GB RSS) on the full list correlating with bursts of Ninefold satiation lines under bulk dev-mode research; owner ruled likely unrelated host-memory issue, "proceed as though full list is OK" — but it is a real correlated crash, not just omitted evidence |
| Pits | implemented | validated | CONFIRMED | `RIMMANDRAKE_PITS_BUILD_1`, 2026-09-06 — "`T: Oiled: ignite`... fireStarted=True"; "PitCell gate toggle proven... flips covered False→True→False". Tested on the ephemeral `pits` modset_builder tier (not one of the archived ModsConfig snapshots), "0 config errors, 0 XML errors in Player.log". **Partial**: prisoner assign/place/feed gizmos remain unproven (root-caused to a missing bridge prerequisite, not to Pits itself) |
| PawnFlavor | implemented | validated | CONFIRMED | `PAWN_FLAVOR_SILENT_NONAPPLY_1` — "Confirmed via jawa/pawn_thoughts on multiple live colonists... Live cold load (592 mods)... positive, log-based proof the gate now genuinely opens" |
| ResearchRetag | implemented | validated | CONFIRMED | `RESEARCH_TREE_NORMALIZATION_1` close note (2026-09-04) — "final proof load, 595-mod full list... 185 techLevel mismatches cleared... 0 orphan fails" |
| RimDefDump | implemented | validated | CONFIRMED | `DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1` — "startup dump PROVEN (525 def files, 589 mods)"; `DOWN_WINDOW_ASSEMBLY_DEPLOY_1` — "jawa/map_info answers live... 243 jawa tools live" |
| SalvageClaim | implemented | validated | CONFIRMED | `SETTLEMENT_VERBS_WAVE_1` — right-click on quicktest map produced "Cannot pay salvage claim on packaged survival meal: not enough silver (need 9, have 0)" as a correctly-disabled FloatMenuOption |
| ShipMemory | implemented | validated | CONFIRMED | `ANOMALY_EXCEPTION_ACCESS_1` — "built, live-verified (minimal list, 21 mods) and closed at 4217267e — patch confirmed clean, reveal letter fires, architect designator flips visible on the 7 buildables"; also directly present in `Transient/Player_log_shipmemory_minimal_verify.log` (JawaBench ready, no ShipMemory-specific error) |
| StarWarsRaces | implemented | validated | CONFIRMED | `STARWARSRACES_UNDECLARED_GENE_DEPS_1` — two live restart bisections, each clearing named cross-reference failures (BigAndSmall/BetterPrerequisites types; 6 Eyes_*_Reptile refs) |
| StructureInjections (RM) | implemented | validated | CONFIRMED | `RIMPLACE_GENSTEP_LIVE_PROOF_1` — "Live, 2026-09-02... Full mod list (~400 active)... Run plan: dwelling_test.txt... calls GenStep_RimplacePlan.ApplyPlan directly" — every planned cell checked back live |
| WreckedMachines | implemented | validated | CONFIRMED | `WRECKED_MACHINES_RESURRECTION_1` — "build_batch god-spawned the Kludged tier... 'displaced':[{'destroyed':'RM_WM_AutomatedSmelter_Wrecked'}] — the wreck was actually wiped" |
| AshkarrInhabited | implemented | runnable | CONFIRMED | `DISTRICT_TEMPLATE_LIBRARY_1` — "fresh 589-mod cold load (mandrake.rut.inhabited newly enabled)... No new Config errors... jawa/world_objects_add ... SUCCEEDED" (placed geometry itself not confirmed — map-switch gap) |
| Cuisine | implemented | runnable | CONFIRMED | `RIVER_STEAM_ANIMATION_1` — "Restarted on a custom 13-mod minimal list (...mandrake.rsw.cuisine) — clean load, 0 config errors, 0 crossref errors, 0 patch failures, 0 typeload" |
| EmpirePursuit | implemented | runnable | CONFIRMED | `EMPIRE_PURSUIT_SURVEY_SHADOW_1` — "live check 2026-08-30 — PASSED... jawa/get_defs ScenPartDef/RuthlessPursuingMechanoids returns... the mod is deployed AND active". **Caveat**: item records the pre-rename packageId `mandrake.empirepursuit`; live packageId today is `mandrake.rut.empirepursuit` (three-tier rename) — same mod, folder unchanged, but worth BENCH's eyes before shipping the promotion |
| JawaIkee | implemented | runnable | UNCERTAIN | `NAMESPACE_PAIR_DEPLOY_1` — harvest_log.py showed zero "Could not find type named" lines for JawaIkee on a confirming load; no specific behavior observed |
| SeaBeasts | implemented | runnable | CONFIRMED | `SW_SEA_MONSTERS_ART_1` (events.jsonl) — "ALL 18 DEFS LIVE 2026-09-02, load 5... Zero cross-reference errors and zero texture failures... mandrake.rsw.seabeasts sits at position 322" |
| StarWarsPatches | implemented | runnable | CONFIRMED | `COLD_LOAD_RUN_SHEET_3` — "PASS - patch split (3 successors loaded, zero cross-ref errors, zero Jawa_* danglers)" |
| TheftHauler | implemented | runnable | CONFIRMED | `BUILDING_THEFT_HAULER_1` — "Enabled on the owner's real full list (592 mods)... 0 DEAD MODS, zero lines naming RimMandrake.TheftHauler... loads clean, no exception" (theft job itself not live-tested — MayRequire-gated on inactive Droidworks at the time) |
| UtinniPatches | implemented | runnable | CONFIRMED | `COLD_LOAD_RUN_SHEET_3` — same patch-split PASS, covering `mandrake.rut.patches` |
| Property | implemented | runnable | UNCERTAIN | `PROPERTY_FABRIC_BUILD_1` — "0 DEAD MODS... assembly loads clean, no exception... downstream code observed successfully calling into it live — strong indirect evidence, though not a direct positive confirmation" |
| PyrelandsFireEcology | implemented | runnable | UNCERTAIN | `FIRE_ECOLOGY_LOOP_1` — cold-loaded on the full 589-mod list, standing baselines held; explicitly "validated offline, not yet live-tested on Pyrelands specifically" (the live-proven ash-ladder belongs to the sibling RSW FireEcology mod) |
| SacredGraffiti | implemented | runnable | UNCERTAIN | `GRAFFITI_FRAMEWORK_BUILD_1` — 5-mod tier incl. mandrake.rm.sacredgraffiti cold-loaded clean (0 config/crossref errors); its own placement mechanism is unexercised (spawnable only via dev-mode inspection, no ritual trigger yet) |
| VaultDungeons | implemented | runnable | UNCERTAIN | Direct log finds (this pass): `Transient/Player_log_before_worldmap_session_2026-09-07.log` + `Transient/Player_log_pre_droidworks_recipe_fix_2026-09-07.log`, both on the current `ModsConfig.MINIMAL.xml` set — "Config error in RUT_GiveQuest_VaultThaw_V1_RustCathedral: quest is run from both incident and random quest" (x6 quest defs): a warning, but it shows the engine loaded and recognized VaultDungeons' quest defs as incident/random-pool members. No actual quest firing observed. |
| BlastDoorFrameAsyncFix | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no BlastDoorFrameAsyncFix-specific Config error. Texture-only fix mod (no defs/patches per folder survey) — "designed" likely under-counts what a pure texPath-override mod needs to function; flagged, not asserted |
| FactionSlate | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no FactionSlate-specific error |
| AshkarrLandmarkArt | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no AshkarrLandmarkArt-specific error |
| BeastNorm | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no BeastNorm-specific error |
| DesertVehicleReskin | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week; also present (mod-ctor confirmed) in `Transient/Player_log_before_vehicle_fuel_filter_test_2026-09-07.log`, no specific fuel-filter behavior observed though |
| Doctrine | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no Doctrine-specific error |
| GravshipAstronautFix | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week (texture-fix mod, see BlastDoorFrameAsyncFix note) |
| IshkoDarkLandmarks | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week. Its own item explicitly said "not yet observed loading live" (2026-09-0x) — that claim has since gone stale; docs decay, this pass supersedes it with fresh log evidence |
| JawaRules | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no JawaRules-specific error |
| JawaVoice | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no JawaVoice-specific error |
| MSEDroidFix | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week (texture-fix mod, see BlastDoorFrameAsyncFix note) |
| MandrakePatches | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no MandrakePatches-specific error |
| PlanetPresetPrime | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no PlanetPresetPrime-specific error |
| PlantGrowth | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no PlantGrowth-specific error |
| ResearchKitEastFix | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week (texture-fix mod, see BlastDoorFrameAsyncFix note) |
| Rites | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no Rites-specific error (research rows present, no gating mechanism live per its own item) |
| SauridFrillFix | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week (texture-fix mod, see BlastDoorFrameAsyncFix note) |
| SeasWaterline | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no SeasWaterline-specific error |
| StrandedQuest | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no StrandedQuest-specific error |
| StructureInjectionsSW | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no StructureInjectionsSW-specific error |
| ToolBeltFix | designed | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week (texture-fix mod, see BlastDoorFrameAsyncFix note) |
| Visibility | implemented | runnable | UNCERTAIN | ACTIVE-51 + 3 clean full-list sessions this week, no Visibility-specific error |

## No promotable evidence (grouped, one line each)

- **Aftermath, AftermathRites** — `PLOT_MECHANISM_MODS_WAVE_1` explicit: "shipped, offline-verified... not deployed/enabled." Not active in any captured snapshot.
- **AshkarrFlora, AshkarrWeatherSuite, BeastLairs, DesertFixtures, LongHunger, MenuShell** — design/code-review/offline-only items; not active in any captured snapshot; batch searches found nothing live.
- **CereanManeFix, KotORBandolierNorthFix, PhytokinBarkHeadFix** — texture-fix mods **deliberately DISABLED** per `EMPIRE_PURSUIT_SCENPART_INSTALL_1` ("stay DISABLED in ModsConfig") / `PHYTOKIN_BARK_EAST_LOOK_1` ("should be RETIRED UNBUILT"). Not active anywhere — correctly excluded.
- **HelixTellurox** — ⚠️ **negative evidence**: `HELIX_TELLUROX_SHELL_LOAD_CRASH_1` — adding it to a working minimal list caused a fallback to Core-only (6 mods) via a MissingMethodException. Do not promote; flag for FOUNDRY attention.
- **LanternDeeps** — ⚠️ **negative evidence**: `LANTERN_DEEPS_INJECTION_1` — "Quicktest attempt 2026-09-07 crashed the game" (missing hard dependency `BiomesTeam.BiomesCore` → NullReferenceException → RimWorld's own mod-list-wipe recovery fired). Do not promote.
- **Oracle, RaidRedesigner, RustChrome, SWBestiary, RestrainingBolts, RiverSteam** — each has an item explicitly stating "deployed, not enabled" / "live verify owed" and each is confirmed absent from every captured ModsConfig snapshot this pass checked. RaidRedesigner is additionally blocked on Oracle being inactive.
- **StructureInjectionsRUT** — absent from every captured snapshot; no item/ledger evidence found (unlike its RM/SW siblings, both of which promoted above).
- **Spikes** — no packageId, no About.xml, never deployed as a mod (dev-tooling C# spikes only). Not promotable by this method; no item evidence either.
- **UtinniShell** — ⚠️ active in the current 51-package set, but carries its own live-observed defect: `Config error in Utinni Shellmandrake.rut.shell: defName Utinni Shellmandrake.rut.shell should only contain letters, numbers, underscores, or dashes.` (seen in all 3 full-list sessions this week). The mod's `<name>` + packageId are getting concatenated into a malformed defName somewhere. Not promoted — this is a defect worth a ticket, not evidence of maturity.
- **WeatherSuite (RSW)** — absent from every captured snapshot; no item/ledger live evidence found.

## Ready-to-run promotion commands (CONFIRMED rows only)

```
python3 src/RimMandrake/rimflow/cli.py capability set Antiquities --function-rung validated --evidence-ref "ANTIQUITIES_TREE_BUILD_1" --date 2026-09-04 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Armoury --function-rung validated --evidence-ref "LIGHTSABER_RECIPE_GATE_1" --date 2026-09-03 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set BirthHatchDemo --function-rung validated --evidence-ref "LIVE_BIRTH_AND_HATCH_DEMO_1" --date 2026-09-02 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Droidworks --function-rung validated --evidence-ref "DROIDWORKS_POWEREDDOWN_NOT_WIRED_1 / DROIDWORKS_FULL_LIST_COEXIST_1" --date 2026-09-08 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set FireEcology --function-rung validated --evidence-ref "FIRE_ECOLOGY_LOOP_1" --date 2026-09-01 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set FluidCanals --function-rung validated --evidence-ref "FLUID_CANAL_FLOOD_TUNING_GAPS_1" --date 2026-09-04 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Graffiti --function-rung validated --evidence-ref "GRAFFITI_FRAMEWORK_BUILD_1" --date 2026-09-06 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Inhabited --function-rung validated --evidence-ref "INHABITED_SETTLEMENT_MAPPARENT_GAP_1" --date 2026-09-04 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set JawaIonWeapons --function-rung validated --evidence-ref "VEHICLE_ION_TIER_1" --date 2026-08-30 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Livestock --function-rung validated --evidence-ref "FORSAKEN_CRAGS_PREDATORS_BUILD_1" --date 2026-09-07 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set LoadTracer --function-rung validated --evidence-ref "COLD_LOAD_STALL_INTERMITTENT_1" --date 2026-09-02 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Ninefold --function-rung validated --evidence-ref "NINEFOLD_RUNTIME_PROOF_BLOCKED_1" --date 2026-09-05 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Pits --function-rung validated --evidence-ref "RIMMANDRAKE_PITS_BUILD_1" --date 2026-09-06 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set PawnFlavor --function-rung validated --evidence-ref "PAWN_FLAVOR_SILENT_NONAPPLY_1" --date 2026-09-02 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set ResearchRetag --function-rung validated --evidence-ref "RESEARCH_TREE_NORMALIZATION_1" --date 2026-09-04 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set RimDefDump --function-rung validated --evidence-ref "DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1" --date 2026-09-03 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set SalvageClaim --function-rung validated --evidence-ref "SETTLEMENT_VERBS_WAVE_1" --date 2026-09-01 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set ShipMemory --function-rung validated --evidence-ref "ANOMALY_EXCEPTION_ACCESS_1" --date 2026-09-04 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set StarWarsRaces --function-rung validated --evidence-ref "STARWARSRACES_UNDECLARED_GENE_DEPS_1" --date 2026-09-03 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set StructureInjections --function-rung validated --evidence-ref "RIMPLACE_GENSTEP_LIVE_PROOF_1" --date 2026-09-02 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set WreckedMachines --function-rung validated --evidence-ref "WRECKED_MACHINES_RESURRECTION_1" --date 2026-09-01 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set AshkarrInhabited --function-rung runnable --evidence-ref "DISTRICT_TEMPLATE_LIBRARY_1" --date 2026-09-01 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set Cuisine --function-rung runnable --evidence-ref "RIVER_STEAM_ANIMATION_1" --date 2026-09-07 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set EmpirePursuit --function-rung runnable --evidence-ref "EMPIRE_PURSUIT_SURVEY_SHADOW_1 (pre-rename packageId, see caveat)" --date 2026-08-30 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set SeaBeasts --function-rung runnable --evidence-ref "SW_SEA_MONSTERS_ART_1" --date 2026-09-02 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set StarWarsPatches --function-rung runnable --evidence-ref "COLD_LOAD_RUN_SHEET_3" --date 2026-09-04 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set TheftHauler --function-rung runnable --evidence-ref "BUILDING_THEFT_HAULER_1" --date 2026-09-01 --seat BENCH
python3 src/RimMandrake/rimflow/cli.py capability set UtinniPatches --function-rung runnable --evidence-ref "COLD_LOAD_RUN_SHEET_3" --date 2026-09-04 --seat BENCH
```

Note: `JawaIkee` is marked UNCERTAIN (not CONFIRMED) so it is intentionally omitted from the command list above,
along with every UNCERTAIN row in the table — those are left for BENCH's judgment call, per this item's rigor rule.
