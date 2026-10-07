# FlowWorks art + muffalo + review map — progress 2026-10-06

Relaunch after OOM death. One line per milestone.

- 23:01 start
- 23:02 requeued all 11 failed fwart jobs (all codex worker_error schema flake) failed/->pending/, manifests parked in _requeued_manifests/
- 23:07 art: 31 of 37 finished jobs installed via art.py ledger (artpipe-collect), cbd58e889 pushed. HELD: RM_Bottle (glass bottle contradicts owner brief 386d51170 patchwork-metal matching set; bucket/barrel still pending) and 5 terrain surfaces Channel_Mid/DeepSand/Fill_Tar_Brim/Fill_Water_Brim/Fill_Water_Half (transparent feathered borders, not seamless tiles - unusable as TerrainDef textures; need re-commission as opaque tileable)
- 23:10 defs + designator icons wired, FlowWorks DLL rebuilt: ca1e656be pushed (first push of it, 85dfbd3e3, was dropped when a peer reset main mid-publish; cherry-picked back)
- 23:13 muffalo (PIT_LIP_OCCLUDES_OUTSIDE_1): sink clamped so drawn centre stays north of the near lip + lip cover sized from the animal's real drawSize; selftest 111/111; a100d8e2e pushed. Live re-shoot of RM_pitlip_muffalo_bug_20261006 owed in the bridge session
- 23:17 scenes: depth_fill (step-cost Harmony postfix on an inlined static never ran -> moved to PathGrid.CalculatedCostAt prefix), fire (ruling 13 detonation consumed at once, implemented + scene waits a pulse); 3425843d9 pushed. sluice grate/open 'held' not root-caused offline (doors are invisible to the kernel by design) - live probe owed
- 23:22 live (flowworks tier, restarted for new DLLs): full recipe then fixes; depth_fill PASS, fire PASS, sluice XFAIL (grate+open pass, shut passes = expected until FLOWWORKS_SLUICE_TWO_DOORS_1) fwpt_20261007T062218_s1; a7e13914f pushed
- 23:30 muffalo re-shot live (Transient/flowworks_art_muffalo/muffalo_after_fix.png): fixed. Review map rebuilt on fresh map (39 visuals + 51 gallery verified, 55 non-colonists swept), keeper RM_fw_review_20261006_art.rws (new file, no other save changed; keepers backed up to D:\Luke\dev\_rmscratch\saves_backup_20261006_fw). Screens review_art_{a,b,c}.png. Pit covers print surrounding terrain by design, so their new art only shows as the build icon. GSS dive shot skipped (no cheap scene). Bridge released.
