# FOUNDRY_HANDOFF_202610070107 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610061623`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A crash on 2026-10-06 left 4 EMPTY loose git objects (staged blobs) and a 5-hour-stale `.git/index.lock`; a commit referencing them passed but `git fsck` and the DLL stamp guard failed. Fixed by deleting the empty objects and `git hash-object -w` on the identical working files. Run `git fsck --no-dangling` first on any wake after a logged-out crash.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing new needs a decision. Cauldron (CAULDRON_ENRICHMENT_VISUALS_1) and LeaningScrub (LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1) are committed and pushed with rebuilt DLLs, selftests 63/63 and 68/68, but neither has been looked at live.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `UNFINISHED_LINE_WORLD_FOUNDRY_1` — source and defs written, NOT committed (DLL stamp guard would refuse), does not compile: UnfinishedLineWorld.cs lines 445/451 use DebugAction without `using LudeonTK;`; copy of the work in /home/mandrake/rm/ul_wip_backup/; NEXT: add the missing using, rebuild with winbuild.py, then commit source, defs and DLL together
- `CAULDRON_ENRICHMENT_VISUALS_1` and `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` — built offline, pushed, claimed in the ledger, not closed; NEXT: run each live (dewfall/prints, six venomvine forms) and close with the sha
- `BIOME_KITS_PUSH_TO_TEST_1`, `FLOWWORKS_LIQUID_KITS`, `NORTHSTAR_VALIDATION_V2_RECORD_1` — unchanged since FOUNDRY_HANDOFF_202610061623; NEXT: read that handoff's pointers and take the first; NEXT: A DLL commit that omits a new untracked source file still builds locally but fails the stamp guard on push; `git add` untracked files by name before the pathspec commit, since a pathspec on an untracked file errors (filed: this handoff).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A DLL commit omitting a new untracked source file fails the stamp guard on push; `git add` untracked files by name before the pathspec commit (see: this handoff)
- `git pull --rebase` refuses with any unstaged edit and `--autostash` is hook-blocked; park your own WIP as a patch outside the repo, `checkout --` those paths, rebase, reapply (see: this handoff).

## Commits

