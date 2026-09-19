# BENCH_REBOOT_HANDOFF_202609121722 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609121357`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->

**The canonical game changed today: `Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` is now THE start save** (canon.yml `planet.start_savegame`, `start_tile: 17007`). The owner flew The Utinni to Zeddo's Yard himself; the settlement there is "Zeddo's Salvage Yard"; the Five Founders are aboard; the world validates 21872/21872 against the frozen CSV; the sea-landmark cleanup (533 removed) is inside it. `CANONICAL_ASHKARR_2026-09-09.rws` is retired as canon — never load it as the world again, never delete it. Every FOUNDRY item that says "load canonical" now means the START save, and every world edit must be re-saved INTO it with the backup + stat discipline.


## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->

- **82% of the planet is still on donor/vanilla biome defs** (MEASURED live: 17,889 of 21,872 tiles, 23 defs — ExtremeDesert 3,969, Propane Lakes 2,531, Desert 2,390 …). `BIOME_OWNERSHIP_WAVE_1` authored the `RUT_` defs and closed without the tile switch; `BIOME_WORLD_SWITCH_WAVE_1` (FOUNDRY, bridge) is the repaint. It is a big edit to the START save — a deliberate, backed-up pass.
- The ship: 92×86 ring, 3,275 cells, **range 20 tiles** with 4 small thrusters (one BROKEN DOWN — the "Thruster breakdown" alert is real). He called it overly ambitious and declined a redesign today; my recommendation (collapse the courtyard, cut the dead top-right arc, thrusters on the outer hull) is in this session's transcript, not filed — he said no new items.
- Post-landing the colony map shows NWN Real Fog of War's dark sight-radius shading even though vanilla fog is 5,465/62,500 cells and `onlyOutsideColony=True` — noted on GRAVSHIP_LANDING_FOG_REVEAL_1, not fixed, not filed (his "no new items").
- Five sheet-verdict channels from the 09-10 review never landed (`SHEET_ORPHAN_CONSUMPTION_1`, FOUNDRY): 6 fauna cuts, 15 flora moves, 4 flora purges, the 118-row new-art commission ledger, 148 flora art:improve rows. Later sittings override the sheet, never the reverse.
- The FULL.LATEST modlist snapshot lags the live list (593 active now, incl. `mandrake.rm.gravshiplanding`, shokkweave, roaches); `modlist_swap.py --status` reads UNRECOGNISED. Someone should `--capture-full --apply` at a quiet moment — his call whether the live list is the one he wants captured.


## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->

- **`CAMPAIGN_STORY_SITTING_1`** (BENCH, needs owner) — filed, Phase A (the Fable GATHER into `design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md`) not started. Next action: background a Fable subagent with the item's Phase A brief (extract-only, forbidden to author), then serve the owner the gather before any cards.
- **`FASCINATING_WORLD_JUNK_1`** (FOUNDRY, design) — filed, nothing started. Phase 1 is a MEASURED census + contact sheet.
- **`BIOME_WORLD_SWITCH_WAVE_1`** (FOUNDRY, bridge) — filed with the census and def mapping; nothing repainted.
- **`UTINNI_WORLDMAP_FLIGHT_ICON_1`** (FOUNDRY) — filed; vanilla draws a pale blue dome; replacement must read as the ring hull.
- **`PLAYER_START_SITE_1`** — the start EXISTS (see carry-forward); still owed: the junkyard structure injection with a landing-footprint clearing (92×86 + 2) and the scenario's start pin. Build against the START save.
- **`OCULAR_OVERDRIVE_SITE_1`** — unblocked today (campaign function ruled: the Spire holds the Rakatan command codes, the only way into the war lab after the crater event; Archon is the Rakatan name for the Cathedral); handed to FOUNDRY for the landmark + dungeon build.
- Owner's remaining asks from this sitting were all filed; he asked for **no new items** before the account switch.


## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->

