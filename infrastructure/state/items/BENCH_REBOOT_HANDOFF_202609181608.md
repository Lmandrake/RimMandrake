# BENCH_REBOOT_HANDOFF_202609181608 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609180533`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔴 **A map made by `jawa/world_tile_map_generate` LIES VISUALLY until `jawa/map_commit
{redraw:true, full:true}` runs** — RegionAndRoomUpdater comes out of mapgen disabled and draw
meshes never invalidate, so destroyed plants and converted terrain keep rendering as if alive.
It cost half this sitting: the owner watched a fire "not consume vegetation" while 99.2% of
fire-visited cells were measurably bare, and a direct ash-paint test showed grass over 2 real
plants. Any past VISUAL verdict from a bridge-generated map without a map_commit first is
suspect. Fix owed: `BRIDGE_MAPGEN_STALE_FINALIZE_1`.

Second, permanent numbers: wild plant desired cover per cell = `min(plantDensity × fertility²,
1)` — fertility multiplies in TWICE — and **Map Designer (zylle.mapdesigner) caps any XML
plantDensity above 1.0 at startup**, folding the ratio into wildPlantRegrowDays (bisected on
add-one-mod loads; GL core and BiomeTransitions cleared). Pyrelands runs density 16 (owner-
approved ~96% cover), asserted by RM_PyrelandsDensityEnforcer.cs, which runs after Map Designer
and wins — confirmed on the full 634 list at tonight's close.

## What the owner should see

Nothing owed his eyes — he sat the whole session and every ruling landed live: plantDensity 16
approved on-screen; ladder pacing (one fire → deep ash) ruled KEEP AS IS; ash-scar art
commissioned; Cinderfall ruled "weak little puffs… very unimpressive" (on the art item); Black
Rain darkening approved untouched; quickgrass growth-stage art approved and its item closed;
grass 2× size ordered as `QUICKGRASS_VISUAL_SCALE_2X_1`. His game is back on the full 634 list
(gizka still deactivated per the 05:33 handoff), campaign save untouched.

## What is half-done, and where it stops

- `BRIDGE_MAPGEN_STALE_FINALIZE_1` -- filed; NEXT: make world_tile_map_generate run map_commit's
  finalize (enable updater, RebuildAllRegionsAndRooms, RegenerateEverythingNow) before returning.
- `PYRELANDS_FLORA_LEAK_1` -- filed (AB_SessileMechanoid ×105 + AB_GiantStikehr ×24 measured on a
  27-mod Pyrelands map); NEXT: pick the enforcement route — runtime wild-plant filter for the
  biome vs def patches on intruders — and prove it on a minimal-list quicktest.
- `PYRELANDS_WEATHER_SCAR_ART_1` -- filed with four owner verdicts inside; NEXT: commission the
  four ash-rung terrain textures (do NOT touch Black Rain's sky curve — approved as-is).
- `QUICKGRASS_VISUAL_SCALE_2X_1` -- filed on his verbatim order; NEXT: visualSizeRange 0.4~0.7 →
  0.8~1.4 in Quickgrass.xml and verify all three growth-stage graphics scale with it.

## Traps learned

- Wild-plant coverage math: desired = min(density × fertility², 1), fertility counts TWICE;
  `wildPlantsCareAboutLocalFertility=false` makes the budget whole-map/uniform (filed: LESSONS_INBOX).
- Bridge-generated maps render stale — phantom plants/terrain until map_commit (filed:
  LESSONS_INBOX; fix: BRIDGE_MAPGEN_STALE_FINALIZE_1).
- World view can wedge: `jawa/world_view show:false` refuses forever (wantedMode Planet
  reasserts); clear_selection/select_pawn/jump/main-tab all fail; save+reload is the reset that
  works (filed: LESSONS_INBOX).
- A generated settlement map's defenders include TURRETS, and downed/dead colonists un-home the
  map so running time culls it — two maps lost in one sitting (filed: LESSONS_INBOX; memory:
  generated-map-culled-unless-home).
- One bad path in a multi-file `git add` drops EVERY file and the commit then fails loudly —
  recurred tonight on a never-created png (see: memory git-add-never-suppress-stderr).

## Closed since the last handoff (1)

- `QUICKGRASS_GROWTH_STAGES_1` — closed at 1688d9a2a on live verification: armed log line, three
  stages seen on-screen, owner: "I like the growth maturation artwork otherwise". (The skeleton's
  prefill missed it — it was FOUNDRY's item, closed by BENCH under prove-it-close-it.)

## Filed and still open (4) — the next seat's queue

- `PYRELANDS_FLORA_LEAK_1` — Alpha Biomes flora spawns on Pyrelands past the grass-only eviction
- `PYRELANDS_WEATHER_SCAR_ART_1` — Pyrelands scar+weather art: ash rungs, filth legibility, Cinderfall drama
- `BRIDGE_MAPGEN_STALE_FINALIZE_1` — world_tile_map_generate leaves the map rendering stale
- `QUICKGRASS_VISUAL_SCALE_2X_1` — double quickgrass on-screen size, scale only

## Commits

```
af501e429 Transient: Pyrelands review session evidence (logs + review crops)
ee128ae38 Sync artpipe daemon + health-dashboard derived state
124ea48a4 Repair stash-pop conflict: torn ledger markers + regenerate queue views
773c70a5d Close 5 FOUNDRY items whose fixes had already landed, never closed
0eb6ac549 ledger sync: Pyrelands review session - 4 items filed, growth stages closed
a372e1d94 Pyrelands: name the density rewriter - Map Designer, bisected live
e244ffab8 Repair stash-pop conflict: torn ledger markers + regenerate queue views
d9f79c270 rimflow: claim/start/close SALVAGECLAIM_WALK_STALE_1
471ca3d84 SALVAGECLAIM_WALK_STALE_1: verify already fixed, closing DONE
38ab02b75 rimflow: claim/start/close MAYREQUIRE_OPERATION_INERT_SWEEP_1
98879ae5b MAYREQUIRE_OPERATION_INERT_SWEEP_1: item file, closing
ec4c2b77b Merge remote-tracking branch 'origin/main' into worktree-agent-a9b8fbe8e63d07827
3d5353719 Merge ARTPIPE_FAILED_REQUEUE_1: clear the failed/ art-job pile
d7e2a95a4 Merge remote-tracking branch 'origin/main' into worktree-agent-a9b8fbe8e63d07827
96a2efd05 DIRTY_CODE_REVIEW_LOOP_RESTART_16: wave, 7 files reviewed, 0 bugs
71e9bf42d Merge remote-tracking branch 'origin/main' into worktree-agent-a9b8fbe8e63d07827
9fdfe8813 Repair merge/stash conflict: torn ledger markers + regenerate queue views
2f2c983bc Merge STALE_RENAME_GATE_SWEEP_1: finish sweep of dead rename-gate citations
d1c62223c MAYREQUIRE_OPERATION_INERT_SWEEP_1: real FindMod gates on 10 more inert MayRequire-on-Operation patches
c4197bd90 rimflow: close ARTPIPE_FAILED_REQUEUE_1 at a6c7e0d6d
... 24 more: git log --oneline 748f6c36b..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-18T14:44:39Z

