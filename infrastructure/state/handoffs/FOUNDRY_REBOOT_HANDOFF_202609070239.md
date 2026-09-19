# FOUNDRY_REBOOT_HANDOFF_202609070239 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609070028`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`EnableDefaultCompileItems=false` + a hand-maintained `<Compile Include>` list in a
csproj is a LIVE, RECURRING trap, not a one-off from Ninefold's original history: it
silently excluded BOTH `TheftHauler` and `Visibility`'s new debug-action files this
same session, with "0 warnings/0 errors" the whole time — the compiler was never told
the files existed. Confirmed by `strings -el <installed DLL>` for a method-body log
string, not by re-reading the csproj (which reads fine either way). **Before trusting
any "0 errors" build result on a mod you didn't author from scratch, grep its csproj
for `EnableDefaultCompileItems` — if it's `false`, check every `.cs` file in the folder
is actually named in the list.** Both fixed this window (`6e6ce2d9`); if a THIRD mod
turns up with this pattern, it's worth a real sweep across every csproj in `src/`,
not another one-off fix.

## What the owner should see

- **RimWorld genuinely OOM'd this window** (~21GB, `start_debug_game_ready`'s full
  dev-quicktest worldgen on the current 603-mod list) with 15.6GB still free system-wide
  at the low point. The base boot-to-menu is fine; it is specifically that heavy
  quicktest path that's now the largest single memory event on this machine this
  session. Worth knowing before anyone else calls `start_debug_game_ready` on this same
  mod count. Worked around by loading an existing save instead (`gravship_scratch_e`,
  a fresh save with the current mod list baked in — no missing-mod warning on load).
- **Two new `_e` saves exist by request**: `gravship_scratch_e.rws` and
  `WORLDMAP_V1_original_e.rws` (the latter a fresh snapshot of the precious frozen
  world save, never overwritten — `_b`/`_c`/the `.bak` are all byte-identical and
  untouched).
- **A CODEX-authored proposal for a second, heavier graphics pipeline was reviewed and
  largely declined**, at your own request. Full verdict:
  `infrastructure/agents/OPUS_REVIEW_codex_graphics_second_pipeline.md`. The one
  real, cheap piece it surfaced (`CODEX_WRAPPER_HARVEST_FIX_1` + per-worker
  `CODEX_HOME`) WAS built and merged into the live pipeline (`814d4223`) — 14 real
  orphaned tree-art images recovered as a side effect
  (`src/RimUtinni/AshkarrFlora/_artsrc/sweetline_orphans_2026-09-06/`, contact sheet +
  README, one deliberately left as a placeholder since picking which becomes the
  shipped sprite is an art call). **A real image-generation smoke test of this fix is
  still owed and needs your explicit authorization** — none has been run, no quota
  spent.
- **`CODEX_PARALLEL_WORKERS_1` needs a ruling**: should the lighter "read Codex usage
  limits before batching" piece be built on its own, given the heavier
  queue+grumpiness-detector architecture it originally bundled was judged
  not worth building at this project's scale? See that item's own 2026-09-07 note.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `BUILDING_THEFT_HAULER_1` — touched this window for the batched live-verification
  pass. Code was already fully built by an earlier session; found and fixed a real bug
  this window (its debug-action test harness was silently excluded from compilation —
  see "Traps learned"). Not live-proven: `mandrake.rsw.droidworks` is not on the live
  mod list, so no pawn kind can carry `TheftHaulerExtension` — the harness bypasses the
  gate to prove the underlying job/Fire mechanism instead, but the real chassis-gate
  path is still unproven. Next action: either add Droidworks to the mod list + restart,
  or accept the harness-only proof as sufficient and close.
- `DEV_LOG_AUTOOPEN_SUPPRESS_1` — NOT touched this window. Inherited `doing` from an
  earlier session (filed 2026-09-03); I have no fresh information on it. Next action:
  `rimflow show DEV_LOG_AUTOOPEN_SUPPRESS_1` and read its own item file before assuming
  its state — do not trust this line for anything but "it's still open."
