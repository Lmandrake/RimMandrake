# BENCH_REBOOT_HANDOFF_202609121357 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609111830`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The 2026-09-12 card sitting is the hinge of everything now in flight: ~60 owner
decisions landed in one session (census + CSV freeze, vapor rules, mutation
deck, cathedral A1-A5, ashfall 3/4, all biome-kit cards, tibanna T1+T2, gizka,
sarlacc all-forks, seven world renames). Every ruling is recorded VERBATIM in
its spec, not summarized — when a FOUNDRY build item cites a ruling, trust the
spec's Owner-rulings section over any queue-title paraphrase. The pattern that
made it work: prep agents build the evidence pack first, cards carry one
plain-language trade each, and the landing edits the spec in the same act as
the ruling (deciding-and-superseding).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **The art verdict sheet awaits him alone**: `D:\Luke\dev\Rimworld\Transient\art_verdict_sheet_2026-09-12.html`
  — 147 lanes, 95 with true original-vs-regen side-by-sides; his decisions JSON
  then lands via `apply_verdicts.py` (dry-run default). The regen pipeline's
  next wave is gated on this.
- **The worldmap STARE + verdict**: evidence pack complete at
  `Transient/worldreview/WORLDMAP_FINAL_REVIEW_report_2026-09-12.md` + 10
  planet shots in `Transient/worldreview/shots/`. Top findings for his eye:
  283/417 ancient vents violate his ruin-only rule; sarlacc landmarks read 6
  live / 7 dead vs expected 1/4 (relocate item must reconcile); canon
  settlements landed at 96.
- **The Spire plot discussion** (he deferred it): prep with four candidate
  shapes at `design/Jawa/spire_plot_discussion_prep.md`.
- Flagged ship: "Fever-tempered" strange-hediff was BENCH's pick under his
  delegation — one word swaps it.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
- `WORLDMAP_FINAL_REVIEW_1` (doing): evidence + shots done; STOPS at the
  owner's STARE sitting. Next action: sit with him over the report + shots.
- `FLOOD_WITNESS_EVENT_1` / `VAPOR_EMITTER_PLACEMENT_1`: blocked on FOUNDRY
  items (flood-canyon mod; vapor cleanup pair) — nothing for BENCH until those
  land.
- `GIZKA_TRIBBLE_ADAPTATION_1`: fully ruled; the whole feature HOLDS on
  GIZKA_HOLD_HOOK_SPIKE_1 (FOUNDRY).
- FOUNDRY holds a fat actionable bridge batch filed tonight: WORLD_NAME_FIXES_1
  (7 ruled renames incl. the freeze re-stamp), SARLACC_WORLDMAP_RELOCATE_1,
  VAPOR_PLACEMENT_CLEANUP_1, TIBANNA_SOURCE_CUT_1 — batching them into one save
  window is the efficient move.