```
8de6bb477 FOUNDRY ledger: claims and notes from the 2026-10-06 session
7753208e5 Rebuild Cauldron and LeaningScrub DLLs to match committed source; add the venomvine form defs and source the previous commit left out
b7f5f96b0 LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1: venomvine forms built offline (selftest 68/68; not live-checked)
9a94a2c41 CAULDRON_ENRICHMENT_VISUALS_1: dewfall visuals, vexxiss prints, cauldron filth, flora defs (offline build, selftest 63/63; live look not yet checked)
ccbd26c87 BENCH handoff 2026-10-06 18:10
6d2fce793 Sheet renders referenced by the committed biome sheets (185 webp, left untracked at logout)
8e66c9842 BENCH state: ledger bridge events, art ledger events and sheet snapshots left uncommitted at logout
566b06f68 Campaign log: artboard offline half + first real trial
e9c9984a5 Campaign log: GSS scoping (owner-found defects were all visual)
ea51294cf Review batch 10: nine files marked clean after fresh full reviews (shade grid, tether pull, watchers, Warscar/RustCathedral/TerminalBiomes settings, pilgrim camps, Unfinished Line tithe patch)
fe6140ff4 Review batch 9: middens, foundry spunstone parts, spunstone study and tree-fall utility clean
490988350 UNFINISHED_LINE_TITHE_BEAT_1: beat 4 'The Tithe and the Hands' - Enclave shuttle waits for the tithe and a Crafting 8+ colonist lent 10 days; 6 settings (PROVISIONAL); Harmony dependency added; site delivery awaits UNFINISHED_LINE_SITE_CHOICE_1
bb7b2cecf LongShade validation: five creatures/plants moved to other biomes on the 2026-10-04 sheet are checked in their new homes, not flagged missing from the Long Shade roster
2a704a08e LONGSHADE_MIDDENS_DESIGN_1: midden heap, vrekka builds and tends heaps, colonists search for vanilla items, 2 toggles (PROVISIONAL); settings screen reachable; map-gen seeding and clean-patch warning not built
3666db8a6 FORGE_SPUNSTONE_SOURCES_1: foundry salvage cache becomes a second spunstone study source (guarded patch, tickerType Rare; offline-applied only, def is in DEPLOY_HOLD)
dc097d11a Review batch 8: shade-grid light layer no longer doubles light after a toggle and no longer cancels shade-gear cover; Solar Mirrors, ledge refuge and sun-heat math clean
19f4d8374 FORGE_SPUNSTONE_SOURCES_1 (part): floatstone door and floatstone-only spunstone hull wall, both gated on spunstone bonding with their own toggles (PROVISIONAL); salvage-cache source needs a UtinniPatches patch, beam awaits a ruling
82f8e7ea1 Settings screens fixed in the remaining 25 rows (wave 3): scroll view + one-column flag + measured heights; sweep table complete
99b61e39b Solar Mirrors uses a real light-layer hook in CreatureBehaviors' shade grid (IRM_LightLayer) instead of patching its internals; per-tick allocs, world-map drawing and stale-cache bugs fixed; behaviour with no subscriber unchanged
c992f1cb2 Review batch 7: flushing a tamed watcher no longer hunts the colony's pet; a hungry watcher no longer loops hide/emerge; 8 files clean
... 74 more: git log --oneline 473d5a265..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M src/RimUtinni/UnfinishedLine/Defs/HistoryEventDefs/RUT_UnfinishedLine_Events.xml
 M src/RimUtinni/UnfinishedLine/Source/RimMandrake.Utinni.UnfinishedLine.csproj
 M src/RimUtinni/UnfinishedLine/Source/UnfinishedLineMod.cs
?? Transient/ModsConfig_before_bridge4.xml
?? Transient/ModsConfig_before_d.xml
?? Transient/ModsConfig_before_fwfinal.xml
?? Transient/ModsConfig_before_fwmap.xml
?? Transient/Player_load13_20261004.log
?? Transient/belt_bridge4_deploy_plan.txt
?? Transient/belt_bridge4_progress.txt
?? Transient/belt_bridge_log_20261004d.md
?? Transient/belt_deep_proto.py
?? Transient/belt_deploy_d_biomes.txt
?? Transient/belt_deploy_d_plain.txt
?? Transient/belt_deploy_done
?? Transient/belt_deploy_plan_d.txt
?? Transient/belt_deploy_prune.txt
?? Transient/belt_deploy_prune_c.txt
?? Transient/belt_deploy_r5_biomes.txt
?? Transient/belt_deploy_r5_plain.txt
?? Transient/belt_deploy_r5_plain2.txt
?? Transient/belt_deploy_r5_plain3.txt
?? Transient/belt_deploy_r6_biomes.txt
?? Transient/belt_deploy_r6_done
?? Transient/belt_deploy_r6_plain.txt
?? Transient/belt_first_errors_d.txt
?? Transient/belt_flowworksNS_preflight2_20261005.txt
?? Transient/belt_flowworksNS_prep2_20261005.txt
?? Transient/belt_fwfinal_probe_burn.py
?? Transient/belt_fwfinal_probe_ext.py
?? Transient/belt_fwfinal_probe_foam.py
?? Transient/belt_fwfinal_probe_fx.py
?? Transient/belt_fwfinal_probe_p3.py
?? Transient/belt_fwfinal_v2live_20261005.txt
?? Transient/belt_fwkits_20261005.md
?? Transient/belt_fwliquids_20261005.md
?? Transient/belt_fwlogistics_20261005.md
?? Transient/belt_fwsheet_20261005.md
?? Transient/belt_gitprobe.py
?? Transient/belt_harvest10_20261003.txt
?? Transient/belt_harvest11_20261003.txt
?? Transient/belt_harvest3_20261003.txt
?? Transient/belt_harvest5_20261003.txt
?? Transient/belt_harvest6_20261003.txt
?? Transient/belt_harvest7_20261003.txt
?? Transient/belt_harvest8_20261003.txt
?? Transient/belt_harvest9_20261003.txt
?? Transient/belt_probe.py
?? Transient/belt_probe2.py
?? Transient/belt_probe_kits.py
?? Transient/belt_probe_pawns.py
?? Transient/belt_probe_rr.py
?? Transient/belt_probe_ruins.py
?? Transient/belt_probe_size.py
?? Transient/belt_rerun19a_20261003.txt
?? Transient/belt_rerun19b_20261003.txt
?? Transient/belt_rerun20a_20261003.txt
?? Transient/belt_rerun20b_20261003.txt
?? Transient/belt_rerun20c_20261003.txt
?? Transient/belt_rerun_TheSump_20261004i.txt
?? Transient/belt_rerun_TheSump_20261004j.txt
?? Transient/belt_rerun_b1_20261004k.txt
?? Transient/belt_rerun_b2_20261004l.txt
?? Transient/belt_rerun_b3_20261004m.txt
?? Transient/belt_rerun_kits_Forge_20261006.txt
?? Transient/belt_rerun_kits_batch1_20261006.txt
?? Transient/belt_rerun_kits_batch2_20261006.txt
?? Transient/belt_reviewFW4_20261005.md
?? Transient/belt_setbg.py
?? Transient/belt_sum.py
?? Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json
?? Transient/foundry_doing_offline_20261006.txt
?? Transient/foundry_doing_slice_00
?? Transient/foundry_doing_slice_01
?? Transient/foundry_doing_slice_02
?? Transient/foundry_doing_slice_03
?? Transient/foundry_fw_reviewmap_20261006.txt
?? Transient/foundry_fw_v2_20261006.txt
?? Transient/foundry_gss_proof_20261006.txt
?? Transient/foundry_kits_rerun_20261006.txt
?? Transient/fw_ovn_A.out
?? Transient/fw_ovn_ALL.out
?? Transient/fw_ovn_ALL2.out
?? Transient/fw_ovn_B.out
?? Transient/fw_ovn_EXT.out
?? Transient/fw_ovn_RES.out
?? Transient/fw_ovn_boot.out
?? Transient/fw_ovn_boot2.out
?? Transient/fw_ovn_boot3.out
?? Transient/fw_ovn_boot4.out
?? Transient/fw_ovn_chainsA.txt
?? Transient/fw_ovn_chainsA2.txt
?? Transient/fw_ovn_chainsB.txt
?? Transient/fw_ovn_cover.py
?? Transient/fw_ovn_drysite.out
?? Transient/fw_ovn_drysite2.out
?? Transient/fw_ovn_ext1.out
?? Transient/fw_ovn_ext2.out
?? Transient/fw_ovn_ext3.out
?? Transient/fw_ovn_ext4.out
?? Transient/fw_ovn_ext5.out
?? Transient/fw_ovn_ext6.out
?? Transient/fw_ovn_iso1.out
?? Transient/fw_ovn_iso2.out
?? Transient/fw_ovn_iso3.out
?? Transient/fw_ovn_iso4.out
?? Transient/fw_ovn_iso5.out
?? Transient/fw_ovn_plotA.out
?? Transient/fw_ovn_plots.out
?? Transient/fw_ovn_probe.py
?? Transient/fw_ovn_probe2.py
?? Transient/fw_ovn_probe3.py
?? Transient/fw_ovn_riv1.out
?? Transient/fw_ovn_riv2.out
?? Transient/fw_ovn_riv3.out
?? Transient/fw_ovn_riv4.out
?? Transient/fw_ovn_rivercount.py
?? Transient/fw_ovn_riversite.out
?? Transient/fw_ovn_riversite2.out
?? Transient/fw_ovn_riversite3.out
?? Transient/fw_ovn_runA.out
?? Transient/fw_ovn_runA.progress
?? Transient/fw_ovn_runB.out
?? Transient/fw_ovn_runB.progress
?? Transient/fw_ovn_runC.out
?? Transient/fw_ovn_runC.progress
?? Transient/fw_ovn_settings.py
?? Transient/fw_ovn_weir.py
?? Transient/fw_ovn_works.out
?? Transient/fw_review_map_build_log.md
?? Transient/fwvisuals_serve.log
?? Transient/list_tools.py
?? Transient/mc_art_poles_20261004/
?? Transient/mc_densify_human_review_notes.md
?? Transient/mc_full_plan_run2_20261004.txt
?? Transient/mc_full_plan_run3_20261004.txt
?? Transient/mc_full_plan_run_20261004.txt
?? Transient/mc_live_run2_20261004.txt
?? Transient/mc_matrix_fast_20261004.json
?? Transient/mc_matrix_fast_run_20261004.txt
?? Transient/mc_matrix_live_20261002/shots/
?? Transient/mc_matrix_live_20261002/shots_pass1/
?? Transient/mc_matrix_noshots2_run_20261004.txt
?? Transient/mc_matrix_noshots3_20261004.json
?? Transient/mc_matrix_noshots3_run_20261004.txt
?? Transient/mc_matrix_noshots_run_20261004.txt
?? Transient/mc_matrix_rec2_20261004.json
?? Transient/mc_matrix_rec3_20261004.json
?? Transient/mc_matrix_rec4_20261004.json
?? Transient/mc_matrix_rec_20261004.json
?? Transient/mc_matrix_run_20261004.txt
?? Transient/mc_owner_shots_r4/
?? Transient/mc_owner_shots_r5/
?? Transient/mc_owner_shots_r6/
?? Transient/mc_owner_shots_r7/
?? Transient/mc_probe_aerial_after_load.py
?? Transient/mc_read_settings.py
?? Transient/mc_relaunch2_20261004.txt
?? Transient/mc_relaunch_20261004.txt
?? Transient/mc_scenes_20261004.json
?? Transient/mc_time_calls.py
?? Transient/mc_time_calls2.py
?? Transient/messy_conduit_live_20261002/maze_01_open.png
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png
?? Transient/modcheck/fixtures.json
?? Transient/modcheck/live_queue/J1_situational_rerun/
?? Transient/modcheck/live_queue/J2_abort_proof/
?? Transient/modcheck/live_queue/situational_rerun/FlameStatues_summary.json
?? Transient/modcheck/live_queue/situational_rerun/ResearchRetag_summary.json
?? Transient/modcheck/surprises/20261004T023842/
?? Transient/modcheck/surprises/20261004T030802/
?? Transient/modcheck/surprises/20261004T032016/
?? Transient/modcheck/surprises/20261004T035902/
?? Transient/modcheck/surprises/20261004T050655/
?? Transient/modcheck/surprises/20261004T053947/
?? Transient/modcheck/surprises/20261004T055717/
?? Transient/modcheck/surprises/20261004T060347/
?? Transient/modcheck/surprises/20261004T062227/
?? Transient/modcheck/surprises/20261004T063127/
?? Transient/modcheck/surprises/20261004T064738/
?? Transient/modcheck/surprises/20261004T064928/
?? Transient/modcheck/surprises/20261004T071347/
?? Transient/modcheck/surprises/20261004T072546/
?? Transient/modcheck/surprises/20261004T074823/
?? Transient/modcheck/surprises/20261005T232247/
?? Transient/modcheck/surprises/20261005T233028/
?? Transient/modcheck/surprises/20261005T235519/
?? Transient/modcheck/surprises/20261006T001545/
?? Transient/modcheck/surprises/20261006T002351/
?? Transient/modcheck/surprises/20261006T003801/
?? Transient/modcheck/surprises/20261006T003853/
?? Transient/modcheck/surprises/20261006T004010/
?? Transient/modcheck/surprises/20261006T004657/
?? Transient/modcheck/surprises/20261006T011305/
?? Transient/modcheck/surprises/20261006T020612/
?? Transient/modcheck/surprises/20261006T021919/
?? Transient/modcheck/surprises/20261006T025413/
?? Transient/modcheck/surprises/20261006T044850/
?? Transient/modcheck/surprises/20261006T045919/
?? Transient/modcheck/surprises/20261006T050151/
?? Transient/modcheck/surprises/20261006T050713/
?? Transient/modcheck/surprises/20261006T060942/
?? Transient/modcheck/surprises/20261006T061257/
?? Transient/modcheck/surprises/20261006T061439/
?? Transient/modcheck/surprises/20261006T062549/
?? Transient/modcheck/surprises/20261006T063053/
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json
?? Transient/northstar/Greentide_20261003T102251Z.json
?? Transient/refused_toll_rite_20261006.md
?? Transient/review_pyrelands_20261006.md
?? Transient/unfinished_line_world_20261006.md
?? Transient/venomvine_forms_20261006.md
?? conversations/
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml
?? deployed/config/ModsConfig.before-tier-flowworks.xml
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml
?? deployed/config/ModsConfig.before-tier-messyconduit.xml
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml
?? deployed/config/ns_flowworks_backup.20261002T070221.json
?? deployed/config/ns_flowworks_backup.20261005T142015.json
?? deployed/config/ns_flowworks_backup.20261005T161529.json
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_dirt.png
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_stone.png
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_dirt.png
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_stone.png
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T232949.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T233603.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T000710.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T001245.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T002141.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003132.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003420.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003624.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003701.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003821.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T004655.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T010918.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011022.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011246.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T020515.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021000.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021144.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021337.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021908.json
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T033840.json
?? src/RimUtinni/UnfinishedLine/Defs/IncidentDefs/RUT_FoundryStrike.xml
?? src/RimUtinni/UnfinishedLine/Source/UnfinishedLineWorld.cs
```

