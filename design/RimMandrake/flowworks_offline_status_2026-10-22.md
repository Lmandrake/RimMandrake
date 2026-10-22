# FlowWorks offline status 2026-10-22

Run one test at a time via `run_selftests.py --only`, base 36d07dde2. Logs: `D:\ClaudeWork\rimmandrake\scratch\fw_offline`.

| selftest | first run | after fixes | note |
|---|---|---|---|
| selftest_flowworks_belt_fixes_h.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_call_sites.py | PASS (1.1s) | PASS |  |
| selftest_flowworks_cover_breaks.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_drawbridge_art.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_driver_rows.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_fuel_moat.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_gpt_b.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_gpt_c.py | PASS (0.2s) | PASS |  |
| selftest_flowworks_looks_round.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_pipe_pole_art.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_review1022_excavation.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_review1022_liquidnet.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_review1022_sheet.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_review1022_superdeep.py | PASS (0.1s) | PASS |  |
| selftest_flowworks_river_colors.py | PASS (0.2s) | PASS |  |
| selftest_flowworks_rivers.py | FAIL (0.1s) | PASS | test pattern stale after settings window moved to a Block() method group; pattern updated, same intent |
| selftest_flowworks_suspension_art.py | PASS (26.4s) | PASS |  |
| selftest_flowworks_suspension_linked.py | PASS (1.0s) | PASS |  |
| selftest_flowworks_swale.py | PASS (0.1s) | PASS |  |
| selftest_hose_port.py | FAIL (0.5s) | PASS | python mirror lacked 2 credit tags the C# CreditTags already carry (pump overflow spill, gravity overflow); added |
| selftest_hose_ports.py | PASS (0.9s) | PASS |  |
| selftest_liquid_look_tune.py | PASS (0.1s) | PASS |  |
| selftest_review_map.py | PASS (6.7s) | PASS |  |
| selftest_settings_search.py | PASS (0.7s) | PASS |  |
| selftest_flowworks_stock.py | PASS (97.8s) | PASS |  |
| selftest_flowworks_sheet.py | PASS (55.7s) | PASS |  |
| selftest_lint_harmony_targets.py | FAIL (1.9s) | PASS | 8 FlowWorks patch classes lacked [PatchFeature] (added, label only); lint regex mis-counted typeof(TipSignal?) arity (fixed) |
| selftest_modmanifest.py | PASS (0.1s) | PASS |  |
| selftest_mayrequire_folded.py | PASS (0.4s) | PASS |  |
| selftest_winstage.py | PASS (0.3s) | PASS |  |
| selftest_pyrelands_fuzz.py | PASS (17.3s) | PASS |  |
| selftest_settings_screens.py | PASS (0.9s) | PASS |  |
| selftest_static_game_state.py | FAIL (0.1s) | PASS | 6 new statics reviewed and listed with reasons (none is per-game state) |
| selftest_harvest_donor_free.py | PASS (1.9s) | PASS |  |
| selftest_flowworks_trench_cover.py | PASS (63.2s) | PASS |  |
| selftest_proof_preconditions.py | PASS (1.4s) | PASS |  |
| selftest_world_layers_export.py | PASS (0.2s) | PASS |  |

## C# SelfTest and DLL stamp
- FlowWorks SelfTest (`RimMandrakeFlowWorks.SelfTest.exe`, built 16:35 from merged source via `selftest_winstage` full-src stage): rc=0, 830 ok, 0 FAIL. The repo `bin/Release/net8.0` exe is stale; and a plain `winbuild.py` stage lacks Defs/Patches, so run it only from a full-src stage (17 false FAILs otherwise: missing files, not verdicts).
- `dll_source_stamp.py check`: `RimMandrakeFlowWorks.dll` MATCH. It was rebuilt through `winbuild.py FlowWorks` after the PatchFeature source edits; DLL and `.srchash` committed with them.

## trench selftest rc=24
`winstage.windows_project_path` stages the clone's whole `src/` via `rsync --delete`; rsync exit 24 means "source files vanished" - another agent saved a file mid-copy. A staging race, not a test verdict (the trench selftest passed 63.2 s when the tree was quiet). `winbuild.stage_build` now retries rsync 24 up to 3 times.