- `GRAFFITI_FRAMEWORK_BUILD_1` — NOT touched this window. Inherited `doing` from an
  earlier session (filed 2026-08-31). Same caveat as above.
- `MACRO_GENERATOR_V0_1` — NOT touched this window. Inherited `doing`, filed
  2026-09-06 (same day, different session). Same caveat.
- `MAPGEN_GL_SHEET_1` — NOT touched this window. Inherited `doing`, filed 2026-09-06,
  `needs bridge`. Same caveat.
- `MAPGEN_PAINTER_V1_1` — NOT touched this window. Inherited `doing`, filed
  2026-09-06. Same caveat.
- `SETTLEMENT_VERBS_WAVE_1` — touched this window for the batched live-verification
  pass. Its scoped piece (salvage-law claim-fee gizmo, `mandrake.rm.salvageclaim`) was
  already fully built by an earlier session, code-review CLEAN, deployed. NOT
  live-tested this pass: it is a pure right-click `FloatMenuOptionProvider` delegate
  with no `JobDef` and no debug action — there is currently NO bridge-reachable way to
  trigger it (confirmed: `rimworld/order_pawn` only issues Goto jobs,
  `rimworld/right_click_cell` is a known-broken synthetic click per
  `skills/rimbridge/SKILL.md` §4). Next action: add a small debug-action test harness
  (same pattern as `DebugActions_TheftHauler.cs`) before the next live-verification pass,
  or accept UI-only manual testing.
- `SETTLEMENT_VISIT_LOOP_1` — heavily touched this window. Full account is in the item
  file itself (`infrastructure/state/items/SETTLEMENT_VISIT_LOOP_1.md`, dated
  2026-09-07 sections): built the missing settlement producer (3 debug actions,
  confirmed registered and callable via `rimworld/execute_debug_action`), but the
  actual compose-step proof is still blocked on a real design gap — `CurrentTile()`
  always returns the currently-loaded map's own tile, so `GetOrGenerateMap` finds the
  existing map and never re-runs generation. Next action: give the debug action an
  explicit tile parameter (a `ToolMap`-typed action taking `x`/`z`) instead of
  "current tile," or add a bridge tool that can answer a `Dialog_DebugOptionListLister`
  picker.

## Traps learned

- **`EnableDefaultCompileItems=false` + stale `<Compile Include>` list** — see "The one
  thing to carry forward" above. Filed to `LESSONS_INBOX.md`.
- **A public field can be a better Harmony success-gate than replicating a private
  guard chain.** `Patch_GravshipLaunched.cs`'s first fix (gate on
  `parent.Spawned && CanLaunch()`) was itself wrong — `TryLaunch` has a LATER guard
  (destination distance vs. `MinFuelLevelInGroup`) that `CanLaunch()` doesn't cover.
  Fixed by gating on `CompLaunchable.lastLaunchTick` instead (public, set
  unconditionally right after every guard passes) — vanilla's own success marker, immune
  to future guard-chain changes. When a Harmony patch needs to know "did the real thing
  happen," look for the target's own internal bookkeeping field before writing a second
  copy of its gate logic.
- **A fresh-context adversarial review of your OWN just-written fix is worth running
  even when you already marked it CLEAN yourself.** The `lastLaunchTick` bug above was
  caught by exactly this — my own self-review had marked the first (wrong) version
  CLEAN. Also caught 3 more real bugs in debug-action test harnesses this same pass
  (a same-tile MapParent collision gap, duplicated code, a narrower-than-real test
  gate). All 4 fixed same session.
- **`rimworld/execute_debug_action`'s catalogue is the only sane discovery route on a
  large mod list** — never `search_debug_actions` (measured: livelocked and killed a
  568-mod game once already). Walk `list_debug_action_roots` →
  `list_debug_action_children` on `"Actions"` and filter client-side; a debug action's
  LABEL is a flat child of `"Actions"`, not nested under its `[DebugAction]` category
  string the way I initially assumed.
