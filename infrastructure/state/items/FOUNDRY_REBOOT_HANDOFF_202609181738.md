# FOUNDRY_REBOOT_HANDOFF_202609181738 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609180351`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Landing a worktree-agent branch into main reliably needs a fixed recipe, not
improvisation: `events.jsonl`/`queue/BENCH.md`/`queue/FOUNDRY.md` collide on
almost every merge because every worktree's background hooks keep touching
them. Recipe: `git checkout --ours` the pure-derived health files, `repair_torn_ledger.py
--apply --owner-said "<reasoning>"` for the ledger (never hand-edit it — a hook
refuses that), `render.py --overwrite-queues` for the queue views, then
`GIT_EDITOR=true git merge --continue` to finish — NOT a bare `git commit`,
because `block_blanket_git_stage.py` has no MERGE_HEAD exemption and git itself
refuses a pathspec-scoped commit mid-merge ("cannot do a partial commit during
a merge"). Full writeup: `[[merging-worktree-agent-branches]]` in my own memory,
and the underlying hook gap is already logged in `LESSONS_INBOX.md` line ~70.
Also: a background `Agent` that goes silent for 10+ minutes waiting on a slow
subprocess (a full 634-mod validate_patch sweep, a large background build) can
die with ZERO commits and no final notification — its worktree lock (pid-based)
can outlive the process itself as a stale `.git/worktrees/<name>/index.lock`;
`fuser <lockfile>` before `rm -f`, then `git worktree remove --force --force`
to reclaim it. Two of five agents in tonight's second wave died this way; their
completed work (where they'd gotten far enough to commit locally) was still
fully recoverable by merging the local commit sha directly from the dead
worktree's path — no push required, since worktrees share the same object store.

## What the owner should see

- Accepted his direct ruling in chat (not filed as a queue item first — executed live): all 14
  sweetline-tree art candidates landed as a `Graphic_Random` rotation, canopy grown to 10 cells
  wide (`visualSizeRange` 5.0~6.5 → 7.7~10.0, same spread ratio). Nobody has SEEN it in-world yet —
  bridge was held by BENCH the whole time this landed. Worth a look next time he's at a save with
  Ashkarr flora active.
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1`'s crash is confirmed to NOT be the bug it's named for (that
  one's fixed) — it's a downstream symptom of `MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` (SWBestiary
  creatures unresolved in the current live list). That sweep item is his call to prioritize, not
  something FOUNDRY should silently do around a restart.
- Two subagent processes in tonight's second BELT wave silently died mid-task (no crash reported,
  just went dark past their idle window) — see "the one thing to carry forward" above for how that
  was recovered. No data was lost, but it's worth knowing the failure mode exists if a future wave
  looks quieter than expected.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — doing; the original duplicate-key bug is fixed, but a
  live null-key ArgumentNullException persists (confirmed against a fresh full-list log tonight),
  caused by unresolved SW-creature PawnKindDef crossrefs; NEXT: fix `MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1`
  first, then re-check this item on the next full-list load.
- `GIZKA_NEWGAME_NRE_FIX_1` — doing/blocked; real crash site is vanilla `ReadingPolicyDatabase.GenerateStartingPolicies()`
  NREing on a ThingDef with null `thingClass`, not GizkaStowaway's own code (read in full, ruled
  out); NEXT: run an isolating bridge test (gizka alone re-activated, FlowWorks fix already live)
  to see if the missing-modExtension-discard pattern from `FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1`
  is the real culprit.
- `BAREHANDED_MELEE_FALLBACK_1` — doing/blocked, `needs: bridge`; 18/23 ranged-only kinds now fixed
  (0 remain of the ones a static pool-join can diagnose); NEXT: 5 kinds (Deepwater Leader/Specialist,
  DeepDesert Heavy, Wildsteam Specialist, Junkers Grunt) need a live per-pawn trait join via bridge
  spawn batches — a static join can't explain why they're bare with an affordable melee pool present.
- `VALIDATE_PATCH_FULL_TREE_SWEEP_1` — abandoned mid-triage; a background agent died silently
  waiting on a full 634-mod `validate_patch.py` sweep (no commits made, nothing lost); NEXT:
  re-dispatch with an instruction to write progress incrementally instead of waiting silently on
  one long background call, or just run the sweep directly and read the output rather than
  delegating it.

## Traps learned

- `rimflow note --owner-said "..."` stamps the event as OWNER authorship, not free text — don't use it for your own investigation notes (filed: LESSONS_INBOX).
- A `Monitor` tail loop must advance its own read offset or it re-emits the same matched lines forever (filed: LESSONS_INBOX).
- `Player.log` mtime can be hours stale relative to a fresh `bridge take` — check `stat`+`tasklist.exe` before trusting its content as current (filed: LESSONS_INBOX).
- A dead background agent's worktree `index.lock` can outlive its process; `fuser` then `git worktree remove --force --force` reclaims it, and local commits are still mergeable by sha with no push needed (filed: LESSONS_INBOX).
- The pathspec-commit hook has no MERGE_HEAD exemption; use `GIT_EDITOR=true git merge --continue`, never a bare `git commit`, to finish a real merge (see: LESSONS_INBOX line ~70, already recorded by a prior seat).

## Closed since the last handoff (16)

- `STALE_RENAME_GATE_SWEEP_1` — 6cc0a59d6875da58dca40db16b2754629125e255
- `ARTPIPE_FAILED_REQUEUE_1` — a6c7e0d6d20c152c911a6bf426cac1e5bf310143
- `MAYREQUIRE_OPERATION_INERT_SWEEP_1` — d1c62223c
- `SALVAGECLAIM_WALK_STALE_1` — 471ca3d844e87b249a1df9d09ff7802c048b75ce
- `MODCHECK_STATUS_ORPHANED_BY_RENAME_1` — b110a7a2d3fd5c21bed87024bf37d6401f194cde
- `NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1` — 611304868522158c6c2d77bdd22725b5515f95bd
- `CANYON_FLOOD_ERASES_CANALS_1` — e14c9cfedbe375883fdb8ce80112bfca3d4d74c1
- `GREENTIDE_FISH_ITEMS_FIX_1` — 0da141b42a410cb48823350a68d66343c630d822
- `ANOOBA_DRAWSIZE_FIX_1` — 1f1b8ab19e378298d5a5d88eeb1bc50775583a0e
- `ENVHAZARDS_DLL_REBUILD_OWED_1` — 60e2d841b092276cb75161490a0b43fe4c032d90
- `OUTERRIM_DROIDDEPOT_PATCH_GUARD_1` — 72995c875c0932fd9db9a5f866bee3cedf287e94
- `GL_EMIT_FLOATRANGE_GENERIC_DROP_1` — 3bf2e7078c95bf2e96f8a487763066eb0d3a0081
- `WRECKEDMACHINES_MOD_SETTINGS_1` — d9df2cabe29ff3d4b88ec38c4b2aaadf38e9ea2d
- `FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1` — 384fc2982
- `ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1` — 0d911632677a0f0f947ddc87c22050159f98d6bc
- `NURSERY_JUVENILES_CRASH_1` — 05974eeb4

## Filed and still open (5) — the next seat's queue

- `PYRELANDS_FLORA_LEAK_1` — Alpha Biomes flora spawns on Pyrelands past the grass-only eviction
- `PYRELANDS_WEATHER_SCAR_ART_1` — Pyrelands scar+weather art: ash rungs, filth legibility, Cinderfall drama
- `QUICKGRASS_VISUAL_SCALE_2X_1` — Double quickgrass on-screen size - scale only, no new art
- `BRIDGE_MAPGEN_STALE_FINALIZE_1` — world_tile_map_generate leaves the map rendering stale until map_commit finalize
- `WALK_FEATURE_KEY_1` — Walk model ruled: add a feature: key so per-feature walks are first-class; teach doctor.py the key

## Commits

```
5602b84ac Ledger: fresh live re-check confirms GiddyUp modlist theory, FlowWorks fixed
c9d9bdd56 Merge BAREHANDED_MELEE_FALLBACK_1: 3 more Geonosian kinds fixed
91290c8eb Sync health-dashboard derived state
0d3cb9759 ledger: BAREHANDED_MELEE_FALLBACK_1 claim/start/note/needs=bridge/block
6a9886d86 Merge GIZKA_NEWGAME_NRE_FIX_1: investigation, left doing, no blind fix
a3afc30a7 BAREHANDED_MELEE_FALLBACK_1: melee fallback for the last 3 Geonosian kinds
c89c93118 Ledger: claim/start/note GIZKA_NEWGAME_NRE_FIX_1 - left doing, don't fix blind
118f64f66 Sync health/queue derived state after stash-pop conflict
3d4cd37c4 Close NURSERY_JUVENILES_CRASH_1: fix confirmed correct and live, 09-17 recurrence traced to unrelated cause
fa290b0f5 Worldmap pass file 1: the_one_map.md map-location sections rewritten to reality (owner ruling)
1fe5e9e0a ledger: close BIOMES_CAVERNS_DEEPSCAN_1 (recon delivered; keep-for-now stands)
a258e38cb Walk model ruled (feature: key -> WALK_FEATURE_KEY_1); Biomes! deepscan recorded
9bbd6fc7b Regenerate queue views
002542136 Modlist sitting 2026-09-18: four deferred cards ruled, cards item closed
539448f8e Merge: land all 14 sweetline tree variants as a Graphic_Random rotation
7c50af47e Sync ledger/health derived state after stash-pop conflict
ccf00b248 Merge FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1: confirm already fixed
f9abee8c8 Merge GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: re-verify already-fixed, left doing
62676109a rimflow: claim/start/close FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1
384fc2982 FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1: verify already-fixed deploy gap
... 49 more: git log --oneline d946c8522..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING (RimWorldWin64 PID 22440, measured via tasklist.exe just now, ~17.8GB — full 636-mod list)
- recorded  : UP (confirmed via a fresh "Bridge token:" line in Player.log, load completed cleanly)
- Bridge    : held by BENCH since 17:09:35Z, idle 20 min, for "Owner-ordered restart: enable 3
              custom mods, full-list reload, dump refresh" — FOUNDRY does not hold bridge, never took
              it back after BENCH's take superseded an earlier FOUNDRY hold this session
- ⚠️ ModsConfig warning seen repeatedly tonight: the live list is neither the stored FULL nor
  MINIMAL snapshot (BENCH added 3 custom mods on top of FULL) — if that's deliberate, someone still
  owes `modlist_swap.py --capture-full --apply` to make it the new recognized baseline; not FOUNDRY's
  call to make unilaterally since it wasn't this seat's restart

Uncommitted files, each line now says whose it is (yours, the other seat's, a subagent's):

```
?? defs.sqlite   BENCH — dump refresh from tonight's owner-ordered restart
?? deployed/config/ModsConfig.before-tier-oracle.xml   BENCH — tier-testing snapshots from tonight's restart, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   BENCH — tier-testing snapshots from tonight's restart, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   BENCH — tier-testing snapshots from tonight's restart, not mine
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_palemoss_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_paletree_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon — old run log predating this session, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow — concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Pufferpig.xml   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Qormot.xml   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Ronto.xml   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swanimals/Pufferpig/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swanimals/Qormot/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swanimals/Ronto/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swresource/Meat_Ronto/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
```

