# FOUNDRY_HANDOFF_202610090438 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610081434`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

Everything built tonight is OFFLINE-proven only; the live game is up on tier `live_20261008b` (19 mods, quicktest map, no human) and 27 live criteria are UNMEASURED because each needs a scene nobody has built. The scene harness (`src/RimMandrake/Utils/scenes/`) is the unlock: build it first, then the ledger's owed criteria become cheap.

## What the owner should see

- Provisional numbers nobody ruled on (all marked PROVISIONAL): Watcher shyness (flinch 9 cells, down 7500-15000 ticks), dry-air blower cooler 14 heat/s and 250 W, Greentide ambient felt heat raised 8 to 12 C, night visibility 0.05 per lit deepfire light per hour, carving memory +4 mood 2 days, ledge counts.
- Texts drafted for his review, shipped as placeholders: 10 biome arrival letters (`Transient/arrival_letters_draft_20261008.md`) and the Cracked Lands ledge inscriptions (`Transient/ledges_inscriptions_draft_20261008.md`).
- Owner question still open: `CRUST_NEVER_STRANDS_1` (needs: owner; card text is in the item). Also the Rust Cathedral Watcher is the sole machine in a no-wildlife biome: bans were read as allowing it like the living bolt.
- Twilight wells: last fading step that can never be reached and what 'frozen' means are unruled.
- `selftest_memwatch.py` fails (BENCH's SEAT_MEMORY work, not ours).
- Watchers was ruled twice today in a way that REVERSED an old ruling: flush hunting is gone entirely (owner typed 'Watchers can't be flushed. They just won't').

## What is half-done, and where it stops

- `SCENE_HARNESS_1` (filed in the progress note only, no item) — nothing built; NEXT: create `src/RimMandrake/Utils/scenes/` on `Transient/belt_lc6_lib.py`, then measure the 27 criteria listed in `Transient/belt_scene_harness_20261008.md`.
- `WATCHER_CREATURES_MOD_1` — kit, piinnok and Rust Cathedral Watcher built; art for the Watcher queued (9 artpipe jobs); NEXT: when the five head pictures land, list them on the head node in `RM_Watcher_RenderTree.xml`, then run the owed live checks.
- `CRUST_NEVER_STRANDS_1` — needs owner; NEXT: ask the card text in the item.
- Ten `next ten` items (`WIRE_DOWN_ALERT_1`, `DECOY_SHADE_TARP_1`, `SPECIMEN_CABINET_DISPLAY_1`, `THICK_LIQUID_CREEP_1`, `SHIP_TOW_LINE_1`, `DUST_SETTLED_LETTER_1`, `SCREEN_STOPS_SPORES_1`, `VERMIN_EAT_BREEDING_FOOD_1`, `TAKEN_BY_LAND_SERVICE_1`) — filed, none built; NEXT: build in that order, S/M first.
- Remaining design-pass idea rows (per-mod and cross-mod tables) — not filed; NEXT: check each row against `infrastructure/state/items/` before filing.
- `WASTELAND_LIVE_FIXTURE_FIXES_1`, `HUGETHINGS_TRUNK_ZERO_BLOCKERS_1` — the second filed, intermittent footprint failure; NEXT: add a debug state read beside the failing check and rerun.
- `DESTROY_BATCH_NEVER_KILLS_PAWNS_1` — filed; NEXT: fix Cauldron `kill_pawns()` and northstar `despawn_pawns_in()` to use a tool that kills pawns.
- `BOILING_ICY_CANAL_FLUIDS_1` — filed; NEXT: add a hot liquid that can flow into a dug channel so a pit can flood with boiling water.
- Harmony resilience adoption — FlowWorks only; NEXT: adopt `PatchApplier` in Ninefold (31 patches) and GimmeSomeSlack (22), then the other 35 mods.
- Game state: running on `live_20261008b`; NEXT: `modset_builder.py --restore` after killing the game, when the owner wants his full list back.

## Traps learned

- `jawa/destroy_batch` never destroys pawns, whatever category you pass; two harnesses relied on it (filed: DESTROY_BATCH_NEVER_KILLS_PAWNS_1)
- A per-mod `deploy --apply` never touches the composed `RimMandrake.Biomes` mod and leaves retired files behind; use `--compose biomes --apply --prune` (see: Transient/belt_live_checks6_20261008.md)
- Selftest build cache reused a stale binary after a source restore and gave a false failure; clear `bin`/`obj` under `D:\Luke\dev\_rmbuild\<name>` (see: Transient/belt_watchers_death or the Watchers progress note)
- Building a path list from `git status` including `??` sweeps in untracked files (99b1619d9) (filed: this handoff)
- `fw_FlowWorks2.txt` is the offline tier, 35 injected faults that are supposed to fail; it is not live evidence (see: Transient/belt_fw_pulse_20261008.md)

## Commits

```
e38328542 Transient: live run outputs from today's acceptance sittings
96b840414 file next-ten design-pass items (Queue all, card 2026-10-08)
f06e97149 BENCH ledger: close MIRROR_REPACK_LEAK_FIX_1, release GREYSEA_FLOOR_PASS_1 with next step
a583da175 scene harness: handoff notes, nothing built yet
32d66ab3f live checks 2026-10-08: progress log, probe scripts, results
38d3bc308 ledger: live checks 2026-10-08 verify events (Watchers W1-W3, fallen wire A1-A4, ticker, scald, warscar, liquid heat, chill pump, dishes)
163c36d80 Pulse widget: manual no-activate title-bar drag (pywebview drag region fails on a NOACTIVATE window)
07ba5826c Away dashboard hang: debugging notes
579d7a824 Watchers: fix three live-found defects (sign TickRare threw NotImplementedException so orphan signs never cleared; RM_Watcher body had no Moving limb so it could not be generated; remains config error); live tier live_20261008b
281d1b91d Pulse autostart task: MultipleInstances Parallel (IgnoreNew refused every re-run while the widget lived)
0d93c27be Pulse widget: fix GUI hang (pywebview walked Api.window into .NET); startup stages, hang watchdog, async SetWindowPos
9b17744c3 Install I'm back digest hook; digest window settable (3h, 90m, 2d, 17:30, 'since 5pm', 'last 6 hours')
07ff006d0 Enact 2026-10-08 card decisions: FeverWood seven redraws, live x'd art deleted (Swarmling, Eopie, Lothcat, Scurrier), Nerf E installed, Great Devourer -> RM_Gulloth
294cac7a1 Away dashboard build log: final state
69c85b19f Pulse: classify OOM kills from the kernel log (planted pen test is not an alarm); widget never resizes on data
d4b968909 ledger: BLOWER_ROOM_COOLER_1 + LAUNCH_HELD_COLONIST_WARNING_1 implemented
d2454e533 Dry-air blower is a room cooler that never heats (BLOWER_ROOM_COOLER_1); launch dialog names held colonists (LAUNCH_HELD_COLONIST_WARNING_1)
68bde2c78 Pulse widget: fit to content, self-reload, autostart task, I'm-back hook (prepared)
593156f3a Pulse spine + floating widget for the away dashboard (AWAY_DASHBOARD_BUILD_1)
29a03f481 Canon realism sweep: progress log, regenerated INDEX, mon_calamari note on deleted rakata image
... 194 more: git log --oneline 38cf6158a..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/ModsConfig_before_bridge4.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/ModsConfig_before_d.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwfinal.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwmap.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/Player_load13_20261004.log   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/acc_biomes/retile_Wasteland.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_bridge4_deploy_plan.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_bridge4_progress.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_bridge_log_20261004d.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_closer.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deep_proto.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes2_20261008.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes_20261008.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_biomes_20261008b.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_d_biomes.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_d_plain.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_done   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plain2_20261008.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plain_20261008.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plain_20261008b.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_plan_d.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_prune.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_prune_c.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_biomes.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain2.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain3.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_biomes.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_done   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_plain.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_first_errors_d.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_preflight2_20261005.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_prep2_20261005.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fw_live_progress_20261008.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_burn.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_ext.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_foam.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_fx.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_p3.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwfinal_v2live_20261005.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwkits_20261005.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwliquids_20261005.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwlogistics_20261005.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_fwsheet_20261005.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_gitprobe.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest10_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest11_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest3_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest5_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest6_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest7_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest8_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_harvest9_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lc6_h.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lc6_p1.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lc6_p8.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lc6_schema.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lc6_tools.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lc6_w1.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_ledges_a4.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_ledges_a4b.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_HugeThings_run.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_Wasteland_run.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_Player_load1.log   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_Player_load2.log   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_Player_load3.log   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_compose_apply.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_compose_plan.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_criteria.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_deploy_apply.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_deploy_dryrun.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_harvest.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_checks6_liquidheat.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_live_ledge_chain.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lt.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lt2.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_lt3.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe2.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_closename.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_kits.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_pawns.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_research.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_rr.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_ruins.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_probe_size.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun19a_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun19b_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun20a_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun20b_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun20c_20261003.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004i.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004j.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_b1_20261004k.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_b2_20261004l.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_b3_20261004m.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_Forge_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch1_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch2_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_reset_stillsand.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_reviewFW4_20261005.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_setbg.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_sum.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_titanic_cctor_20261008.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_titanic_cctor_criteria.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe2.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe3.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe4.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/belt_watchers_probe5.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/desk_muffalo.bmp   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/desk_muffalo.png   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/desk_muffalo_crop.png   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_111942_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_112136_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_115503_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_115726_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_141130_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_192249_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_192717_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_193911_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_194127_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_194450_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_195412_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_195845_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_200302_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_200559_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_201552_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/enact_test_sheet_20261008_205124_jobs.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_doing_offline_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_00   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_01   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_02   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_03   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_fw_reviewmap_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_fw_v2_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_gss_proof_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/foundry_kits_rerun_20261006.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_A.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_B.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_EXT.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_RES.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot3.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_boot4.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA2.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsB.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_cover.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext1.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext3.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext4.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext5.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_ext6.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso1.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso3.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso4.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_iso5.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_plotA.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_plots.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_probe.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_probe2.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_probe3.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv1.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv3.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riv4.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_rivercount.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite2.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite3.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.progress   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.progress   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.progress   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_settings.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_weir.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_ovn_works.out   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fw_review_map_build_log.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/fwvisuals_serve.log   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/gpt_rimflow_review_20261007.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/gpt_watchers_enrichment_20261008.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/gpt_watchers_prompt_20261008.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/gptreview_TerminalBiomes.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/gptrun_terminal.log   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/list_tools.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_art_poles_20261004/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_densify_human_review_notes.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_full_plan_run2_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_full_plan_run3_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_full_plan_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_live_run2_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots_pass1/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots2_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec2_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec3_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec4_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_rec_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_matrix_run_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r4/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r5/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r6/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r7/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_probe_aerial_after_load.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_read_settings.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_relaunch2_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_relaunch_20261004.txt   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_scenes_20261004.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_time_calls.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/mc_time_calls2.py   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_01_open.png   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T053520Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T053520Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T060517Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T060517Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T141026Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261008T141026Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Contagion_20261008T180840Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162026Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162026Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162455Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162455Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162938Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261008T162938Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Droidworks_20261008T164227Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Droidworks_20261008T164227Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/FallLineArrivals_20261008T164348Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/FallLineArrivals_20261008T164348Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/FloodedCanyon_20261008T181336Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/FloodedCanyon_20261008T181336Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261008T054429Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261008T054429Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162237Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162237Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162557Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162557Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162710Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162710Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162816Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261008T162816Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T053605Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T053605Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T060512Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T060512Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141235Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141235Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141349Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141349Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141407Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T141407Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/HugeThings_20261008T172200Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T145909Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T145909Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T151443Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T151443Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T153646Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T153646Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T164403Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261008T164403Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152152Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152152Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152418Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152418Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152627Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T152627Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T153038Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Ninefold_20261008T153038Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T055017Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T055017Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141053Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141053Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141134Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261008T141134Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261008T154155Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261008T154155Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T055021Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T055021Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141200Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141200Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141210Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261008T141210Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261008T054730Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261008T054730Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T053530Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T053530Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T060204Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T060204Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140846Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140846Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140950Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261008T140950Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161034Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161034Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161128Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161128Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161806Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261008T161806Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/UnfinishedLine_20261008T164359Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/UnfinishedLine_20261008T164359Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142004Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142004Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142437Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142437Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142736Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T142736Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T143247Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261008T143247Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Wasteland_20261008T173848Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/Wasteland_20261008T175942Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/WreckedMachines_20261008T164044Z.html   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/WreckedMachines_20261008T164044Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/modcheck/surprises/20261008T212550/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/northstar/Greentide_20261003T102251Z.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/refused_toll_rite_20261006.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/review_pyrelands_20261006.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/unfinished_line_world_20261006.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? Transient/venomvine_forms_20261006.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? conversations/   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-ishko.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-live_20261008.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-live_20261008b.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.before-tier-watchers_live.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261005T142015.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? deployed/config/ns_flowworks_backup.20261005T161529.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? infrastructure/state/items/SHIPVERMIN_FREE_TIER_BEASTS_1.md   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
?? src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll.srchash   FOUNDRY helpers' scratch from tonight's belt runs; Transient shelf life ~14 days
```

