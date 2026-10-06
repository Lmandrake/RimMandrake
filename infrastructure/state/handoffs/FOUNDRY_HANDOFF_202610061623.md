# FOUNDRY_HANDOFF_202610061623 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610061232`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The FlowWorks checkout was slow because runs went STALE, not because checks were slow: mod_hash covered art_source (14.6 MB), review-map tooling and a held scaffold, so any art or tooling edit voided every finished run. Fixed with `FlowWorks/.hashignore` (status.py `_hashignore`); v2 is GREEN 59/59 in 176 s, recorded at the current hash. BENCH is now remaking the evaluation: start from that, and remember the scoreboard still counts 0 proven for FlowWorks because validation_v2 records no deploy fingerprint or detector coverage.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- FlowWorks north star stays DRAFT: needs his re-validate plus the owner review `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` waits on. GimmeSomeSlack is CONDITIONALLY ACCEPTED by his word (not validated); 9 live matrix hose FAILs (MX_H00.. min_bend_radius_ge ~0.19 vs 0.95x1.2) are untraced.
- Tar look: he chose mid grey between dark and light; saved as tint (0.58,0.56,0.60), verified by probe after a cold start. The pond still rendered pure black in screenshots while its colour read grey: cause not found, he says it now reads as visibly dark liquid.
- His open art notes from the review map: station 8 proportions (100-cell lower canal, appears filled though captioned empty), station 9 brown Mud squares beside ponds, muffalo pale-blue ghost render near station 17, station 10 red spots (lava shader, gone), torch/fire source at the channel end (not built: ignition needs a real Fire thing).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `BIOME_KITS_PUSH_TO_TEST_1` — TheForge 72P/1F/22U, FeverWood 84P/5F/12U, Greentide partial; Scarlands, RustCathedral, TerminalBiomes, CreatureBehaviors never ran this pass; NEXT: rerun `situational_rerun.py --mods Scarlands,RustCathedral,TerminalBiomes,CreatureBehaviors --bland-world --retile` on the builds_biomes tier after triaging floatstone and the FeverWood cloud-suppression rows
- `FLOWWORKS_LIQUID_KITS` — baths, reactions, hot floods, residue built, wired into Mod Settings, defs resolve live (73ad78ccb); no station, feature row or run exercises them; NEXT: add a Liquid kits feature row to human_review.py FEATURES and run each mechanic live
- `NORTHSTAR_VALIDATION_V2_RECORD_1` (not filed) — validation_v2 and proof_all write no deploy fingerprint or detector record so the report shows 0 proven; NEXT: file it and make both scripts record run_identity at start and end
- `FLOWWORKS_TANK_LOOP_ROW_WRONG_1` and `FLOWWORKS_CONFINEMENT_TOGGLE_VESTIGIAL_1` — still open, need his decision; NEXT: ask whether to retire channelConfinementEnabled (touches the hash-bound walk)
- `GAME_STATE` — game UP on the flowworks tier with the review map loaded, bridge FREE; NEXT: run modset_builder.py --restore with the game closed when nobody needs it (his FULL.LATEST list is 610 mods)
- `crash-backup-20261005` branch and refs/stash-saves/crash-autostash-20261005 — liquid looks re-landed; NEXT: delete both once he agrees nothing else is wanted
- Local clone note — this window's earlier pull --rebase failed on a dirty tree; NEXT: before any pull here commit tracked Transient/ledger files by explicit path

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `required_checks_report`/modcheck status judged runs STALE because mod_hash covered non-shipping files (see: `FlowWorks/.hashignore`, commit message of this session)
- A def naming a C# class that is not in the csproj compiles into nothing and trips the launch gate on every map; deploy copied it because untracked defs deploy (see: src/DEPLOY_HOLD.txt history, CLAUDE.md EnableDefaultCompileItems line)
- zsh does not split an unquoted path list: `git commit $F` with a string failed with one giant pathspec; use a zsh array (see: CLAUDE.md zsh trap)
- pkill -f killed my own shell (see: memory pkill-f-matches-my-own-shell)
- RM_LiquidLookProof.Tune only re-applies members of the NAMED liquid or fluid: tune RM_Liquid_Tar for the pond and RM_Fluid_Tar for the canal fills, then read Material to confirm (filed: lessons)
- OS-level screenshots catch other windows over the game; use rimworld/take_screenshot (saved under the game's Screenshots folder) (filed: lessons)

## Commits

```
6c720a859 Tar surface tint set to the owner's chosen mid grey (0.58,0.56,0.60), verified after a cold start
647645474 Liquid look proof: Material probe reads a terrain's real shader, colour and queue (tar renders black though its colour reads mid-grey)
7835cf0f6 FOUNDRY ledger: bridge taken and released
a124f9ae1 Tar uses the water shader and wading splash, near-black slate colour (owner 2026-10-06); NOT yet seen working
02a56e4bc FlowWorks review README: how to return to the keeper review map
07bddf469 FlowWorks review map verify record 2026-10-06
227cb33a3 FlowWorks review sheet and map key regenerated from the 2026-10-06 GREEN run; review map built (85/85 stations) and saved as RM_fw_review_20261006
73ad78ccb FOUNDRY ledger: bridge taken and released
b13f21360 FlowWorks liquid kits: baths, reactions, hot floods and residue built, wired into Mod Settings, loaded live
2cd2a25fd FOUNDRY ledger: bridge taken and released
218dde98e FlowWorks mod hash ignores files that never ship, so art and tooling work no longer stales a finished run
9ef73b127 Kit rerun and GSS acceptance records 2026-10-06; NORTHSTAR_RESULTS_JOIN_1 prose moved to closed/
caabd9e92 GSS north star conditionally accepted by owner (not validated); open: 9 matrix hose FAILs untraced
270ff6a99 File 6 Chill plant variant art jobs (Eldspar/Fuselight/Ghostpane var2/var3) Derived from kept A; NEXT note on CHILL_SURFACE_SITTING_1 for Graphic_Random wiring.
cd93b54f6 Chill art rulings ingested (14 rulings, 3 purges) + 12 art jobs filed Variants (Eldspar/Fuselight/Ghostpane) have no pipeline mechanism; not filed. Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
4d436e2a3 Chill sheet rulings (owner, 2026-10-06) + sheet refresh state; owner-shard drop event
865c70ad6 Cut RM_Keelgrass from the Chill (owner, Chill sheet: "it is gone")
60a9e364d Ledger: drop PROPANE_LAKE_HYDROCARBON_TENTACLER_1
d2f36f0b6 Drop RM_Ulkhoss (owner: "Drop the ulkhoss, don't need it.")
73a431abf Gate req 4: our own copy is not the donor column; purged donor original counts as shown-and-rejected Sheets export `ours` and `donorPurged`; rows with no donor original at all fail as UNMEASURED donor art. Abyss rebuilt. Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
... 10 more: git log --oneline e99f4f6b5..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/ModsConfig_before_bridge4.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/ModsConfig_before_d.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/ModsConfig_before_fwfinal.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/ModsConfig_before_fwmap.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/Player_load13_20261004.log   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_bridge4_deploy_plan.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_bridge4_progress.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_bridge_log_20261004d.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deep_proto.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_d_biomes.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_d_plain.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_done   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_plan_d.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_prune.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_prune_c.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r5_biomes.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r5_plain.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r5_plain2.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r5_plain3.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r6_biomes.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r6_done   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_deploy_r6_plain.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_first_errors_d.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_flowworksNS_preflight2_20261005.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_flowworksNS_prep2_20261005.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwfinal_probe_burn.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwfinal_probe_ext.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwfinal_probe_foam.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwfinal_probe_fx.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwfinal_probe_p3.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwfinal_v2live_20261005.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwkits_20261005.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwliquids_20261005.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwlogistics_20261005.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_fwsheet_20261005.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_gitprobe.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest10_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest11_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest3_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest5_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest6_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest7_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest8_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_harvest9_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe2.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe_kits.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe_pawns.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe_rr.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe_ruins.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_probe_size.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun19a_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun19b_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun20a_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun20b_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun20c_20261003.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_TheSump_20261004i.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_TheSump_20261004j.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_b1_20261004k.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_b2_20261004l.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_b3_20261004m.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_kits_Forge_20261006.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_kits_batch1_20261006.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_rerun_kits_batch2_20261006.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_reviewFW4_20261005.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_setbg.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/belt_sum.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/foundry_fw_reviewmap_20261006.txt   FOUNDRY, this session
?? Transient/foundry_fw_v2_20261006.txt   FOUNDRY, this session
?? Transient/foundry_gss_proof_20261006.txt   FOUNDRY, this session
?? Transient/foundry_kits_rerun_20261006.txt   FOUNDRY, this session
?? Transient/fw_ovn_A.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ALL.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ALL2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_B.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_EXT.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_RES.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_boot.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_boot2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_boot3.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_boot4.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_chainsA.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_chainsA2.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_chainsB.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_cover.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_drysite.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_drysite2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ext1.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ext2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ext3.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ext4.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ext5.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_ext6.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_iso1.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_iso2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_iso3.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_iso4.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_iso5.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_plotA.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_plots.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_probe.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_probe2.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_probe3.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riv1.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riv2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riv3.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riv4.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_rivercount.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riversite.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riversite2.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_riversite3.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_runA.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_runA.progress   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_runB.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_runB.progress   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_runC.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_runC.progress   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_settings.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_weir.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_ovn_works.out   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/fw_review_map_build_log.md   FOUNDRY, this session
?? Transient/fwvisuals_serve.log   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/list_tools.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_art_poles_20261004/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_densify_human_review_notes.md   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_full_plan_run2_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_full_plan_run3_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_full_plan_run_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_live_run2_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_fast_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_fast_run_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_live_20261002/shots/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_live_20261002/shots_pass1/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_noshots2_run_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_noshots3_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_noshots3_run_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_noshots_run_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_rec2_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_rec3_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_rec4_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_rec_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_matrix_run_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_owner_shots_r4/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_owner_shots_r5/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_owner_shots_r6/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_owner_shots_r7/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_probe_aerial_after_load.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_read_settings.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_relaunch2_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_relaunch_20261004.txt   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_scenes_20261004.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_time_calls.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/mc_time_calls2.py   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/messy_conduit_live_20261002/maze_01_open.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/fixtures.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/live_queue/J1_situational_rerun/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/live_queue/J2_abort_proof/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/live_queue/situational_rerun/FlameStatues_summary.json   FOUNDRY, this session
?? Transient/modcheck/live_queue/situational_rerun/ResearchRetag_summary.json   FOUNDRY, this session
?? Transient/modcheck/surprises/20261004T023842/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T030802/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T032016/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T035902/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T050655/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T053947/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T055717/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T060347/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T062227/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T063127/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T064738/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T064928/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T071347/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T072546/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261004T074823/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261005T232247/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261005T233028/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261005T235519/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T001545/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T002351/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T003801/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T003853/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T004010/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T004657/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T011305/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T020612/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T021919/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T025413/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T044850/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T045919/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T050151/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T050713/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T060942/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T061257/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T061439/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T062549/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/modcheck/surprises/20261006T063053/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? Transient/northstar/Greentide_20261003T102251Z.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? conversations/   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.before-tier-flowworks.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ns_flowworks_backup.20261002T070221.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ns_flowworks_backup.20261005T142015.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? deployed/config/ns_flowworks_backup.20261005T161529.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? infrastructure/state/items/closed/NORTHSTAR_RESULTS_JOIN_1.md   FOUNDRY, this session
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_dirt.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_stone.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_dirt.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_stone.png   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T232949.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T233603.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T000710.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T001245.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T002141.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003132.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003420.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003624.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003701.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003821.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T004655.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T010918.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011022.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011246.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T020515.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021000.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021144.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021337.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021908.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T033840.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/matrix_live_20261004T104900.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/matrix_live_20261004T111300.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T010730.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T012345.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T012712.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T082415.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T084118.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T084830.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T085649.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T090138.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T105819.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T110845.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T084920.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T085739.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T090236.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T105830.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T110854.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_carry_20261004T233651.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_carry_20261005T001134.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_live_20261004T085236.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_live_20261004T105934.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_live_20261004T110908.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_maze_20261004T234830.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_maze_20261004T235220.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_maze_20261004T235328.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_relay_20261004T225835.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_save-load_20261004T085316.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_save-load_20261004T105944.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_save-load_20261004T110918.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T084401.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T105710.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T110816.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T144404.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_save-load_20261004T084454.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_save-load_20261004T105719.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_save-load_20261004T110824.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_hose_live_20261004T212855.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_hose_live_20261004T212933.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T175845.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T180716.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T212841.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T212919.json   earlier sessions (BELT/FOUNDRY/BENCH), untracked run output, left in place
```

