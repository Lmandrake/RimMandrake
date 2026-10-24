# FOUNDRY_HANDOFF_202610241805 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610240741`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

Order (owner, 2026-10-24): "you do not have bridge. Wake foundry. You have two subagents. Keep the art pipeline going. Focus in ingesting the GPT assessments and filing tickets... Stay a light orchestrator all night." — it ended when he wrote again (he is at keyboard); a successor applies nothing of it. What carries: everything he decided tonight by card or words is enacted or filed, and the biggest hazard is DIRTY CODE: a long fix/review chain (enact.py, art_sheet.py, art_eval runner/shadow, deploy_custom_mods.py, SWB move defs, tuning) left files DIRTY on purpose because a fixer cannot clean its own code; clearing them needs fresh-eyes full-file reviews, not more fixes. (filed: ENACT_*_UNREVIEWED, SWB_MOVE_VET_UNREVIEWED, DEPLOY_GUARD_VET_UNREVIEWED, ARTEVAL_TUNING_VET_UNREVIEWED)

## What the owner should see

- Water round 3 sheet needs his picks: Twilight panes v3 (quarter size, 4x number, ~4.5 hexes lit) and Chill abyss (face value 22, films-off row is the halo fix): `D:\Luke\dev\RimMandrake\Transient\world_water_review_r3_2026-10-24.html` (served http://localhost:38159/?t=dnM1qDL7kHWE3PXEdCUM-Q; server PID 1374876 may be gone: re-serve with serve_gated).
- Excretor side view ('more alien' is his call): `Transient/biome_ffar/art_eval_shadow_fauna_excretor_r1_00_sheet_2026-10-24.html` (gitignored, ext4 clone only).
- Unspoken-for: TunnelSnake C held; its 3 SWBestiary pictures are owner-kept and need his words before the RSW copy is removed; Fuzzrunner variant C held (enact skips an identical east); SandStalker waits on the Skarnix redo.
- The three Durrok/Vexxiss/Bloodlurk style size fixes were done by resample/GPT-redraw+box, not pure GPT as he asked (he may object): see gpt_shrink notes.
- GPT conflicts for his digest: GPT_CONFLICTS_FOR_OWNER_DIGEST (five; the visitor one is decided: INDETERMINATE for need/mood/job).
- Nine orphan game mod folders to delete by hand (GAME_ORPHAN_MODS_DELETE_BY_HAND); 21 mods drift (GAME_DRIFT_DEPLOY_OLDER_COMMITS). The deployed work needs a game restart; the live mod list is still the flowworks swap.

## What is half-done, and where it stops

- `WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP` — Grey Sea, Twilight deep, Scald faces installed; Chill and Twilight panes wait; NEXT: collect his picks on the r3 sheet, install the picked Chill/Twilight faces, then build SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT.
- `world look program (WORLD_* tickets, design/Jawa/worldbuilding/world_look_program_2026-10-24.md)` — decals pipeline, big mountains (may bleed into neighbours), soft hex edges default, Contagion weeping look (look only), rivers/roads with water; NEXT: claim MOUNTAINS_REDRAW_BIG_NOT_LITTLE_PICS and WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE offline.
- `RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH` — filed for BENCH (FlowWorks); NEXT: BENCH to claim it.
- `ENACT_ALIAS_KEEP_FIX_BLOCKS_NEWER_PICK`, `ENACT_KEPT_CONFLICT_FIX_PARTIAL_PLAN`, `ENACT_APPLY_REFUSED_HARDEN_PARTIAL_PICK`, `ENACT_VARIANT_TICK_FIX_MOVED_LANE` — enact.py all-or-nothing is in, these remain by harm order; NEXT: fix ALIAS_KEEP first, then spawn a fresh reviewer for enact.py (still DIRTY).
- `SWB_BIOMESTEAM_MIGRATE_AS_ONE_FOLDER` — 57 Biomes-team ports move as one folder (needs a C# type list widening + rebuild); also Vozzik/Zhakka C#, SandLion/Vozzik twins, 8 sea-beast + TunnelSnake dedupes; NEXT: design the one-folder migration as a builder item with a C# rebuild.
- `FUNGALWEEVIL_LABEL_JUDGE_PROPOSES_NEW` — Grellik (canon name) needs a new label; NEXT: spawn a judge agent to propose it.
- Reviews owed (DIRTY): enact.py+stale_lane selftest, art_sheet.py, art_eval runner/shadow/fauna_spec, fauna_drive/round_series, world_face_variants.py, deploy_custom_mods.py, art_eval tuning files, SWB move XMLs, RM_CauldronFauna.xml; NEXT: one fresh Opus full-file review per cluster, edits only for severe defects.
- `ARTEVAL_JUDGE_LIVE_HEAD_TO_HEAD`, `ART_EVAL_SIZEJUMP_TUNE_OVERBLOCK` — size-jump/confidence floors built but OFF because every setting accepts art he purged; NEXT: design head-to-head judging that can be measured on the owner-labelled set.
- `ART_SERIES_WIRE_STOP_AND_CANCEL` — manual `fauna_drive stop` exists; auto-stop when he keeps art is not built; NEXT: build the rule.
- `ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS` — round-1 verdicts on bollard-damaged creatures need re-judging; NEXT: re-judge Crustweevil/Dustflutter/Fuzzrunner/Surrik/Peeper round-1 renders (series are STOPPED; he kept or picked their art).
- Stale sheets: owner_escalations_leaningscrub_2 (3 rows), cauldron (2 rows); NEXT: rebuild both sheet records.
- `GPT biome review follow-up` — 31 tickets filed and description rewrites applied (all 6 biomes); NEXT: confirm roster-gap design tickets (Zeer browse source, Cauldron trunk deposits, Bark warden) are claimed by a builder.
- Carried from earlier handoffs: `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` (update-on-change engine, proposal B), `ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP`, `RIMPULSE_*`, `HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY`; NEXT: reread FOUNDRY_HANDOFF_202610240741 pointers.

## Traps learned

- A fixer cannot mark its own code clean, so every fix spawns a review that finds a new defect: break the chain by letting reviewers edit only for severe defects and filing the rest (filed: lessons).
- Workers copied unrelated images from the shared ~/.codex cache and the wrapper recorded success (bollard, pipe-flange, belt-pack); the guard is now resize-robust but misses mirrored/cropped copies (see: FOREIGN_GUARD_WIDEN_MIRROR_CROP).
- Enact trusted old slot keys and old keeps: refusals now name the pick, all-or-nothing per pick (filed: lessons 20261024T112527Z, T135551Z).
- The owner answers sheets by PICKING; shadow ingest read zero rows until tuning (f4436e4adc) (filed: SHADOW_INGEST_HARVEST_OWNER_PICKS).
- Sheet prereview fingerprints track paths not pixels, so a rebuild looks unchanged (filed: lessons 20261024T142412Z).
- `art.py purge` deletes the stored files: back up first (filed: lessons purge-deletes-stored-files).
- Shared clone: one helper's art-ledger commit can sweep another's events before their PNGs; the art guard then refuses the push until they commit (filed: lessons).
- zsh: `git show $c:path` needs `"${c}:path"` (filed: lessons).

## Commits

```
73f129d50b ledger+lessons: by-card deploy run 2026-10-24 (compose biomes+SWBestiary --prune, UtinniPatches, AtmosphericBase, Armoury), file GAME_DRIFT_DEPLOY_OLDER_COMMITS, two deploy lessons
cfb6f38203 DUG_WATER_FILL_FIX_NO_CANAL_DEBIT + DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM + DISABLED_LIQUID_FIX_LIMITLESS_SOURCE: GPT review batch A liquid-sim fixes
112e665d34 RAIL_LADDER_REDRAW_FAT_RUNG_FENCE: rail ladder (lowered+raised) = approved v5 wood geometry recoloured to the ground ladder's pale wood (owner: 'The paler ladder is much better and is thick enough'); palette/alpha/iron/shading checks + can-fails; pinned BEFORE; portable E/W out PNGs
3017ad0438 LADDER_PORTABLE_DECIDE_EAST_WEST_FACING: portable ladder E/W = ground ladder raised 30 deg (sheet panel 3), west mirrors east
63b567595a deploy planner: repo_deleted uses --no-renames, so a file renamed or moved in a commit (UtinniPatches RUT_Wasteland.xml -> RUT_Wastes.xml, Shyrack _44 -> _4) is pruned as a repo delete instead of kept as a hand edit; selftest case
1abdb2974a BENCH wake: commit stranded seat-clone state (ledger shard, conversation, modcheck/northstar results, art_eval runs)
99ccdb51ef ledger: pipeline tuning f4436e4adc — close 6 fixed art-eval items, file ARTEVAL_TUNING_VET_UNREVIEWED + ARTEVAL_JUDGE_LIVE_HEAD_TO_HEAD, SIZEJUMP not enabled note
f4436e4adc ARTEVAL_TUNING: pipeline tuning from owner picks (canvas gate, picks harvest, round dedupe, stopped skip, resumable regress)
1626414e68 COMPOSE_PLAN_FIX_COMMITTED_DELETES: compose plan and def guard map game-only Biomes/<key>/ paths back to the source folder's git history, so a committed source delete (RM_TetchikJar.xml) is pruned as stale instead of kept as a hand edit; selftest_deploy_compose_deleted
81a928047a ledger: close EXCRETOR_PICTURE_ASK_KEPT_OR_OWN by card (fae3d5a5ba); batch 6 notes on SWB_INVENTED_MIGRATE_TWENTY_LEFT + SWB_MOVE_VET_UNREVIEWED; lesson borrowed-picture-own-slot-redraw
fae3d5a5ba SWB_INVENTED_MIGRATE_TWENTY_LEFT batch 6: excretor redrawn by card and moved to RM tier as RM_Excretor
0acc077a02 ledger: sha correction notes (guard commit rebased to b808af1de7)
8d1852e7b9 ledger: close DEPLOY_PLANNER_FIX_CRASH_ON_DELETED + SWB_BIOMES_DEPLOY_GUARD_DUPLICATE_DEFS; file DEPLOY_GUARD_VET_UNREVIEWED, GAME_ORPHAN_MODS_DELETE_BY_HAND, COMPOSE_PLAN_FIX_COMMITTED_DELETES; lessons git-ls-files-deleted-misses-git-rm, deploy-guard-scope-not-live-modsconfig
b808af1de7 SWB_BIOMES_DEPLOY_GUARD_DUPLICATE_DEFS: planner def guard refuses an --apply that leaves the game copy with a def defined twice, a moved def's old name live beside its alias target, or a moved def with no home
d78e91a908 BENCH handoff 2026-10-24 17:10: FlowWorks owner review enacted in part; art/hose/live queues stopped at committed boundaries
62f1062aca conversations: catch-up 22 record(s)
462ccd05f2 ledger: round-3 owner words on sea faces, Twilight panes, Chill abyss (OWNER shard)
55a843cccf code review: mark world water generator, biome_worldfaces guard and 3 RM sea defs clean (reviewed diff since last clean mark)
fb078d7b36 WORLD_SEA_FACES_INSTALL_PICKED_LOOKS: install confirmed sea faces + round-3 water sheet
d862a8b300 lesson: art guard - re-install a newly added texture through the ledger
... 226 more: git log --oneline e6f46b1e50..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/all_bridge_art_sheet_2026-10-21.html   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M Transient/biome_ffar/modern_pump_sprinkler.subjects.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M Transient/biome_ffar/modern_pump_sprinkler_sheet_2026-10-23.html   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M conversations/2026-10-23-2333-b64adee4.md   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M deployed/config/ModsConfig.before-tier-flowworks.xml   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M infrastructure/state/art/sheets/art_eval_shadow_gptredo_02_sheet_2026-10-24.snapshot.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M infrastructure/state/art_eval/regen_rounds.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M infrastructure/state/art_eval/runs/owner_escalations_contagion_20261024/shadow_build.log   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
 M infrastructure/state/ledger/events/OWNER.jsonl   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_cauldron_r2_00_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_cauldron_r2_01_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_cauldron_r2_02_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_contagion_r2_00_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_contagion_r2_01_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_contagion_r2_02_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_contagion_r2_03_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_contagion_r2_04_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_leaningscrub_r2_00_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_leaningscrub_r2_01_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
?? Transient/biome_ffar/art_eval_shadow_fauna_leaningscrub_r2_02_sheet_2026-10-24.decisions.json   (generated / other agents' Transient; tracked bits committed in 797c503a4c)
... 221 more uncommitted paths (by top-level dir: Transient 201, infrastructure 13, src 4, conversations 2, deployed 1): git status --short
```