- `rimworld/load_game` never reports `programState`; `get_game_info` returns `status: game_loaded` with `programState: None` on a healthy loaded game. Do not wait on `Playing` — assert on `mapCount > 0` and a ticking/answering `ticksGame`.
- `jawa/set_pawn_identity` / `set_pawn_skill` / `pawn_traits` / `pawn_get` take `pawn`, not `pawnId`; `pawn_traits` takes `action` + `trait`; `jawa/inspect_string` takes `thingIds`; `jawa/destroy_batch` takes `rects` + `categories`, never ids; `jawa/list_things` has no name-contains filter. The client's declared-parameter check catches these — read its message, don't retry the same key.
- Gravship substructure fuses with any substructure it lands touching: a wreck's foundation became part of the ship (one connected component) and flew with it. Cutting a 1-cell seam (`set_terrain_layer removeTop` then `set_substructure_batch remove`) disconnects it; the remainder is left behind at launch.
- `GenStep_Fog` unfogs only the flood from `PlayerStartSpot`; a start spot inside a walled complex reveals one room. Fixed for arrival maps by `mandrake.rm.gravshiplanding` (postfix on `GenStep_GravshipMarker.Generate`, order 1700 > Fog 1500). Maps that already exist take the `ArriveExistingMap` path and log `0 -> 0` — that is correct, not a failure.
- FOUNDRY in belt mode commits every few seconds; `.git/index.lock` collisions are constant. Retry in a loop; a lock older than ~90 s with `pgrep -x git` empty is stale (`pgrep -f "git "` matches your own shell — never use it for this).
- The bridge's `world_tile_get` carries no lat/long; the planet CSVs do. `world_neighbors` takes `path`, not tiles — adjacency offline from lat/long was faster than finding the right tool.
- `ModsConfig.xml` is a single-line `<activeMods>` list — any grep on it dumps 600 ids onto the screen. Parse it, never grep it.


## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (2) — the next seat's queue