Uncommitted (replace each not this session's with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   health publisher auto-rebuild (any window's prune/list triggers it) — not in-flight work
 M Transient/codebase_health.json   health publisher auto-rebuild (any window's prune/list triggers it) — not in-flight work
 M Transient/codebase_health_artifact.html   health publisher auto-rebuild (any window's prune/list triggers it) — not in-flight work
 M infrastructure/dashboards/hub/data/health.json   health publisher auto-rebuild (any window's prune/list triggers it) — not in-flight work
 M infrastructure/state/codebase_health_last.json   health publisher auto-rebuild (any window's prune/list triggers it) — not in-flight work
?? defs.sqlite   def-dump tooling scratch — not this session's
?? deployed/config/ModsConfig.before-tier-oracle.xml   FOUNDRY modcheck tier-swap backups — not this session's
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   FOUNDRY modcheck tier-swap backups — not this session's
?? deployed/config/ModsConfig.before-tier-warlab.xml   FOUNDRY modcheck tier-swap backups — not this session's
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_palemoss_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_paletree_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artist daemon (no-LLM tile) — its queue/output, do not touch
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency temp — safe to ignore
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   old Cherry Picker preswap backup — not this session's
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Pufferpig.xml   another window's bestiary art wave — mid-flight, leave alone
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Qormot.xml   another window's bestiary art wave — mid-flight, leave alone
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Ronto.xml   another window's bestiary art wave — mid-flight, leave alone
?? src/RimStarWars/SWBestiary/Textures/swanimals/Pufferpig/   another window's bestiary art wave — mid-flight, leave alone
?? src/RimStarWars/SWBestiary/Textures/swanimals/Qormot/   another window's bestiary art wave — mid-flight, leave alone
?? src/RimStarWars/SWBestiary/Textures/swanimals/Ronto/   another window's bestiary art wave — mid-flight, leave alone
?? src/RimStarWars/SWBestiary/Textures/swresource/Meat_Ronto/   another window's bestiary art wave — mid-flight, leave alone
```