- **A `Dialog_DebugOptionListLister` picker opened via `execute_debug_action` cannot be
  clicked through from the bridge** — no tool exists to answer it. `rimworld/close_window`
  closes it cleanly (confirmed: `success:true`, `windowCountDelta:-1`), which is the
  right move when a debug action you invoked turns out to need a follow-up click you
  can't make.
- **`CurrentTile()` (the `Find.CurrentMap != null ? that tile : selected world object`
  pattern, copied from an existing debug action) silently defeats any test that wants a
  DIFFERENT tile than the one currently loaded** — switching camera view with
  `jawa/world_view` does NOT clear `Find.CurrentMap`. `GetOrGenerateMapUtility
  .GetOrGenerateMap` on an already-mapped tile just returns the existing map unchanged,
  so a map-generation-dependent test can report `success:true` while proving nothing.
  Full account: `SETTLEMENT_VISIT_LOOP_1`'s 2026-09-07 note.
- **A WSL process does not pass a bare env var to a Windows child process** — it must
  also be named in `WSLENV`, or the Windows side sees an empty value. Measured twice
  independently today (once by me investigating memory, once by the graphics-pipeline
  agent building per-worker `CODEX_HOME`). Any tool that shells out from WSL to a
  Windows `.exe` and relies on an env var needs this checked.
- **`strings -el` on a .NET DLL finds method-body string literals but NOT
  `[Attribute("...")]` constructor-argument strings** — those live in a different
  metadata blob encoding. Useful for proving "was this file actually compiled in,"
  useless for proving an attribute's exact argument text.
- **A full parallel selftest-suite run can produce false failures from environment
  contention or leftover state, not code regressions** — this session's `40/42` run
  showed a stale-worktree false positive (`selftest_one_path_seam.py`, fixed by
  removing the leftover `.claude/worktrees/agent-*` directory once its branch was
  safely merged/parked) and a timeout under 8-worker-parallel load that passed clean
  standalone (`selftest_cli.py`). Don't treat a failing full-suite run as gospel without
  re-running the specific failures in isolation.

## Closed since the last handoff (22)

- `LANDFORM_RECIPE_ROUNDTRIP_1` — f28586a6be865408d7d318b65fb6dfc1e7f5d6a3
- `TERRAIN_GRID_RENDERER_1` — 0ad8ecb5792b49531c36de6671a5b72657cfe9d4
- `CORPUS_MAP_STATISTICS_1` — e29c40c98cff7e429c30483b03147d3df5a183bc
- `GL_GRAPH_EMITTER_1` — 3ef2e7f565a3453a72dc44997a31ab126abb160c
- `ARMOURY_SWMODS_DONOR_GAP_1` — 94f8c6a923d8314c02b6933e5d06fdf2faa7a70b
- `ARMOURY_LEATHER_GEN_DESYNC_1` — 548432d9
- `BEHEMOTH_TEXTURE_MISSING_LIVE_1` — 74a53711
- `ARMOURY_MELEEPOWER_STALE_1` — da3a06e8
- `TILES_STAMP_VERIFY_1` — 104bb236
- `RESEARCH_VALIDATOR_BUILD_1` — f1ebc8c1
- `DROID_DONOR_PATCH_GATE_1` — 78224ac9
- `WILD_ANIMALS_PADDED_LISTS_1` — 7e937f14
- `MEGAFAUNAYIELD_GEN_BEHIND_1` — 589d9c9b
- `ARMOURY_GEN_HANDEDIT_DESYNC_1` — f95eacfc
- `LOAD_CONFIG_ERROR_SWEEP_1` — 7f781d1e
- `ARMOURY_ABSORBED_KOTORCORE_DUPES_1` — a24cda4d
- `DROID_RETIREMENT_ORDER_ASSERT_1` — 0f430178
- `DOCTRINE_LOADAFTER_STALE_1` — bf99382b
- `ARMOURY_SWMODS_MODNAME_GAP_1` — 62fbc541
- `MODSET_BUILDER_RESTORE_STALE_1` — abc1e7cd
- `RIMMANDRAKE_PITS_BUILD_1` — abc1e7cd
- `PROPERTY_FABRIC_BUILD_1` — ae21392d52ce05e652df917864d73aa42dec362c

