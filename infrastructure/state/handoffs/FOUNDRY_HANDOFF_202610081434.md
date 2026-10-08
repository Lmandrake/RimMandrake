# FOUNDRY_HANDOFF_202610081434 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610080208`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Memory discipline is now law for this seat: nothing under /tmp (tmpfs counts against the 10G seat cap and survives its writer), selftests at most 4 workers, at most 3 subagents. The crash of 23:16 on 10-07 was memory, not a bug; its lost work is recovered (local main realigned to origin, selftest triage, acc_biomes fixes, SolarMirrors pass 4, held-clone triage all pushed). Fleet fix is SEAT_MEMORY_CLONES_DRIVES_1 (BENCH).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **HugeThings is broken by a mod bug**: RM_TitanicCreaturesMod's static constructor throws in Harmony patching, so wake components are never injected (HUGETHINGS_TITANIC_CCTOR_THROWS_1, cause unproven beyond 'likely PatchNamespace').
- **SluiceGate landed as a draft** (6cdda1140): new C# in FlowWorks, no ThingDef or engine hook wired.
- Open Wasteland/Contagion live-suite rows and the Linked-graphic NRE are listed in Transient/acc_biomes_fixes_20261008.md; Warcasket has 2 unexplained live failures.
- Quarantine (/home/mandrake/rm/_quarantine/2026-10-08/, ~106 GB incl. wt/gitlab 30 GB) is awaiting your word to purge; safe set and commands in Transient/stale_clones_exam_20261008.md.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `GPT_FULL_REVIEW_TOP10_1` — TerminalBiomes review launched detached (pid of run_gpt_review.py, 2400 s timeout), no file yet; NEXT: check design/RimMandrake/gpt_reviews/TerminalBiomes.md exists, then verify all 10 reviews' claims against source before acting.
- `ACCEPTANCE_SITTING_RESUME` — acc_green_min done except LuminousPigment and Ninefold; acc_green_min2, acc_l1x, acc_harness, flowworks never started; bridge RELEASED; NEXT: rimflow bridge take, rerun LuminousPigment/Ninefold with python -u, then the remaining tiers one driver at a time.
- `HUGETHINGS_TITANIC_CCTOR_THROWS_1` — filed, unfixed; NEXT: read Player.log for the Harmony exception in RM_TitanicCreaturesMod cctor, fix, rebuild, restart.
- `WASTELAND_CONTAGION_LIVE_FAILS` (items from acc_biomes) — tipping/middenshell toggles, Contagion placement/inject/manhunter unresolved; NEXT: reproduce live per Transient/acc_biomes_fixes_20261008.md.
- `SEAT_MEMORY_CLONES_DRIVES_1` — BENCH's; phase 1 partly landed (claude_bounded, block_tmpfs_clone hook); NEXT: none for FOUNDRY except obey the memory limits.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- git hard reset/stash are hook-blocked; recover a divergent local main with commit-then-`pull --rebase` after moving blocking untracked files aside (filed: this handoff)
- A helper pushing from a no-checkout clone leaves duplicate unpushed commits locally; rebase drops them (see: Transient/held_clone_triage_20261008.md)
- run_gpt_review.py wrote its input to /tmp (tmpfs); now Transient/ (see: commit on origin/main)

## Commits

