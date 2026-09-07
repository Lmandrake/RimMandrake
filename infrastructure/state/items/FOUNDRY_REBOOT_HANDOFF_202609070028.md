# FOUNDRY_REBOOT_HANDOFF_202609070028 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_20260906D`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`RM_BaseGraffiti`'s `placementMask=Any` looked like "accept any source" and
was the exact opposite: `FilthMaker.TerrainAcceptsFilth` reads a filth's
`placementMask` as a REQUIREMENT the terrain's own `filthAcceptanceMask`
must fully cover (`(terrainMask & placementMask) == placementMask`), and no
real `TerrainDef` declares all four `FilthSourceFlags` bits — so `Any` is
the one value guaranteed to place NOTHING, anywhere, ever. It shipped clean
(0/0 build, deployed, active in the owner's list) for a full week before a
live spree run proved the mark count stayed at zero. Fixed to `Unnatural`
(vanilla's own `Filth_Trash` uses it). **Anything else that places Filth in
this codebase — the 8 remaining sacred marks, mural bases, cant glyphs —
needs this same check before it ships**, not after: `grep -n
"placementMask" <the def>` and confirm it isn't `Any`. General form: a
clean build and an active mod entry are not evidence a mechanism fires;
only a live run that produces the artifact (a filth Thing, a fire, a
mark) is.

## What the owner should see

- **A near-miss on his live mod list, caught before it stuck.**
  `modset_builder.py --restore` was pointing at a dated 568-mod snapshot
  (2026-08-11) instead of the current 598-mod `ModsConfig.FULL.LATEST.xml` —
  restoring after a test-tier swap would have silently dropped 30 mods
  he's added since. Caught by comparing counts before trusting it, his live
  list was hand-corrected back to 598, and the tool itself fixed (now reads
  `FULL.LATEST.xml` directly, and its own safety check compares against the
  real pre-swap backup instead of the just-swapped live config, which is
  what let the bug through undetected before). No action needed from him —
  flagging because it touched his actual list, however briefly.
- **`PITCELL_PRISONER_BED_BRIDGE_GAP_1` (newly filed) is a scope call, not
  urgent**: Pit Cell's prisoner-intake gizmos can't be bridge-tested at all
  without a new companion tool (nothing can flag a bed `ForPrisoners` except
  an in-game click). Worth a ruling on whether that tool is worth building,
  or whether prisoner intake stays "proven only by a human playing" — his
  call, no rush.
- Two real, previously-unverified defects were found and fixed autonomously
  this wave (Oiled-pit ignite; the graffiti placementMask above) — both are
  bug fixes to already-ruled mechanics, not new design, so shipped without
  waiting for a ruling. Mentioned for awareness, not because either needs a
  decision.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `DEV_LOG_AUTOOPEN_SUPPRESS_1` — not touched this pass; git log shows
  `14701fa7` "Harmony prefix suppresses the dev-mode error-log auto-open,
  deployed" against this item, which reads as finished. Next action: verify
  the criteria in the item file are actually met and `rimflow close --sha
  14701fa7`, or say what's still short if something is.
- `GRAFFITI_FRAMEWORK_BUILD_1` — mechanism layer is now fully proven live
  (this pass): the absorbed vandal spree places marks correctly after the
  placementMask fix above; the viewer-reaction `ThoughtWorker` and the
  breach-bias Harmony hook are built and compile clean but still
  unexercised live (both need a real content def with
  `viewerReactionThought`/`breachLure` set, which is content, not
  mechanism). Next action: content authoring (8 more sacred marks, 3 mural
  tiers, 4 jests, taunts, 5 cant glyphs, ~34 art assets per spec §3) — held
  to the owner-voice boundary three prior passes already drew; do not
  write flavor text solo. Once even one real content def exists, live-prove
  the two remaining mechanisms the same way this pass proved the spree.
- `MACRO_GENERATOR_V0_1` — not touched this pass; git log shows `ef4db906`
  "chooser + plan + validator + gates + terrain painter, selftest 4/4,
  first comparator sheet" against this item, which reads as a working v0.
  Next action: read `infrastructure/state/items/MACRO_GENERATOR_V0_1.md`'s
  own verify/criteria sections against that commit and close if met, or say
  what's short.
- `MAPGEN_GL_SHEET_1` — not touched this pass; git log shows two commits
  (`2ef0cfe5` "7 of 8 emitted landforms proven applied in-game", `b28f6e2b`
  the gl_emit/--rotate work under it) — one of 8 landforms apparently still
  not proven applying. Next action: find which of the 8 is the holdout and
  either fix it or record why it's an accepted exception, then close.
- `MAPGEN_PAINTER_V1_1` — not touched this pass; git log shows `dafe7fb6`
  "organic masks, elevation->terrain bands, hydrology, selftest 5/5, 10-12
  terrains, perimeter/area 2.64-2.69 on all 8, v1 comparator sheet" against
  this item, which reads as complete against its own stated targets. Next
  action: confirm against the item's own verify section and close.

None of the five above were opened or advanced by this window this pass —
they were already `doing` when this session's visible context began (their
citing commits are all dated 2026-09-06 evening, before the work shown
above). Reporting them here rather than silently carrying them forward
uninspected.

## Traps learned

- **`FilthMaker.TerrainAcceptsFilth`'s `placementMask` is a requirement on
  the TERRAIN, not a permission on the FILTH** — see "the one thing to
  carry forward" above. `Any` (all 4 `FilthSourceFlags` bits) is backwards;
  vanilla real filth defs use one or two specific flags (`Terrain`,
  `Unnatural`).
- **`modset_builder.py --restore`'s own safety check compared the restore
  target against `CONFIG`, but by the time anyone calls `--restore` in
  normal use, `CONFIG` already holds whatever tiny `--tier ... --apply`
  just wrote** — comparing against your own just-made test tier can never
  catch anything. Fixed to compare against the newest
  `ModsConfig.before-tier-*.xml` backup instead, which is the actual
  pre-swap state.
- **`start_debug_game_ready` really will queue a second worldgen if called
  twice while the first is still initializing** — hit this directly (ran a
  throwaway status script that re-issued it), the second call timed out at
  30s exactly as the skill warns, and recovery was just patience + a fresh
  connection + `get_game_info`/`list_colonists` polling, not a restart.
- **`rimworld/select_pawn` only resolves player-controlled colonists** —
  confirmed directly: it refused a spawned hostile pawn by both `pawnId`
  and `pawnName` with "Could not find player-controlled colonist", and
  selecting a colonist did not reveal any additional pawn-context debug
  actions either (267 visible children under `Actions` before and after).
  Vanilla's `DebugToolsPawns.AddGuest(GuestStatus.Prisoner)` ("Add
  Prisoner") needs an existing `Building_Bed` with `ForPrisoners==true`
  already on the map or it silently does nothing (`success:true`,
  `logCount:0`) — and `ForPrisoners` has no reflective setter or debug-menu
  leaf anywhere on the bridge, gizmo-only. This is
  `PITCELL_PRISONER_BED_BRIDGE_GAP_1`.
- **`rimworld/step_game_ticks` caps at roughly 600 real ticks per call
  regardless of the requested count** (returns `status: "timedout"` with
  `advancedTicks` around 600), so proving anything that needs thousands of
  in-game ticks (a mental-break spree runs ~20,000+) means looping the call
  dozens of times, not one big request — budget accordingly, and run the
  loop in the background rather than blocking on it.
- Filed to `infrastructure/state/LESSONS_INBOX.md` in the usual one-line
  form; full detail lives in this handoff and the two closed items'
  commits.

## Closed since the last handoff (21)

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

## Filed and still open (61) — the next seat's queue

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

## Commits

```
c5e44c24 Graffiti: fix the absorbed vandal spree never placing a mark (placementMask=Any is backwards); add graffiti test tier
f89eac71 rimflow: close RIMMANDRAKE_PITS_BUILD_1 and MODSET_BUILDER_RESTORE_STALE_1 at abc1e7cd; spawn PITCELL_PRISONER_BED_BRIDGE_GAP_1
abc1e7cd Pits: fix dead Oiled ignite (Flammability 0), root-cause the prisoner-intake gap; modset_builder --restore no longer uses a stale mod-count snapshot
b3298eee BENCH_REBOOT_HANDOFF_202609070000: handoff written and checked — nine biome sheets ruled, droid program Foundry-ready, saves scrubbed, traps logged
06b8880a the_cracked_lands.md: biome sheet ratified — the flood, soil in the shade, cisterns, fliers feed here and nest in the desert, Moisture Farmers only, the roads; FISH_BY_BIOME_1 and SAND_SWIMMERS_MOD_1 filed
f74d7e27 sequence riders: freeze review → settlement rejigger → assignment sitting
f11ca284 file SETTLEMENT_REJIGGER_ROUND2_1 — settlements re-shifted to the frozen biomes, sequenced after the freeze review and before the assignment sitting
c215533f WORLD_RIVER_COLORS_1: per-vertex gradient along the river preferred over hard segments
8e06a11e file WORLD_RIVER_COLORS_1 — per-segment river colors and the slate-cyan propane lake on the world view
d6807c4b MODE: belt — owner stepping away, FOUNDRY runs the queue
ac911c58 GLOBAL_CLAUDE.md: handoff-at-end-of-queue doctrine, generalized to every session
34b021c2 Badlands sitting: Contagion widened to every rain-fed dayside high (sterilized on descent); half-plant tree art note; FUNGAL_SOIL_TRADE_1 and MOISTURE_FARM_TEMPLATES_1 filed; tree-ownership ticket gets its riders
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE
- Live `ModsConfig.xml`: 598 active mods, verified matching
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (restored
  correctly after two test-tier swaps this pass — see "the owner should
  see" above).

Uncommitted at wrap (everything else this session touched is committed and
pushed through `d99aba4a`):

```
 M infrastructure/state/LESSONS_INBOX.md         -- MINE, committing with this handoff
 M infrastructure/state/codebase_health_last.json -- NOT mine, was already dirty at session start
 M infrastructure/state/queue/BENCH.md            -- NOT mine, another window's concurrent activity
 M src/RimStarWars/BeastLairs/About/About.xml                              -- NOT mine, pre-existing
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml -- NOT mine, pre-existing
?? infrastructure/state/items/FOUNDRY_REBOOT_HANDOFF_202609070028.md  -- MINE, this file, committing with this handoff
?? Transient/graf_*.py, Transient/pits_*.py, Transient/*.log  -- MINE, throwaway bridge-driving scratch scripts, left untracked on purpose (Transient rule)
?? everything else under Transient/, design/Jawa/worldbuilding/review/, infrastructure/state/*.lock, src/RimMandrake/LoadTracer/Assemblies/, research/  -- NOT mine, pre-existing at session start
```