- `SHEET_ORPHAN_CONSUMPTION_1` — Consume the 5 orphaned verdict channels of the 2026-09-10 assignment sheets (fauna out x6, flora move x15, flora out x4, 118-row NEW-ART/DEF ledger, f
- `CAMPAIGN_STORY_SITTING_1` — The formal campaign-story pass: gather EVERY campaign-arc fragment from the earliest notes to today (dungeons and their purposes, the floating station

## Commits

```
5fddd399d Transient: ModsConfig + Player.log backups from the GravshipLanding restart
352723f00 CANONICAL START SAVEGAME registered: CANONICAL_ASHKARR_START_2026-09-12.rws (owner, 2026-09-12)
92b256a75 File CAMPAIGN_STORY_SITTING_1: the formal campaign-story pass (owner, 2026-09-12)
47e332615 rimflow: close GRAVSHIP_LANDING_FOG_REVEAL_1
19d212ce8 GRAVSHIP_LANDING_FOG_REVEAL_1: proven live at 17007 (62500 -> 5465 fogged), close notes
a4671ea2e File FASCINATING_WORLD_JUNK_1: the scav-flavoured wreck reskin programme (owner, 2026-09-12)
997dc73c3 MLIE_FAUNA_ABSORPTION_1: port Corinathoth, Dactillion, Dalgo (80 -> 77 remaining)
37182c7a7 rimflow: file 3 items from post-restart Player.log triage (GiddyUp wildBiomes duplicate, dead MegafaunaYield GR_* targets, ScarRoach/CathedralRoach missing textures) - all pre-existing, none caused by tonight's belt-mode work
3a608276a MLIE_FAUNA_ABSORPTION_1: port Cannok, Clodhopper, Convor (83 -> 80 remaining)
6e92224b4 RimMandrake: Gravship Landing Reveal — unfog the outdoors on gravship-arrival maps before the landing picker (GRAVSHIP_LANDING_FOG_REVEAL_1)
95023f57f rimflow: sync ledger/queue views after belt-mode wave 4 (PATCH_MAYREQUIRE_OPERATION_SWEEP_1 closed)
4565d5796 Closes: PATCH_MAYREQUIRE_OPERATION_SWEEP_1
908ffd9df File GRAVSHIP_LANDING_FOG_REVEAL_1: landing picker fogged to one room (start-spot flood + NWN on non-colony maps)
c9bfed75a rimflow: sync ledger/queue views after belt-mode wave 3 (RUST_CATHEDRAL/PATCH_MAYREQUIRE filed+needs, code-review mark-clean wave)
c8b696e32 MLIE_FAUNA_ABSORPTION_1: port Boma, Borcatu, CanCell (86 -> 83 remaining)
2c9e20736 RUST_CATHEDRAL_MECHANICS_1: build §4 eel-fishing + §5 deep-drill response (6/6 sections offline-complete); file PATCH_MAYREQUIRE_OPERATION_SWEEP_1
8c4731b5e UTINNI_WORLDMAP_FLIGHT_ICON_1: record what the vanilla icon looks like in play (pale blue dome)
6749e2092 File UTINNI_WORLDMAP_FLIGHT_ICON_1: own the gravship's world-map flight icon (owner, 2026-09-12)
92b7ddef3 mark-clean: 4 fauna-wave files after diff-scoped review (BiomeCast_Ashkarr x2, RSW_Bantha_Thoughts, AnimalBiomeDuplicates_Fix)
1c0a5dcdb SHEET_ORPHAN_CONSUMPTION_1: addendum, 9 (not 5) confirmed already-built dupes in the 118-row ledger
af78ab87b Sea landmark cleanup (owner ruling 2026-09-12): shoreline-only, capped ~7% — 533 of 613 sea landmarks removed live, plan + replay script committed
1176b77a9 SHEET_ORPHAN_CONSUMPTION_1: audit table for 5 orphaned sheet-verdict channels, no writes
c88a886a9 RUST_CATHEDRAL_MECHANICS_1: build §3 living bolts (3/6 sections); file CATHEDRAL_ROACH_THINKTREE_GAP_1
678f0bdac File BIOME_WORLD_SWITCH_WAVE_1: 82% of tiles still on donor/vanilla biome defs (MEASURED live); the ownership wave closed on def authoring only
9808b920b INHABITED_AUGMENTATION_BUILD_1: wire 8.9 crashed_ship + 8.11 beast_lair (14/14 built+wired, 0/14 placed)
e62125946 MLIE_FAUNA_ABSORPTION_1: port Anooba, Beldon, Bolotaur (89 -> 86 remaining)
765cdb3f4 Gravship v2 'The Utinni' ring layout: owner's first size cut (booms removed), exported live 2026-09-12
ccdd2e1ba rimflow: sync ledger/queue views after belt-mode wave (VAPOR close, ASHFALL/NINEFOLD needs routing)
3469346f3 NINEFOLD_MISSING_EVENT_HOOKS_1: rimbridge-companion tools to trigger trade + launch
6e94a8845 ASHFALL_SPIRE_LANDMARK_1: author The Spire LandmarkDef, fixed-name RulePackDef, procedural icon
3af86502e Closes: VAPOR_PLACEMENT_CLEANUP_1
919d5c155 Plot sitting 2026-09-12: Ashfall campaign function ruled (the Key to the war lab), Archon name, Mechanoid-pass mechanics, sheet-orphan item
db113e1b7 FOUNDRY reboot handoff 202609121425: fill carry-forward/owner/half-done/traps sections; file 6 lessons from tonight's session
3f7352f6b rimflow: sync ledger/queue views after tonight's FOUNDRY session, bridge released
424f8c743 NINEFOLD_MISSING_EVENT_HOOKS_1: live-verify Sh'kaar and Ohm, 5/9 -> 7/9 gods live
ccff212c5 WEBWORK_KIT_BUILD_1: live-verify FrontCreep on a bordering-biome map, close SHOKKWEAVE_SOLE_SOURCE_1: live-verify web-cutting + nest raid; fix wake-on-approach bug
421ee05db Health hook cycle outputs
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-12T17:21:58Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M design/Jawa/fauna/BiomeCast_Ashkarr.xml
 M design/Jawa/fauna/cast_assignment.csv
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
 M infrastructure/state/facts/mlie_creature_defname_map_wave_c.json
 M infrastructure/state/facts/mlie_wave_c_worklist.json
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml
 M src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_MlieWaveC_Resources.xml
 M src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml
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
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dianoga.xml
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dragonsnake.xml
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Eopie.xml
?? src/RimStarWars/SWBestiary/Textures/swanimals/Dianoga/
?? src/RimStarWars/SWBestiary/Textures/swanimals/Dragonsnake/
?? src/RimStarWars/SWBestiary/Textures/swanimals/Eopie/
```