```
615707116 FOUNDRY ledger: bridge release
7f679850e FOUNDRY ledger: close HELD_CLONE_WORK_TRIAGE_1, bridge events
3a4aab0de run_gpt_review: stage bundle on ext4 Transient, not tmpfs /tmp
528690632 Warcasket validation: strip random apparel in _settle, wide-rect pawn lookup, diagnostics for missing pawns
90dbfb822 Seat memory watchdog: rm-memwatch timer reads memory.events/shmem per seat, toasts on oom_kill (SEAT_MEMORY_CLONES_DRIVES_1)
0b43abbe0 mirror: gc.autoDetach=false so auto-gc is not killed at unit exit, leaking tmp_pack_* (MIRROR_REPACK_LEAK_FIX_1)
bea86861e BENCH handoff 2026-10-08: seat-memory work landed, restart to verify the new launcher live
905266c35 Seat memory: lesson pointing at the enforcement; progress note on SEAT_MEMORY_CLONES_DRIVES_1
139775499 Selftests run in rm-harness.slice, not the seat (SEAT_MEMORY_CLONES_DRIVES_1)
f9cefa560 Record owner's concern about home-made seat-memory pieces and the standard fallback (mask tmp.mount)
d8b371cae HELD_CLONE_WORK_TRIAGE_1: decision table
6cdda1140 FlowWorks: land stranded sluice gate draft (Building_RM_SluiceGate, math, settings)
8807aaa41 claude_bounded: delegated tool cgroup (6G, swap 0), seat temp on ext4, terminal reset on any exit
c998ed183 File quarantine purge (10-15), held clone work triage, mirror repack leak; web research on Claude Code memory
b04e16755 Queue own-art jobs for condenser water, karrek paste, seep stone
1a13d2c17 File the art and DLL tails from the 10-08 handoff as ledger items so none lingers unowned
93ae58050 Add block_tmpfs_clone PreToolUse hook; merge hook points at ext4 scratch, not /tmp worktree
a46ffeffd Stale clones exam 2026-10-08: unpushed/alternates check, verdicts, proposed removal order
7a9793fff HugeThings validation: settings set triggers RefreshAllMaps; wake failure is a mod bug (Titanic cctor throws)
882696f61 Disk clean-up 2026-10-08: quarantine list, held-back clones, mirror tmp_pack cause
... 175 more: git log --oneline 0633d640b..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/ModsConfig_before_bridge4.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/ModsConfig_before_d.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwfinal.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwmap.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/Player_load13_20261004.log   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_bridge4_deploy_plan.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_bridge4_progress.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_bridge_log_20261004d.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deep_proto.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes2_20261008.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes_20261008.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes_20261008b.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_d_biomes.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_d_plain.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_done   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_plain2_20261008.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_plain_20261008.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_plain_20261008b.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_plan_d.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_prune.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_prune_c.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_biomes.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain2.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain3.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_biomes.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_done   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_plain.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_first_errors_d.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_preflight2_20261005.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_prep2_20261005.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_burn.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_ext.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_foam.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_fx.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_p3.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwfinal_v2live_20261005.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwkits_20261005.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwliquids_20261005.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwlogistics_20261005.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_fwsheet_20261005.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_gitprobe.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest10_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest11_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest3_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest5_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest6_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest7_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest8_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_harvest9_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe2.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe_kits.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe_pawns.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe_rr.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe_ruins.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_probe_size.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun19a_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun19b_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun20a_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun20b_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun20c_20261003.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004i.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004j.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_b1_20261004k.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_b2_20261004l.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_b3_20261004m.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_Forge_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch1_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch2_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_reviewFW4_20261005.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_setbg.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/belt_sum.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/desk_muffalo.bmp   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/desk_muffalo.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/desk_muffalo_crop.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_doing_offline_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_00   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_01   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_02   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_03   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_fw_reviewmap_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_fw_v2_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_gss_proof_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/foundry_kits_rerun_20261006.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_A.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_B.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_EXT.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_RES.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_boot.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_boot2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_boot3.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_boot4.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA2.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsB.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_cover.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ext1.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ext2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ext3.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ext4.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ext5.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_ext6.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_iso1.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_iso2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_iso3.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_iso4.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_iso5.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_plotA.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_plots.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_probe.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_probe2.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_probe3.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riv1.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riv2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riv3.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riv4.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_rivercount.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite2.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite3.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.progress   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.progress   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.progress   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_settings.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_weir.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_ovn_works.out   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fw_review_map_build_log.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/fwvisuals_serve.log   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/gpt_rimflow_review_20261007.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/gptreview_TerminalBiomes.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/gptrun_terminal.log   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/list_tools.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_art_poles_20261004/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_densify_human_review_notes.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_full_plan_run2_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_full_plan_run3_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_full_plan_run_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_live_run2_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_run_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots_pass1/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots2_run_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_run_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots_run_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_rec2_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_rec3_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_rec4_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_rec_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_matrix_run_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r4/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r5/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r6/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r7/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_probe_aerial_after_load.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_read_settings.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_relaunch2_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_relaunch_20261004.txt   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_scenes_20261004.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_time_calls.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/mc_time_calls2.py   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_01_open.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T053520Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T053520Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T060517Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T060517Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T141026Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T141026Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261008T054429Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261008T054429Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T053605Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T053605Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T060512Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T060512Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141235Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141235Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141349Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141349Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141407Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141407Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T055017Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T055017Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141053Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141053Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141134Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141134Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T055021Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T055021Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141200Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141200Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141210Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141210Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261008T054730Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261008T054730Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T053530Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T053530Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T060204Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T060204Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140846Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140846Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140950Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140950Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142004Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142004Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142437Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142437Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142736Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142736Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T143247Z.html   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T143247Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/northstar/Greentide_20261003T102251Z.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/refused_toll_rite_20261006.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/review_pyrelands_20261006.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/unfinished_line_world_20261006.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? Transient/venomvine_forms_20261006.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? conversations/   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-flowworks.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-ishko.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261002T070221.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261005T142015.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261005T161529.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? infrastructure/state/items/SHIPVERMIN_FREE_TIER_BEASTS_1.md   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_dirt.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_stone.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_dirt.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_stone.png   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T232949.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T233603.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T000710.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T001245.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T002141.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003132.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003420.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003624.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003701.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003821.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T004655.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T010918.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011022.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011246.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T020515.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021000.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021144.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021337.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021908.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T033840.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261007T140351.json   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
?? src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll.srchash   scratch from earlier BELT/bridge or helper runs, not mine to commit; Transient shelf life ~14 days
```

