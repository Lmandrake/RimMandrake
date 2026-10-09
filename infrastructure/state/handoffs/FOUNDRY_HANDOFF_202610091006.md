# FOUNDRY_HANDOFF_202610091006 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610090438`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Landing is the hazard now: ~45 helpers landed by plumbing, so the shared clone drifted and the OLD `land.sh` once replayed someone else's HEAD onto origin. Use only `src/RimMandrake/Utils/land.sh <sha> <paths>` or `-m "<msg>" <paths>` (`LAND_REPO=<clone>` from a private clone); never `git reset --hard` (hook-blocked); the clone was just reconciled to origin/main (0 ahead, 0 behind) and the backup of its stale files is `/home/mandrake/.seat-tmp/foundry_tree_backup_20261009_0305/modified.tar` (filed: lessons 20261009T100707Z-FOUNDRY-land-sh-old-replayed-shared-head).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Two things only he can unblock:** (1) the venomvine / Cistrel / Nubrith art: the finished own renders cannot replace his kept pictures until he types one sentence (or rules keep on a sheet); a card click is refused by the art ledger; the sheet `D:\Luke\dev\RimMandrake\Transient\own_render_keep_sheet_2026-10-09.html` is built but the serve gate refuses it (it is a biome-sheet gate). (2) `SCALD_GALLERY_SCHEMATIC_UNLOCK_1`: he answered *"Need a different tech to find. This makes no sense."*; the gallery needs a different reward and a re-ask with candidates.
- **34 card drafts, sets 2-9 unasked:** `D:\Luke\dev\RimMandrake\Transient\morning_cards_20261009.md` (set 1 asked and answered; sets need the `date` line added).
- **Rulings taken by card tonight (all recorded as notes):** forced launch always available; Illisk many bodies, near-immune to non-blast, common; vexxith Harmony in Cauldron + keep strong; gloomcast followers; Peakstorm overlay; middens; site B cut; 4 venomvine forms; waste run one quest, 5 branches, core is waste only; recycling lands on the Homestead; shade study per biome via vanilla research; salvage crew trades; dhuvvox stays a pawn; all 7 Long Shade extras; Joining Water standalone; Leachmoss B settled.
- **Provisional numbers nobody ruled on:** every new feature (all marked PROVISIONAL), e.g. Illisk non-blast scale 4%, tear-free hull hit 30% max HP, Peakstorm dust 2400/300 ticks.
- **Sitting 2 FAILS stand on the ledger** (dunes tint, weeper, jawa tow, joining water): all four were then fixed and PASSED or re-diagnosed in sitting 3 except the Jawa tow (fixed in source, unverified).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `STILLSAND_NATIVE_CRASH_LIVECHECK_1` — passed once (12,084 ticks); NEXT: run the optional A/B (old DLL, sun pathing off) in the next sitting to prove the cause, not only the fix.
- `LONGSHADE_JAWATOW_LIVECHECK_1` — Peaceful-to-Combat fix landed `3f5ad1125`, not deployed; NEXT: deploy LongShade, run the scene with `S.run(5)` before each dry run, then `rimflow verify`.
- `LONGSHADE_STAMPEDE_LIVECHECK_1` — forced fire works, toggle-off control unproven; NEXT: re-run with the setting off and no stampede already running.
- `NINEFAULTS_RITE_START_RECHECK_1`, `THERETURN_RITE_START_RECHECK_1` — filed, unrun; NEXT: run `ritual_start` on a throwaway map.
- `SETTINGS_SCREEN_KIT_1` — Core + Drawer built, FlowWorks linked; NEXT: wire a FlowWorks screen to `SettingsKitDrawer.Draw` and prove reset buttons in game.
- `HARMONY_PATCH_RESILIENCE_1` — ~45 mods converted; NEXT: add `BeforeExpose/AfterExpose` to the ~13 `[PatchFeature]` mods that lack them, then the owed live criteria.
- `CREATURE_BEHAVIORS_SETTINGS_SCREEN_1`, `ENVHAZARDS_SETTINGS_SCREEN_1` — need a design pass and his eyes; NEXT: adopt the kit once he sees the FlowWorks screen.
- Remaining ~240 acceptance criteria (572 owed at 21:00): NEXT: `rimflow next --acceptance --seat FOUNDRY`, then the plan `Transient/belt_acceptance_plan_20261009.md` and tier `acc_20261009c`.
- Game: UP on tier acc_20261009c (67 mods); NEXT: `modset_builder.py --restore` after killing the game by PID when he wants his full list back.
- Local-only leftovers: untracked `src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll.srchash` collides with the tracked file; NEXT: delete it (it describes no committed DLL).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Old `land.sh` replayed the shared HEAD onto origin (filed: lessons 20261009T100707Z-FOUNDRY-land-sh-old-replayed-shared-head)
- A composed member's packageId does not exist at runtime, so MayRequire on it never loads; the CLAUDE.md '74 inert Operation guards' claim measured 0 (filed: lessons 20261009T100707Z-FOUNDRY-composed-mod-member-e-g-mandrake)
- `IncidentWorker.CanFireNow` caches per tick (filed: lessons 20261009T100707Z-FOUNDRY-incidentworker-canfirenow-caches-its-result-per)
- A native Burst crash is not the last sound logged; free native arrays after 60 ticks (filed: lessons 20261009T100707Z-FOUNDRY-native-burst-job-crash-with-no)
- Rite behaviours without `<roles />` never start; `git reset --hard` is hook-blocked (filed: lessons 20261009T100708Z-FOUNDRY-ritualbehaviordef-without-roles-cannot-start-from)
- The art ledger keeps owner-kept shas sha-wide and accepts only a sheet ruling naming the incoming sha or his typed words; a card click is refused (see: Transient/belt_art_enact_20261009.md)
- Gate-stamped serve: `serve_gated.py` refuses any non-biome sheet (see: Transient/own_render_keep_sheet_2026-10-09.html task log)