## Filed and still open (63) — the next seat's queue

- `HORRORWASTES_BIOME_DISSOLVE_1` — Dissolve the HorrorWastes biome: re-biome its 1,711 tiles into neighbors (Deadstone receiving def ruled at the PropaneLakes sitting), re-freeze, re-ho
- `HORRORS_RAIDING_FACTION_1` — Horrors become a RAIDING faction (no settlements, nightside-gated encounters) + nests/sinkholes/crysalises injected as nightside dungeon content — the
- `CONTAGION_BIOME_PLACEMENT_1` — Move the Contagion (AB_OcularForest) to the peaks above the green: Scald Spine's 38 non-green highs + optional Ashfall/Dew Horn tops — NO green square
- `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` — Put the unused tile mutators and Geological Landforms landforms on the frozen world — 88 of ~380 in use, zero GL_* (owner 2026-09-06)
- `MACRO_GENERATOR_V0_1` — Macro generator v0: ONE idea per map — chooser + plan + terrain grid, graded on a comparator sheet by the owner (research doc §9.3 step 4)
- `CORPUS_STATS_VANILLA_CONTROLS_1` — Vanilla control maps for corpus_stats.py (≥10 at matched sizes) + corpus-vs-controls section; fix or drop the degenerate chokepoint proxy
- `NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1` — Ninefold: Patch_GravshipLaunched postfix fires on FAILED launches, feeding Ta'Baa for nothing (code review 2026-09-06)
- `STRUCTUREINJ_RUT_TEMPLATE_DEFECTS_1` — StructureInjectionsRUT: toll_gap.txt bakes rot=4 (invalid Rot4); glass_sea.txt is unreferenced dead content — regenerate from Lua
- `CODEX_WRAPPER_HARVEST_FIX_1` — codex_image.py discards finished images on timeout (harvest never runs) — fix, recover ~14 orphaned TREE_GRAPHICS images, retire chroma-key: native tr
- `CODEX_PARALLEL_WORKERS_1` — N-worker codex exec queue with receiving-agent AGENTS.md prose + grumpiness detector reading rollout rate_limits; own CODEX_HOME per worker
- `MAPGEN_GL_SHEET_1` — Map generator: 8 plans through the GL emitter, quicktest screenshots beside painter renders — the real terrain, one sheet (owner 2026-09-06: both rout
- `MAPGEN_PAINTER_V1_1` — Map generator painter v1: organic masks, elevation→terrain bands, hydrology with cause; v1 comparator sheet (owner 2026-09-06)
- `MAPGEN_CONVERGENCE_LOOP_1` — Map generator convergence loop: painter vs GL vs corpus, iterate until the owner calls it great (owner 2026-09-06)
- `LIQUID_BIOMES_MAP_1` — Four liquid biomes on the frozen world: boiling ocean, two brine seas, and the propane lake as worldmap tiles under Umbra (render before painting)
- `VEHICLE_FUEL_PATCH_UNFILTERED_1` — DesertVehicleReskin fuel patch widens fuel for EVERY Vehicle Framework vehicle (VVE trucks on potatoes); About.xml says draught only — owner ruling: i
- `GL_EMITTER_OBJECT_GAP_1` — gl_emit rebuilds 14 of 44 landforms one <Object> short (coast/river family, Gorge, Valley); selftest must cover all 44
- `ANCIENT_WAR_LAB_1` — The war lab beneath the propane lake over the Impact Site — submerged dungeon, lab fauna + mechanoid guardians, and the crater ending as a permanent m
- `FOUNDRY_REBOOT_HANDOFF_20260906C` — FOUNDRY reboot handoff 2026-09-06 (evening) - READ FIRST on wake
- `BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1` — build.py tool-removal guard byte-scans the DLL and reported a fictitious lost tool (jawa/pawn_); compare against source [Tool] declarations
- `LANTERN_DEEPS_INJECTION_1` — The crystal caverns as an injected underground layer beneath ≤ −40 °C nightside maps — quicktest the cave-map generation, two entrance features (emerg
- `COLD_LOAD_RUN_SHEET_4` — Run sheet for the next full-list load: three readings owed from the 2026-09-06 offline wave
- `DROID_FACTIONS_IN_FROZEN_SAVE_1` — Census: which droid FactionDefs/kinds/need classes are scribed in the frozen world and campaign saves
- `DROID_DONOR_REFGREP_1` — Per-donor reference grep: every KotOR/ABF/Asimov/Depot defName and class in src/ and every active mod
- `DROID_ORACLE_VOICE_DESIGN_1` — Design (dormant): four droid Oracle consumers with prescribed fallbacks, claude -p transport
- `DROIDWORKS_LIVE_LOOP_PROOF_1` — Minimal-list quicktest proof of the five-state loop on GNK + a KotOR kind; close the 8 open live checkboxes
- `DROIDWORKS_FULL_LIST_COEXIST_1` — Enable Droidworks in the full mod list beside the donors; cold load, texPath census, Harmony idempotency
- `DROIDWORKS_FORMAT_TIERS_1` — Format tiers blank/mindless/programmable/sapient with needs by tier (ruling 4), work gating, format recipes
- `DROIDWORKS_MODULE_ABSORB_1` — Absorb KotOR's six-slot droid module apparel as RSW_DW_Module_* (loot-only, no recipes)
- `DROIDWORKS_HEADS_BRAINS_SPIKES_1` — Brain trio (import-only), per-family heads with CompHeadIdentity, the mindstone head, per-faction data spikes
- `DROIDWORKS_FINE_PARTS_1` — Fine parts per family (limbs, sensors, motivators, cells) with quality, drop tables and stat/personality effects
- `DROIDWORKS_SHOP_BENCHES_1` — Repair bench, reassembly harness (head-gated), rebuild-from-corpse, overclock as a bench job
- `DROIDWORKS_BOLT_PAYOFF_1` — Restraining bolt consequences: mood aura, rebellion on removal past resentment threshold, shear on damage, un-bolt-each-other
- `DROIDWORKS_ION_SHIELD_BODYSIZE_1` — Ion breaks shields (EMP side-damage) and scales by body size — merge with ION_STUN_IGNORES_BODY_SIZE_1
- `DROIDWORKS_DETONATION_REVIEW_1` — Detonation grid (energyDensity x charge) built and SAVED for the owner to walk; deny-module on JDS battle kinds
- `DROIDWORKS_PRIMITIVE_TIER_1` — Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats, the G2 repair droid (new art), the Junker suicide droid
- `DROIDWORKS_WIPE_SEVERITY_1` — Memory wipe: 7-day severe relearning debuff, service-record reset, permanent accreting hardware quirks
- `DROIDWORKS_RESEARCH_ROWS_1` — Seven Droidworks research rows in The Unbolting; cut the Depot droid-brain rows; brains never researchable
- `DROID_FACTION_LOADOUTS_1` — Droids in every faction's hands: Empire attack droids, Homestead utility droids, Hutt heavies, Junker suicide droids, traders' protocol droids, Trade 
- `DROID_FDE_KINDS_REPOINT_1` — Repoint the 4 Jawa_Droid_* FDE kinds and FDE droid backstories onto Droidworks races (fix the generator)
- `DROID_FDE_GOODWILL_CAP_1` — Free Droid Enclaves goodwill cap via GoodwillSituationDef (spec: restraining_bolt_technical.md)
- `DROID_PROTOCOL_TRADE_ADVANTAGE_1` — Protocol droid in the trade party shifts prices both ways; none on your side is a penalty
- `DROID_REPAIR_FOR_PROFIT_EVENTS_1` — Recurring event: friendlies bring droids for paid repair/upgrade; inferior/superior parts choices; offload problem droids
- `DROID_HUTT_CAPTIVES_1` — Droids held in Hutt torture chambers as a rescue-or-purchase source at Hutt sites
- `DROID_DISTRESS_CALL_REPOINT_1` — Re-point the BTD Droid Distress Call quest's 5 KotOR kinds to Droidworks kinds; reframe as the crashed-droid rescue
- `DROID_RETIRE_KOTORDROIDS_1` — Retire guy762.kotordroids (wave R1) after modules, heads, loadouts, FDE repoint and Distress Call are closed; cold load
- `DROID_RETIRE_ABF_SYNCORE_1` — Retire ABF + SynCore (wave R2); DroidDonor_ABFGate fires; remove DroidsAreMachines ABF half; cold load
- `DROID_RETIRE_DEPOT_ASIMOV_1` — Retire Droid Depot + Asimov + MSEDroidFix (wave R3); repoint the Empire KX kind; retire NoDroidManufacture; cold load
- `DROIDWORKS_CHASSIS_PERSONALITY_1` — Per-family starting-trait weights and the protocol-droid pedantry social modifier
- `DROIDWORKS_SERVICE_RECORD_DRIFT_1` — CompServiceRecord: time-since-wipe accretes chassis-weighted idiosyncrasies; wipe resets
- `DROIDWORKS_MODULE_PERSONALITY_1` — Installed modules carry attitudes: CompModulePersonality trait-hediffs while worn
- `DROIDWORKS_WILD_DROIDS_1` — Wild crashed droids: factionless erratic hostiles, capture -> Wild spike -> reprogram-as-recruit with resistance
- `NIGHTSIDE_ICE_DEF_1` — Author RUT_NightsideIce (own def inheriting vanilla IceSheet, every list overridden, no arctic zoo, aurora-clear) and paint its 802 highland tiles und
- `ARMOURY_LOADAFTER_STALE_1` — Armoury declares 3 loadAfter packageIds against roughly 40 mods its patches actually target
- `PATCHMODS_LOADAFTER_SWEEP_1` — StarWarsPatches and UtinniPatches have the same undeclared-loadAfter gap; sweep every mod of ours that patches somebody else
- `PATCH_LEDGER_MINUS_ONE_OSCILLATES_1` — 87 patch_ledger entries record an original of -1, and any op emitted onto one oscillates in and out on alternate runs
- `ARMOURY_SUBSTRING_RUNG_TRAP_1` — gen_armoury_patch's 'repeater'/'heavy'/'cannon' substring rung can retune any third-party projectile a turret drags in
- `FUNGALFOREST_RAID_MERGE_1` — Dissolve BMT_FungalForest (an underground def on 425 surface tiles) into its neighbors per the measured cluster table (the Rot; Wasteland at South Cra
- `FUNGAL_SOIL_TRADE_1` — Jawas dig fungal soil from the Rot and haul it to the moisture farms by ship — early money; digging sends distress through the fungal whole and brings
- `MOISTURE_FARM_TEMPLATES_1` — Content injection: several highly plausible moisture-farm templates (homestead, vaporator field, cistern head, compound, ruin) — needed many times ove
- `WORLD_RIVER_COLORS_1` — Color the worldmap's rivers by segment (red headwaters → brackish green/brown jungle → toxic brown/blue termini) and the propane lake slate cyan — Riv
- `SAND_SWIMMERS_MOD_1` — Sand fishing: impassable Deep Sand pools you fish like water, with sand-swimmer analogs (never fish-shaped) — the sand swimmers mod
- `OASIS_LANDMARK_PLACEMENT_1` — Hand-place and hand-name the Oasis landmarks on Weeping Stones tiles with per-site mutator loadouts (uplink/haven/stockpile/dead ring); seep-oasis sit
- `OASIS_MUTATOR_PATCH_1` — Whitelist ZBiome_DesertOasis into vanilla TileMutatorDef Oasis; strip donor snow weathers; re-point forageability; alien-flora swap in additionalWildP

## Commits

```
4de79033 rimflow ledger sync: this session's claims/starts/blocks/drops/closes/file
814d4223 Merge graphics-pipeline fixes: harvest-on-timeout, per-worker CODEX_HOME, chroma-key retirement
9ea7e950 codex_image.py: a timeout is not a failed image; per-worker CODEX_HOME; retire the chroma-key generation path
64e09460 Mark 6 files CLEAN after adversarial review + fixes
572413c0 Adversarial review (fresh-context agents): fix 4 real findings
e2d042e2 COLONY_VISIBILITY_BUILD_1: note the csproj fix, live sweep still owed
ad6fef13 SETTLEMENT_VISIT_LOOP_1: debug actions confirmed live-callable; compose proof still blocked on same-tile GetOrGenerateMap no-op + no picker tool
6e6ce2d9 TheftHauler + Visibility: fix silently-excluded debug-action files (real bug)
50e9677f Bank CODEX's second-graphics-pipeline proposal, unvalidated -- do not act on it yet
5c1f7df9 biome status table: weeping_stones + cracked-lands enrichment rows added beside the done sheets; next = Cypre Jungle; _openers_prep marked as decayed on list membership (README table is the authority)
504093ef close CRACKED_LANDS_ENRICHMENT_1 at dd8c7c71
dd8c7c71 the_cracked_lands.md: enrichment backfilled and ratified — time-sorted bestiary (the Sealed/Spenders/Patient, no-truce inversion), water chimes with the owner's tooltip, discovery surveys, crack-wax, NEVER-the-bottom ban; explosive visible growth ruled WORLD-WIDE (EXPLOSIVE_PLANT_GROWTH_1) with a plotted witnessed flood (FLOOD_WITNESS_EVENT_1); grammar README gains the enrichment step
4df56038 SETTLEMENT_VISIT_LOOP_1: log the start_debug_game_ready OOM crash
36d7e0b6 file CANON_LORE_PROPAGATION_1 — Wednesday 2026-09-09 post-reset: canon→lore propagation sweep + the three-layers-of-canon rethink sitting; claim CRACKED_LANDS_ENRICHMENT_1
95cf8525 Weeping Stones rulings landed: truce cheap-for-v1, dewback move RULED, droids never take potable water (propagated to faction_roster_v2 water doctrine); four items filed (landmarks, mutator patch, roster, cracked-lands enrichment backfill)
56f07f2d weeping_stones.md: enrichment pass — bestiary (7 natives + 29-cast reconciliation, dewback mis-cast found), weather+sound (fog at wind-hour, singing vanes), items/structures ladder, 11 faction faces of the water; owner's pass owed
4af94dfb TheftHauler + Visibility: test harness debug actions for the batched live-verification pass (Droidworks not on the live mod list, no other way to reach either mechanism)
bc1ccdb4 Inhabited: add the revisit half of the test harness (casing proof)
7e08f3af Inhabited: build the missing settlement producer (test harness)
09552b98 weeping_stones.md: biome sheet written with the owner — dew+relic engine, biome+landmarks architecture, the truce, the comb convergence, the recapture ladder, seep oases; VAPOR_EMITTER_PLACEMENT_1 filed
89ef5813 File MOD_NAMING_CONSOLIDATION_AUDIT_1 for BENCH: owner asked for a full mod-naming/consolidation review with an ASCII relationship map.
ae21392d COLONY_VISIBILITY_BUILD_1: re-verified clean/deployed, block on live batch
22c43313 NINEFOLD_ENGINE_M0_1: state ledger + hooks CLEAN, block on voice redline
87331ff7 Ninefold: gate Ta'Baa launch credit on CanLaunch, not TryLaunch entry
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-07T02:09:23Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/codebase_health_last.json
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? design/Jawa/art/gods/busts/.gitignore
?? "design/Jawa/worldbuilding/lua suggestions/"
?? design/Jawa/worldbuilding/review/creature_art/
?? design/Jawa/worldbuilding/review/creature_register.fiftyone_export.json
?? design/Jawa/worldbuilding/review/deck/creature_deck.pptx
?? design/Jawa/worldbuilding/review/deck/creature_deck_manifest.json
?? design/Jawa/worldbuilding/review/furniture_art/
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260902_181509.xml
?? infrastructure/state/codebase_health_last.json.lock
?? infrastructure/state/facts/mlie_creature_defname_map_wave_a.json
?? research/RimMandrake/inspiration/map_injection_2026-09-06/p2_createprefab_export.xml
?? src/RimMandrake/LoadTracer/Assemblies/
```