- Artpipe: 147 lanes await verdicts; pending/ is empty BY DESIGN (next wave
  gated on the owner's sheet) — do not refill it to satisfy the belt floor.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- Duplicate-design trap (cost a cleanup wave): item files don't record produced
  designs — sweep design/ + INDEX.md for prior product BEFORE delegating any
  "draft X". Three duplicates in one belt wave.
- The health dashboard's "0 clean" headline was a git-lock-starved run
  presenting total ignorance as measurement (HEALTH_UNMEASURED_HEADLINE_1
  filed). Any generator that runs during FOUNDRY's commit storms can do this.
- Subagents that "wait for a notification/monitor" are HUNG — no notification
  ever reaches them. Two hit it tonight; the fix is one foreground loop inside
  a single Bash call. Also: map parallel-spawn agent IDs from each spawn
  RESULT, never by prompt order — a misdirected resume nearly put a second
  driver on the bridge.
- git add with a missing path drops EVERY listed file silently when stderr is
  suppressed; and a lone .git/index.lock that is 0 bytes with no live git
  process is stale and safe to remove — but pgrep first, always.
- The game can sit at the main menu with the bridge answering — "No world is
  loaded" from every world tool. Load CANONICAL_ASHKARR_2026-09-09 and poll
  world_info until it returns REAL DATA; never trust the load call's own
  success.

## Closed since the last handoff (7)

- `DASHBOARD_HUB_ARTIFACT_1` — e4c0e9acd5f25778b423766aa0bd3c8afb8d137b
- `RECORD_HUB_HEALTH_PROOF_1` — 286790738
- `DUNGEON_DESIGN_RESEARCH_1` — 78234b27a
- `CANON_PLANET_CENSUS_1` — d49aa5f03
- `MUTATION_MODIFIERS_SURVEY_1` — f4a40fd1d
- `MECHANICS_CARDS_SITTING_1` — 6d13d4b07
- `CSV_REGION_SYNC_1` — 0b3c6d937

## Filed and still open (2) — the next seat's queue

- `VAPOR_PLACEMENT_CLEANUP_1` — Vapor emitter part-4 cleanup per the 2026-09-12 ruled rules: magma-vent 5 out-of-lock tiles, ancient-vent ruin-only audit, swamp/ruin gas re-seat, Poi
- `ASHFALL_SPIRE_LANDMARK_1` — Place The Spire landmark (Ashfall Research Base site): thin black needle, disc pad near top, intermittently visible through Scald turbulence — live pl

## Commits

```
7138c5455 All seven world renames RULED (owner cards): Site Aurek, Farside Station, Site Cresh, Cold Stores, The Breaks, Cratercrown, Zeddo's Salvage Yard — WORLD_NAME_FIXES_1 spec complete
bb9438816 SHRINE_GUARDIAN_BIOME_GATE_1: live-verify on a repainted Desert quicktest map, close
4d73c5a80 rimflow: sync ledger/queue views after QUICKTEST_POSTSETUP_CRASH_1 close
fa95b3fdc QUICKTEST_POSTSETUP_CRASH_1: live-verify the XML self-prereq fix was insufficient; real fix is a Harmony guard
76025543f Mark MandrakePatches About.xml CLEAN (new loadAfter entry for tonight's research self-prereq fix, correctly documented)
bd35a33b5 rimflow: sync ledger/queue views after DROID_SYSTEM_BUILD_1 close
5736f2888 DROID_SYSTEM_BUILD_1: fresh minimal-list spawn/NRE proof; item's reopen premise was stale
b6b5d5ba2 QUICKTEST_POSTSETUP_CRASH_1: fix RR_ElectricityBasics self-referencing prerequisite
daf8e2592 HELIX_TELLUROX_BUILD_1: live spawn/butcher proof done, re-blocked on HorrorWastes cast wiring
9fb08f576 rimflow: sync ledger/queue views after tonight's close/needs wave
65b2dc41c File QUICKTEST_POSTSETUP_CRASH_1; re-block 3 items on it
3e05542a6 CreatureBehaviors: rebuild DLL -- committed copy was stale vs source
133a257c5 Closes: NINEFOLD_FIRE_HOOK_RATELIMITED_1
0ce4c1c30 Closes: BUILDING_THEFT_HAULER_1
e9cce8686 Live world batch: SARLACC relocate, Colony rename, VAPOR Part-4 cleanup
f28cd7521 ASHFALL_SPIRE_LANDMARK_1: live-checked, re-blocked needs=offline
257bbbc7f fix: RUT_Webwork_{Anchor,Web,Gutter,Nest} missing thingClass crashed EVERY game load
a0936110a Code review: 6 tonight's-work files clean, no fixes needed
f3754dac7 rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1's cleaning pass
682f5c0ac Code review: LanternDeeps mineshaft/darkness files clean
cd536a36a LanternDeeps: rebuild DLL (no code change, verification build for review)
ea656f205 Mark ShokkweaveEconomy About.xml CLEAN after fix
b0d3ba6fc ShokkweaveEconomy: correct stale About.xml claim (FrontCreep now exists); mark StructureInjectionsRUT.csproj CLEAN after review
02648abb2 Droidworks: rebuild DLL, mark Droidworks.csproj clean
d9f505eae rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1's cleaning pass
7c69183af DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean tonight's dashboard/tooling fixes
9e5089f22 DIRTY_CODE_REVIEW_STANDING_LOOP_1: fix silent-zero ledger failure in project_maturity_dashboard.py
62c3d3c9a Code review: StructureInjections.csproj clean
c89c85687 StructureInjections: rebuild DLL (no code change, verification build for review)
d261cc238 Code review: RimProperty PropertyTuning.cs and RM_Property.csproj clean
ee8057a78 RimProperty: remove dead AnimalTheft MTB constants from PropertyTuning
17d4028dc Code review: ShipShields particulate/predictive/landing-advisory files clean
291b653cf ShipShields: rebuild DLL (no code change, verification build for review)
73ee4d1bb DROIDWORKS_WIPE_SEVERITY_1: root cause fixed - droid patients can never be InBed()
72034dd1f Deploy ShipShields DLL (not in live ModsConfig, no lock); SHIELD_MODS_LEVERAGE_1 now needs=bridge
ea5d07d5c SHIELD_MODS_LEVERAGE_1: finish particulate screen, build predictive-failure alert and landing advisory
220eef337 SETTLEMENT_VISIT_LOOP_1: staleness already resolved, deep re-verify vs RimSage finds no bugs
6e08a7e7e rimflow: BUILDING_THEFT_HAULER_1 reclaim/start/needs=bridge, plus queue re-render
3d4c98650 BUILDING_THEFT_HAULER_1: mechanism re-verified clean, DLL deploy confirmed already done
8a20ae7b2 VAULT_DUNGEON_BUILD_1: tally pass, no new creative content this round
e93bb33d6 NINEFOLD_FIRE_HOOK_RATELIMITED_1: still deploy-blocked, mod DLL locked live
415669d91 Close GIZKA_HOLD_HOOK_SPIKE_1: live-confirm Scenario.PostGravshipLanded fires
f9f45c391 INHABITED_AUGMENTATION_BUILD_1: wire 4 more built archetypes (8.4/8.6/8.10/8.13)
80244e7f8 RUST_CATHEDRAL_MECHANICS_1: build §1 hum-mood system (2/6 sections now, walls+roaches prior)
3eced2c32 LANTERN_DEEPS_INJECTION_1: ruined-mineshaft entrance + darkness mechanic
d0e3b19ab VAULT_THAW_QUEST_FAMILY_1: build the missing WAKE/LOOT signal sender for V6
97416ab49 SETTLEMENT_VERBS_WAVE_1: build walkable-commerce verb (2/4 families now live)
999b1aa0a TILE_STRUCTURE_DESIGNS_1: whisper batch 1 - engine + 3/22 rows wired
d4d359683 World rename proposals: Helix sites + two feature near-dups, SW-precedent grounded
cc6692c8f SHOKKWEAVE_SOLE_SOURCE_1: build web-cutting + nest-raid harvest routes
040cc28df canon.yml settlements: live census landed (96, owner card); WORLD_NAME_FIXES_1 filed (Zeddo's Salvage Yard ruled verbatim)
16ae5500f Close TIBANNA_SOURCE_CUT_1: fix a CherryPicker-crashing comment, verify both cuts live
5fc19bff1 WORLDMAP_FINAL_REVIEW_1: capture full-planet STARE screenshot set
e2b1262d3 MLIE_FAUNA_ABSORPTION_1: defName-drift sweep + Iriaz/Mudhorn ported
09c2eb0b1 Ledger: close LIQUID_TYPES_SPIKES_1
4457f42c1 WORLDMAP_FINAL_REVIEW_1: evidence pack recorded; STARE + verdict remain for the owner sitting
190484852 WORLDMAP_FINAL_REVIEW_1: night audit report — features/regions 0 mismatch, terminator fix confirmed live, 283 ancient-vent violations quantified, sarlacc landmark counts flagged
a0b7c4b21 Ledger: close CSV_REGION_SYNC_1 (all 809 region mismatches resolved)
0b3c6d937 CSV_REGION_SYNC_1 complete: Abandoned Mines 34 tiles landed from live feature read (22 Ashfall + 12 Notch), freeze re-stamped; night world dumps committed
c56a541e8 SHRINE_GUARDIAN_BIOME_GATE_1: build + validate the ambient shrine guardian gate
a2ca0eb73 Lessons: map parallel-spawn agent IDs from results, not order
08b909d33 WAR_LAB_CRATER_HOOK_1: wire CompIgniteCraterOnDestroy to a new reactor-core def
3a3596e8e rimflow: note real landing commit for HUB_TAB_PUBLISHER_MIGRATION_1's close
8ff50a8be Repoint artpipe + maturity publishers to the dashboard hub
51813d54e Surveyor-misdirection quest spec (three deception verbs, GM-fired offer); both night quest specs registered in INDEX
e887d0192 Flood-witness invitation quest spec (prose, per ruled design; alert-unlock flagged unruled)
942e51465 Art verdict sheet v2: 95/147 lanes with true original-vs-regen side-by-sides (89 extracted from live textures); 52 no-original lanes listed with reasons
27cbded5f Owner AFK: "I'm going to bed, afk. Go as far as you can. Keep subagents going!"
98ab47464 rimflow: sync ledger for DIRTY_CODE_REVIEW_STANDING_LOOP_1 note
45e009211 mark-clean: RM_CompVerminNest.cs, RM_ShipVermin.csproj
daaf1cd31 mark-clean: check_canon.py, selftest_check_canon.py, doc_claims.py
af13037d4 doc_claims.py: flush the table before absorbing trailing prose with no blank line
785b67074 Fix codebase_health headline lying '0 clean' on an all-unmeasured run
31431ae8e rimflow: sync ledger for SARLACC_HABITAT_BUILD_1 claim/block
91a75fd0f SARLACC_HABITAT_BUILD_1: build the sarlacc's native-habitat creature/mechanics (RSW tier)
4f657da7e Art verdict sheet v1 (147 lanes) + generator and verdict-applier; originals resolution pass owed for 141 redo lanes
12cd5c306 TIBANNA_SOURCE_CUT_1: cut the non-beldon tibanna sources (CARD T1)
5f4f56066 Health rebuild after git-lock-starved run (1669 green, 0 unmeasured); hub v10; HEALTH_UNMEASURED_HEADLINE_1 filed
cd320df9c Note: CANON_CONSISTENCY_CHECKER_1 close content landed in 21b30f26a
84c4afa20 Note: WRECKAGE_VERMIN_SPAWN_1 close content landed in 21b30f26a
21b30f26a Hub: retheme embedded health page to the brown palette (retheme_health.py); iframe backgrounds off white; published v9
7629d0884 Hub: embed full health/maturity pages as iframed tabs; art tab gains unresolved-review-sheets links (artsheets subcommand + manifest); published v8
bdebe751f Sarlacc design ACCEPTED (owner 2026-09-12): all forks ruled, Devourer-modeled swimmer, RSW tier; spec struck in part; deep_desert ban-5 carve-out under the freeze; SARLACC_HABITAT_BUILD_1 replaces design item
16f42b74b CANON_CLAIM_TAGGING_1: Phase 0 canon tagging in doc_claims.py
c53845fdf Fix check_canon [water] rule matching any 25% regardless of context
ce9a1ca54 SCALD_DIVING_MOD_1: v1 Deep Diving mod (blocked, not closed)
5782ab18e Spire plot-discussion prep: threads, tensions, four candidate shapes + sitting agenda
d56e28654 Canon storage adopted (Phase 0+1, owner card); three FOUNDRY items filed; checker water-rule fix filed
9b45ff076 Regenerate project tracking (owner request): all four hub tabs re-sourced, lamps GREEN, hub republished v7
26cd324b7 Close MODLIST_RESTORE_AND_BATCH_DEPLOY_1 (criteria met 2026-09-09, still healthy); note Ikee-half-dead finding on IKEE_MYNOCK_ART_REGEN_1
e93f9b9fd Drop PLANETARY_BEAUTY_LOADSCREENS_1: owner terminated it live this session
05ffb83af Planet status: remaking -> frozen (owner card; the freeze's own condition met) — planet rules bite; FactionSlate 14->13 stale count; gizka free-gift IN v1
c9bc11ff7 Miasma strange tier ruled in full: five hediffs selected (Swarm-marked, Salt-blooded, Loam-lunged, Mother-dreamed, Fever-tempered); Tide-reader cut
b20a3ebc6 GIZKA_HOLD_HOOK_SPIKE_1: gravship-landing hook identified, live proof owed
facc17f68 Ledger: close MECHANICS_CARDS_SITTING_1
6d13d4b07 Card sitting 2026-09-12 complete: PF weather ratified, injection fauna = envelope union; sitting record; ASHFALL_SPIRE_LANDMARK_1 filed
f9a1329c9 rimflow ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 tail-wave note
c92b4eaf6 Mark 10-module DIRTY_CODE_REVIEW_STANDING_LOOP_1 tail wave CLEAN (Greentide, LoreStages, Ninefold, RaidRedesigner, SacredGraffiti, DesertVehicleReskin, Shokk, LanternDeeps, RestrainingBolts, StructureInjectionsRUT)
fd3bafa39 Liquid+Scald cards ruled: Scald FRESH (rivers flow OUT — wrong inflow premise deleted), steam-catch both+toggle, diving is v1 (SCALD_DIVING_MOD_1), coolant Other bucket, films in v1
3b8e16ddf Mark 5 leftover .csproj files CLEAN (missed in the hydro/dune batch pass)
ce01a5a8a rimflow ledger sync: close FLOOD_CANYON_BIOME_1, block WRECKAGE_VERMIN_SPAWN_1, bridge released
083dea2c7 Mark RiverColors and ShipMemory .csproj files CLEAN (missed in earlier pass)
582ebeaf7 rimflow ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 five-module wave note
53cb421d2 Mark Aftermath/FluidCanals/ManyWaters/MovingDunes/ProximityHatch CLEAN after full-file review
5f12f476e Fix MovingDunes influx double-scaling on the drift-speed slider
fa13c2092 rimflow ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 tail-wave note
d9bac2fc3 Mark Pyrelands/RustChrome/StructureInjections/WeatherSuite/JawaRules CLEAN after full-file review
2467e0a2d rimflow ledger sync: RiverColors/ShipMemory clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
94349307e Mark RiverColors + ShipMemory Source CLEAN after full-file review
1cff9edb0 Mark DroidRepairJobs QuestNode + Antiquities job/workgiver CLEAN after full-file review
e758283f4 Snapshot the live campaign mod list before the flood/shipvermin test swap
d5afc7409 WRECKAGE_VERMIN_SPAWN_1: fix two live-confirmed defects, spawn still unproven
e319ec73f FLOOD_CANYON_BIOME_1: live-verify the chime/flood/recede cycle and the master toggle
3469c9625 Mark Inhabited Source (InhabitedFateWorker, MapComponent_InhabitedWatch, Patch_BeggarsFromPool) CLEAN after full-file review
6cbc02a1e Mark RimUtinni/FungalSoilTrade Source (GenStep_ScatterFungalGround, MapComponent_RotFungalDistress, csproj) CLEAN after full-file review
5f3ba0678 rimflow ledger sync: SWBestiary clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
5a13e0abc rimflow ledger sync: Visibility clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
e28106030 Mark SWBestiary Source (ThoughtWorker_IkeeNearby, CompKilnBelly, CompLightAversion) CLEAN after full-file review
4b5c50715 Fix CompKilnBelly: doseFeedDef was never checked, any CompKilnFeed item counted as a dose
fe34bf6ea Mark RimMandrake/Visibility Source module (3 files) CLEAN after full-file review
b4a195534 rimflow ledger sync: PlantGrowth clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
2467077e3 Mark RimUtinni/PlantGrowth Source module (3 files) CLEAN after full-file review
5f995fb3f Mark RimUtinni/LongHunger Source module (3 files) CLEAN after full-file review
e2333e565 Fix LongHunger: nextPulseAt ignores durationMultiplier for the first tremor
ac5d19d92 Mark RustCathedralWalls Source module (3 files) CLEAN after full-file review
67fdbff6b BrainWorms: rebuild DLL with tonight's 3 fixes (stale-cold expulsion check, dead expelledWorm setting, ETA tooltip ignoring rate multiplier)
1056c8a11 rimflow ledger sync: BrainWorms clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
456c555e5 Mark BrainWorms module CLEAN after full-file review
6e94c55d0 Fix BrainWorms: stale cold-flag surgery race, dead expelledWorm field, ETA math
e7bf384ea ShipShields: rebuild DLL with the thermal-veil PushHeat double-divide fix
38e75a3fd Mark ShipShields Source module (4 files) CLEAN after full-file review
fdbba895e Fix ShipShields thermal veil: apply room temp delta directly, not via PushHeat
0f6497f66 rimflow note: JawaIonWeapons clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
aeccad6b9 Mark JawaIonWeapons module (6 files) CLEAN after full-file review
635efab7f rimflow note: Graffiti Source clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
433aea6f5 Mark Graffiti Source module (6 files) CLEAN after full-file review
76a58422a rimflow note: ScavengerEvents clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
982aa8ce7 Mark PyrelandsMechanics Source module (7 files) CLEAN after full-file review
2679d79d8 Mark ScavengerEvents module (7 files) CLEAN after full-file review
d2db1fa70 ScavengerEvents: fix ShipBreak's silently-empty loot corpse; correct a mislabeled DropThingsNear param
84a2a0e39 Mark TitanicCreatures CorpseSite/Footprint/Wake module (7 files) CLEAN after full-file review
7c9b0e9ef TitanicCreatures: fix broken thick-roof pathfinding avoidance
afe33b556 Sump beast, Forge tower/rain/beldons, Tibanna T1+T2 ruled (owner sitting 2026-09-12); TIBANNA_SOURCE_CUT_1 filed
457e31588 rimflow note: CreatureBehaviors clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
64ea45985 Mark CreatureBehaviors module (7 files) CLEAN after full-file review
20ce46f24 Mark EnvironmentalHazards module (9 files) CLEAN after full-file review
0637431c1 EnvironmentalHazards: apply hazardDamageMultiplier where the retrofit missed it
0ba73d7a2 VAPOR_TERMINATOR_GEYSER_FIX_1: zero SteamGeysers_Increased at/past the terminator
60d204c4a Mark Pits module (8 files) CLEAN after full-file review
744da3686 Fever Wood cards 2-3 + Sump cards 1-2 ruled: Tenant rescue window, 40-cell fear, moat fire cascades, traps disarmable
831201d4c Miasma cards ruled (strange tier real: 2-3 hediffs owed; surge kills unfloored crops; creche marked-only); Fever Wood plumbing factions fine
4b440f019 Pits: fix stale build-command path in csproj header comment
2d76cdd96 Ledger note: RimProperty code-review wave closed
a8216aed8 Gizka cards ruled (tunable slow default, 15 silver, cull guilt in, HOLD for hold-hook); spike filed as the gate
db6532a4d Mark RimProperty's 10 dirty files CLEAN after full-file review
c62d11c4c RimProperty code review: fix suspicion-prune half-life mismatch, stale build-path comments
2752470f8 rimflow: log Droidworks code-review wave note
720f2f8a9 Mark Droidworks module (21 files) CLEAN after full-file review
d0c985e6a Droidworks: fix garbled log tag in BoltCorePatches error messages
8f86f501a canon.yml helix_lineage: splice_motive ruled — the key over the Cathedral's machines; works, or seems to; cost held open
8990896f2 Ashfall base cards ruled: literacy-ladder gating, Helix key-motive (works, or seems to), landmark = The Spire; campaign function TBD
f921a1e78 KYBER_TRADE_PLOT_1: Mod Settings retrofit for the kyber quest content
90059a2a1 KYBER_TRADE_PLOT_1: build the Homestead visit + donation/smuggle quests, block on GM-layer Heat
822b6fa48 CATHEDRAL_PLAYER_CONCEALMENT_ARC_1: all five cards ruled, build unblocked
803cec81c Cathedral A2-A5 RULED (owner cards 2026-09-12): reveal scope minimal; exposure is a real losable outcome; surveyor quest IN; sale exposure by volume
99295c49c Cathedral A1 RULED: the Utinni knows — she receives the Rakatan transponder on dead frequencies; ledger: close MUTATION_MODIFIERS_SURVEY_1
f4a40fd1d Contagion mutation deck RULED (owner cards 2026-09-12): custom gene, vanilla removal risk, 50/50 large-variance rolls
0660a11f1 MOD_OPTIONS_RETROFIT_1: record progress, block pending live verification
7a14e5ed2 MOD_OPTIONS_RETROFIT_1: real Mod Settings for 46 mods (Greentide's cross-biome opt-in included)
4c98263c4 mark-clean: WRECKAGE_VERMIN_SPAWN_1 ShipVermin/Utinni files
96156db67 rimflow: claim/block WRECKAGE_VERMIN_SPAWN_1
5b0fefcf5 WRECKAGE_VERMIN_SPAWN_1: wreck-anchored vermin nest mechanism
1325cfac6 mark-clean: AmbientShrineGuardians.cs, GeothermalDensityField.cs
4cd37218f MOD_OPTIONS_RETROFIT_1: settings gate for UtinniPatches ambient shrine doctrine and geothermal density field
a99079e96 mark-clean: HUB_LAMP_TIME_FIX_1 dashboard hub scripts
a49c5ea77 HUB_LAMP_TIME_FIX_1: fix hub dashboard timestamp/staleness bugs
cb2e69890 FLOOD_CANYON_BIOME_1: standalone RimMandrake Flooded Canyon biome mod
338d886c4 rimflow: claim/close MUDSWALLOW_LIVE_LIST_FIX_1
eb5826bf0 mark-clean: MudSwallow Scan() fix and RUT_Greentide.xml wildPlants guards
7949f4eac MUDSWALLOW_LIVE_LIST_FIX_1: fix live-list mutation bug, guard Greentide wildPlants
74c87278e Ledger: close CANON_PLANET_CENSUS_1
d49aa5f03 CANON_PLANET_CENSUS_1: land the corrected planet census; frozen CSV declared sole census source (owner card 2026-09-12)
869a4dd61 Vapor rulings landed (owner card sitting 2026-09-12): 3 ratified + PoisonForest gases + helixien junker rule; cleanup filed for FOUNDRY
2e68e1674 CSV_REGION_SYNC_1: land five region renames + freeze re-stamp (owner card yes, provenance verified)
7c8ccb757 CANON_PLANET_CENSUS_1: owner caution — CypreJungle/GreaterSwamp are pending-swap donor names, not canon rows
0881775a6 CANON_PLANET_CENSUS_1: frozen-CSV re-census closes the gaps (29 biomes explained, rivers 298, water 6.62%)
593c9a619 WRECKAGE_VERMIN_SPAWN_1: vermin spawn from wreckage (owner 2026-09-12, verbatim)
90f35057f Card-sitting agenda (46 pending decisions); correct two stale awaits-ruling claims — explosive design's core rulings landed 2026-09-10
ecf63d997 FOUNDRY handoff 202609120305: Shokkweave/roaches/wall-tier live-verified, corrupted-mods root cause fixed, major worldmap finding for the owner
cec07be1a CANON_PLANET_CENSUS_1: sitting-prep block (24 cited rows) + honest gaps; lessons line on duplicate-design trap
1276c6c44 Remove duplicate explosive/flood drafts made blind to the 2026-09-10 canonical designs; salvage folded in as dated addenda, all references repointed
e5b194b4e Update FULL.LATEST modlist snapshot (592 mods) and regenerated health/hub artifacts
91ca2f18e GIZKA_TRIBBLE_ADAPTATION_1: ship-pest design draft (reuses active donor creature); delete 2026-09-08 spec built on wrong art-absent base
0001bce2d Code review: RustCathedralWalls (RUST_CATHEDRAL_MECHANICS_1 §2), all 14 files CLEAN
67cbd7f5a HUB_LAMP_TIME_FIX_1: lamp ages off by UTC offset (confirmed; the recorded 7.0h was the artifact) + hub_check gate holes; caveat on DASHBOARD_HUB_ARTIFACT_1's numbers
077eb2502 MUDSWALLOW_LIVE_LIST_FIX_1 filed (live-list mutation bug, confirmed); GIZKA recon: Tribble module read, gizka already in SW Animal Collection
bfec1a970 FLOOD_CANYON_BIOME_1: flooded-canyons standalone RimMandrake biome mod (owner 2026-09-12); FLOOD_WITNESS_EVENT_1 narrows to the campaign beat
d04712072 Ledger: file VAPOR_TERMINATOR_GEYSER_FIX_1; belt-wave item states
7881bed55 VAPOR_EMITTER_PLACEMENT_1: emitter inventory + rule proposals + frozen-map audit (21 geysers violate terminator rule)
65b9ab9ad Batched live verification round 2: roach spawn confirmed, companion no-op check confirmed, river-tile count settled
241c9caca MOD_OPTIONS_RETROFIT_1: superb mod-options required on every mod (owner 2026-09-12); doctrine in CLAUDE.md
00cf6bedf FLOOD_WITNESS_EVENT_1: witness-event design draft + owner cards (4 routes)
a5bd2278b RUST_CATHEDRAL_MECHANICS_1 §2: wall-tier mining defs (the wall ladder)
ec5a6a510 CSV_REGION_SYNC_1: patched candidate (5 renames, 775 rows) + diff; Abandoned Mines blocked on per-tile authority
175e6e80f EXPLOSIVE_PLANT_GROWTH_1: terminal-moment design draft + owner cards (no build before ruling)
f1106a60b Ledger: close DUNGEON_DESIGN_RESEARCH_1
78234b27a DUNGEON_DESIGN_RESEARCH_1: dungeon design research corpus — sources, metrics catalog, canon experiences, map templates, skill sketches
9b2971f5b MUTATION_MODIFIERS_SURVEY_1: mutation-systems survey table + draft deck (owner rules the deck)
fb20bb12c Mark RUT_Greentide.xml CLEAN: donor GRiNDTerra Biomes references verified
02bca50d1 Lesson: a new mod referencing a sibling mod's not-yet-redeployed class tripped RimWorld's corrupted-mods recovery reset
e15f05a0e Ledger: close RECORD_HUB_HEALTH_PROOF_1; belt-wave claims
286790738 DASHBOARD_HUB_ARTIFACT_1: land FOUNDRY's publisher-side no-clobber proof (RECORD_HUB_HEALTH_PROOF_1)
484da7647 Mark batch-4 companion hardening files CLEAN after independent review
ef1525da6 Fix jawa/set_stuff regression from batch 4: SetStuffDirect call was deleted
8f4e8a0be Companion hardening batch 4: ~27 lower-value silent-failure findings (build-clean --gm, deployed)
a201115a5 Ledger: close NONDIV4_TEXTURE_FIX_1
79715b3d2 NONDIV4_TEXTURE_FIX_1: record our-mods phase done
cf3aee40b NONDIV4_TEXTURE_FIX_1: pad 87 non-%4 textures in our own mods (transparent, centered)
c593d594f HUB_TAB_PUBLISHER_MIGRATION_1: codebase-health hook now regenerates hub/data/health.json
eb27deefd Close DASHBOARD_HUB_ARTIFACT_1 — all verify boxes proven
e4c0e9acd DASHBOARD_HUB_ARTIFACT_1 verify complete: two-seat no-clobber proven live (peer republished health+art, shell+other tabs kept)
feec8c4fa Ledger: claim+start 3 offline items (companion hardening, texture padding, hub publisher migration)
0f08526fc Code review: RUST_CATHEDRAL_MECHANICS_1 §6 (roaches) marked CLEAN, no fixes needed
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     verify Webwork/Shrine/Shokkweave biome mechanics

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 D infrastructure/artpipe/pending/dactillion_v1_east.json
 D infrastructure/artpipe/pending/dactillion_v1_north.json
 D infrastructure/artpipe/pending/dactillion_v1_south.json
 D infrastructure/artpipe/pending/fanback_v1_east.json
 D infrastructure/artpipe/pending/fanback_v1_north.json
 D infrastructure/artpipe/pending/fanback_v1_south.json
 D infrastructure/artpipe/pending/grank_v1_east.json
 D infrastructure/artpipe/pending/grank_v1_north.json
 D infrastructure/artpipe/pending/grank_v1_south.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimUtinni/ShokkweaveEconomy/Defs/ThingDefs_Buildings/ShokkweaveHarvestNodes.xml
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