## Commits

```
cf93cbcd1 Validators: LongShade tow gate follows the compose manifest; dump selftest skips defs changed after capture
ceddedac7 Digest: Sketto lock gate
e6dc1c3b8 Sketto plate v3 east filed (legs line); S/N lock gate refuses at re-pose cover
68169c584 Swarmling green v3 east/north rows after v2 size rejects
59b411efb Digest: morning contact image
4c36fd2af Morning art outcomes 2026-10-09: notes and contact image
234a4abeb Digest: conflict triage pointer
b6096b058 Art scripts re-review: ingest.py marked clean; enact conflict triage for the morning
c272dca94 Stale-letter guard: exempt letters whose click-time snapshot has identical shas (carriedFrom-aware); others stay CONFLICT
0ad084438 Digest: stale-letter audit
1e5260368 Stale-letter ingest audit: 28 spurious rejected events on 10 redo rows, no wrong rulings/installs
ab59e3086 Code review: enact, ingest, serve_gated marked clean
ab6bed31a enact/ingest: refuse stale-letter rows (CONFLICT), rejections from the ruled snapshot, no re-install over a later same-row keep, clear_followed survives a racing save
59400daf1 LongShade Jawa tow: cause trace and revised live scene (CanFireNow per-tick cache; Peaceful group)
3f5ad1125 LongShade: Jawa return tow asks Peaceful but 7 of 8 RUT_Jawa_* factions have none; fall back to Combat, skip factions with neither Sitting 3 never saw this: CanFireNow caches per tick, so its later dry runs replayed one stale false.
071195d89 Transient: ledger shard reconcile log 2026-10-09
d3f7499fc FOUNDRY ledger: land 7 pending local lines (two rite-start recheck items, notes, bridge/game stamps)
0972a3fd7 Rites census: all 3 RitualBehaviorDefs carry roles; recheck items for NineFaults and TheReturn
4d0b64239 BENCH ledger: note on TERMINAL_SETTINGS_CONSUMERS_WIRE_1
a3eab212f TerminalBiomes Mod Settings review notes: dead controls, not clean
... 292 more: git log --oneline a18d58507..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/ModsConfig_before_bridge4.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/ModsConfig_before_d.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwfinal.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwmap.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/Player_load13_20261004.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/Player_pre_acc_20261009.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/Player_sitting1_20261009.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/acc_biomes/retile_Wasteland.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_acc3_crashes_before.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_acc3_illisk_map_id.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_acc3_ls_map_id.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_acc3_slime_map_id.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_acc3_still_map_id.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_acc3_tow_map_id.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_bridge4_deploy_plan.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_bridge4_progress.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_bridge_log_20261004d.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_closer.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deep_proto.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes2_20261008.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes_20261008.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes_20261008b.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_d_biomes.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_d_plain.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_done   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plain2_20261008.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plain_20261008.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plain_20261008b.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plan_d.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_prune.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_prune_c.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_biomes.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain2.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain3.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_biomes.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_done   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_plain.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_first_errors_d.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_preflight2_20261005.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_prep2_20261005.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fw_live_progress_20261008.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_burn.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_ext.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_foam.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_fx.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_p3.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_v2live_20261005.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwkits_20261005.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwliquids_20261005.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwlogistics_20261005.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_fwsheet_20261005.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_gitprobe.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest10_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest11_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest3_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest5_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest6_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest7_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest8_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_harvest9_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lc6_h.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lc6_p1.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lc6_p8.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lc6_schema.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lc6_tools.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lc6_w1.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_ledges_a4.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_ledges_a4b.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_HugeThings_run.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_Wasteland_run.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_Player_load1.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_Player_load2.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_Player_load3.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_compose_apply.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_compose_plan.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_criteria.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_deploy_apply.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_deploy_dryrun.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_harvest.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_liquidheat.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_live_ledge_chain.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lt.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lt2.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_lt3.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe2.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_closename.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_kits.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_pawns.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_research.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_rr.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_ruins.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_probe_size.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun19a_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun19b_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun20a_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun20b_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun20c_20261003.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004i.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004j.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_b1_20261004k.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_b2_20261004l.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_b3_20261004m.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_Forge_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch1_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch2_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_reset_stillsand.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_reviewFW4_20261005.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_selftest_fix_20261009.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_selftests_20261009.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_setbg.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_sum.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_titanic_cctor_20261008.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_titanic_cctor_criteria.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe2.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe3.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe4.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe5.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/desk_muffalo.bmp   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/desk_muffalo.png   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/desk_muffalo_crop.png   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_111942_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_112136_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_115503_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_115726_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_141130_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_192249_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_192717_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_193911_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_194127_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_194450_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_195412_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_195845_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_200302_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_200559_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_201552_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_205124_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_220000_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_220528_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_221930_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_223759_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_224130_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_224933_jobs.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_doing_offline_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_00   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_01   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_02   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_03   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_fw_reviewmap_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_fw_v2_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_gss_proof_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/foundry_kits_rerun_20261006.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_A.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_B.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_EXT.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_RES.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot3.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot4.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA2.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsB.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_cover.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext1.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext3.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext4.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext5.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext6.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso1.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso3.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso4.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso5.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_plotA.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_plots.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_probe.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_probe2.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_probe3.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv1.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv3.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv4.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_rivercount.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite2.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite3.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.progress   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.progress   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.progress   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_settings.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_weir.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_ovn_works.out   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fw_review_map_build_log.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/fwvisuals_serve.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/gpt_rimflow_review_20261007.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/gpt_watchers_enrichment_20261008.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/gpt_watchers_prompt_20261008.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/gptreview_TerminalBiomes.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/gptrun_terminal.log   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/list_tools.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_art_poles_20261004/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_densify_human_review_notes.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_full_plan_run2_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_full_plan_run3_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_full_plan_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_live_run2_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots_pass1/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots2_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec2_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec3_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec4_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_matrix_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r4/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r5/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r6/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r7/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_probe_aerial_after_load.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_read_settings.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_relaunch2_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_relaunch_20261004.txt   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_scenes_20261004.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_time_calls.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/mc_time_calls2.py   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_01_open.png   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T053520Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T053520Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T060517Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T060517Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T141026Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T141026Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Contagion_20261008T180840Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162026Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162026Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162455Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162455Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162938Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162938Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Droidworks_20261008T164227Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Droidworks_20261008T164227Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/FallLineArrivals_20261008T164348Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/FallLineArrivals_20261008T164348Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/FloodedCanyon_20261008T181336Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/FloodedCanyon_20261008T181336Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261008T054429Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261008T054429Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162237Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162237Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162557Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162557Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162710Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162710Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162816Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162816Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T053605Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T053605Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T060512Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T060512Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141235Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141235Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141349Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141349Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141407Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141407Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T172200Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T145909Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T145909Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T151443Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T151443Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T153646Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T153646Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T164403Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T164403Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152152Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152152Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152418Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152418Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152627Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152627Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T153038Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T153038Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T055017Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T055017Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141053Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141053Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141134Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141134Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261008T154155Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261008T154155Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T055021Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T055021Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141200Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141200Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141210Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141210Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261008T054730Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261008T054730Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T053530Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T053530Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T060204Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T060204Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140846Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140846Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140950Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140950Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161034Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161034Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161128Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161128Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161806Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161806Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/UnfinishedLine_20261008T164359Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/UnfinishedLine_20261008T164359Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142004Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142004Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142437Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142437Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142736Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142736Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T143247Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T143247Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Wasteland_20261008T173848Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/Wasteland_20261008T175942Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/WreckedMachines_20261008T164044Z.html   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/WreckedMachines_20261008T164044Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/modcheck/surprises/20261008T212550/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/northstar/Greentide_20261003T102251Z.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/refused_toll_rite_20261006.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/review_pyrelands_20261006.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/unfinished_line_world_20261006.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? Transient/venomvine_forms_20261006.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? conversations/   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_20261009.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_20261009b.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-ishko.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-live_20261008.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-live_20261008b.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-watchers_live.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261005T142015.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261005T161529.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? infrastructure/state/items/ART_PIPELINE_DAEMON_1.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? infrastructure/state/items/BIOME_MOD_SPLIT_EXECUTION_1.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? infrastructure/state/items/BIOME_MOD_UNIFICATION_1.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? infrastructure/state/items/UNSUBSTANTIATED_SPECIES_ABILITIES_1.md   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json   FOUNDRY helpers' scratch from tonight's belt and acceptance runs; Transient shelf life ~14 days
```

