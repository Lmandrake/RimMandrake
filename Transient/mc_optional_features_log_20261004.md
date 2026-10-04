# MessyConduit optional features log 2026-10-04

- 11:38 start: skeleton
- 11:38 read design 1.5/2.5, SectionLayer, CordMaterials, CordGraph comp motion, CordMotion
- 11:40 design settled: swayMode CPU|Shader (CutoutPlant, auto-registered by MaterialPool, auto-fallback to CPU), floorRipple default off; rows B7b_sway_shader_path, B7c_floor_ripple replace the two UNBUILT rows
- 11:43 code written (Core Ripple/ShaderSwayAlpha + selftest, settings, CordMaterials plant strand, layer, comp, probe, validation rows); running offline
- 11:43 offline 6/6 PASS (selftest incl. shader alpha + ripple checks); building
- 11:44 built, deployed, game relaunched (bridge up 33s); running validation --live --fresh-map
- 11:46 live run validation_result_20261004T114613.json: 42 PASS, B7b + B7c PASS
- 11:47 visible check: shader_sway_look.py (OS captures, off/cpu/shader/shader_roofed)
- 11:48 look run 1 inconclusive: whole-screen diff counted terminals + grass sway (~2.4k px noise every mode); rerun cropped at min zoom
- 11:49 look run 2 (cropped, min zoom): changed px off 0/0, cpu 13/2, shader 25/23, shader_roofed 0/0; red diff sits on the tail -> shader route VISIBLY moves (measured positive). Evidence Transient/mc_shader_sway_look_20261004/{result.json,look_sheet.png}
- 11:49 --save-load PASS (validation_save-load_20261004T114931.json); aerial/hose live next
- 11:51 aerial live 18 PASS; hose live run; matrix next (~6 min)
- 11:59 matrix matrix_live_20261004T1152.json done; committing then recording
- 12:02 run_selftests 172/173 (only failure src/RimUtinni/UtinniPatches/selftest_utinnipatches_dump.py, unrelated); publishing
- 12:03 record core REFUSED: STALE (run at dff0b5f00e86, mod now 49214331977a -- shader_sway_look.py added to the mod folder after the run). Re-running core live + save-load at 49214
- 12:05 re-run at 49214: core validation_result_20261004T120435.json (42 PASS) recorded REFUSED on U_motion_look UNCOVERED, U_style_missing_art UNBUILT, M4_save_load_hash UNCOVERED (covered by validation_save-load_20261004T120447.json PASS), M9_remove_mod_clean UNCOVERED (paused); matrix_live_20261004T1152.json recorded GREEN (121 PASS, 1 SKIP). Done.
