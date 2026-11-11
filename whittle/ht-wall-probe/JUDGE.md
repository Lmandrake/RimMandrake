Independent judgment: **PASS for TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS, within the stated diagnostic-repair scope.** I did not build this work. I read STATEMENT.md and NOTES.md, current changed Python, the relevant C# implementation, before/final/first-run source comparisons, manifests, both raw live payloads and row receipts, process outputs/return codes, restoration records, every retained preflight row, host identity receipts, and startup/post-probe exception inspections. I did not read the excluded reports, prompts, builder messages, parent conclusions, or previous verdicts. My checks used local files and pure/fake Python calls; I did not access the game or bridge. This review writes only JUDGE.md.

1. **True — the diagnostic explicitly tests default Walls/Slots and legacy wake, with the specified opposite wall expectations and forced-out controls.**

   Source: `src/RimMandrake/HugeThings/northstar/titan_test_races_live.py:170` (`judge_roof`), `:210` (`roofwall_row`), and `:300` (full-runner integration). The row runs slots True then False, invokes T2 and control in each, pins successful calls to one cell, and reads all five prerequisite/mode fields before and after each probe. `RM_HugeThingsSettings.cs:96` defines WallsSlotsActive from the same four gates. `TitanicWakeProcessor.cs:41` processes roofs before crushables; `:127` skips walls/doors when WallsSlotsActive, while `:142` retains legacy Crush damage. `TitanValidationHooks.cs:184` plants RoofConstructed and a WoodLog wall, records positive initial HP, assigns `p.Position = east`, reads outcomes, and cleans up its fixture. The C# hook and processor are byte-identical to their before snapshots; this repairs the Python expectation without altering game behavior.

   Evidence: [successful raw payload](evidence/live_run_2/live.json), zero-based `calls[119]`, `[135]`, `[156]`, `[173]`, each with successful completed operations; [probe stdout](evidence/live_run_2/probe.stdout), [process rc](evidence/live_run_2/probe.rc), and [row receipt](evidence/live_run_2/live_rows.json). All four calls use `103,103`; the wall is placed east at `104,103`.

   | Measured mode | Subject / reported tier | Roof afterward | Wall HP | Destroyed |
   |---|---|---|---|---|
   | Walls/Slots True | T2Adult / T2 | none | 195 → 195 | False |
   | Walls/Slots True | T2Control / None | RoofConstructed | 195 → 195 | False |
   | Walls/Slots False | T2Adult / T2 | none | 195 → 135 | False |
   | Walls/Slots False | T2Control / None | RoofConstructed | 195 → 195 | False |

   The other four mode fields read `True` throughout. TierReport independently reports both subjects at bodySize 8.0, with T2/wakeComp=True versus None/wakeComp=False. The raw first attempt reproduces these outcomes too.

   Limitation: this demonstrates one direct Position assignment per arm, on harness races and a constructed roof/wood wall. It does not establish natural wall clearing, pathfinding, a clearing job, general crossing, other materials/tiers/roof types, or flight. Legacy damage here leaves the wall standing.

2. **True — the checker requires measured, non-vacuous data, rejects wrong outcomes and missing controls, preserves strict gameplay aggregation, and accurately describes this probe.**

   Source: `judge_roof` requires the five measured boolean strings, enabled prerequisites, full-string parsing, positive starting HP for both subjects, bounded final HP, consistent destruction flags, exact subject/tier identities, the expected roof outcomes, and mode-specific wall outcomes. Missing/malformed/inconsistent measurements return no verdict; valid wrong outcomes return FAIL. `roofwall_row` requires both complete arms, successful hooks, stable measured modes, successful cleanup where supplied, and exact raw setting restoration. Its error/restoration paths cannot produce PASS. The original five required IDs remain unchanged. `verdict` uses `live_results.aggregate(...)["gameplay_pass"]`; MOD FAIL classification, missing rows, duplicates and UNMEASURED cannot count as gameplay success. The bounded wrapper explicitly requires only R4 and reports its limited scope; that does not satisfy the full five-row runner.

   Evidence: [source diff](evidence/source.diff), current `selftest_hugethings_test_races.py:125`, `:180`, and `:224`, plus recorded test stdout/stderr/rc. The pre-fix run is RED, rc 1, 117/166; the initial repaired detailed run is 189/189, rc 0. The later [residue-fix detailed stdout](evidence/residue_fix_tests_detail.stdout) is 195/195, [rc 0](evidence/residue_fix_tests_detail.rc), empty stderr. Its six added checks reject leftover walls, control residue, unknown filth and out-of-bounds cleanup. The retained postfix, post-review, final and residue-fix harness runs each actually ran one test and report PASS/rc 0; their cache lines explicitly say the result was not recordable because the test changed. I do not treat those as cached proof. Independently, I ran the current `judges`, `roofwall_modes`, and `roofwall_residue` functions under `python3 -B`: **112/112 passed**, process rc 0, with fake runners and no game/bridge calls. Rejudging the stored raw arm outcomes also gives PASS for each mode.

   The first live attempt still exits 1 and remains UNMEASURED despite correct wall/roof outcomes because legacy damage leaves rubble. The second wrapper permits only measured T2 rubble of two named defs within the rectangle to be removed; it cannot remove a remaining wall into a pass. That is a justified fixture-cleanup repair, not relaxed outcome checking.

   Limitation: the tests do not exhaust all possible failures. The pure checker trusts supplied hook text/readbacks; it is not an independent observer inside the engine. The original compatibility row ID still says “crushes_walls,” but its documentation and emitted detail explicitly say Position-setter teleport, L1, and no path/job. No full five-row gameplay acceptance is claimed by the R4-only live run.

3. **True — the retained successful SteveDesktop run demonstrates the scoped results under the intended all-five-DLC tier, with host protection, scene/settings restoration, process evidence and applicable preflight passes. This independent review passes that scoped work.**

   Evidence: [successful attempt receipt](evidence/live_run_2/receipt.json), [raw live payload](evidence/live_run_2/live.json), both offline/live preflights and their stdout/rc, `running_identity.stdout`, `guard_before.stdout`, `lease_before.stdout`, `lease_live.stdout`, shutdown/release receipts, and [retake chain](evidence/retake_chain.json). The ordered running list contains Harmony, Core, Royalty, Ideology, Biotech, Anomaly, Odyssey, RimBridgeServer, SimpleCameraSetting, GimmeSomeSlack, FlowWorks, HugeThings, HugeThingsTestRaces and Patches. L04 confirms that ordered list against the intended modset. L01 and process receipts agree on successful-run PID 37596, start 10:51:36Z, port 5174; the earlier attempt used PID 13480.

   The applicable SteveDesktop lock is `/mnt/d/RimTest/data/scratch/DRIVER_LOCK.json`: BENCH, PID 2786427, start 83570.41, boot ID `83c87369-52bb-43a4-9179-a6cd07ce769d`, platform wsl, host SteveDesktop. Generation 1394 was released to FREE after attempt 1; retake records the same complete driver identity at generation 1395. Before/live lease receipts agree; after attempt 2 the game is stopped, the lease released and the guard FREE. Game status rc 3 before/after means stopped, not failed probing. Probe rc is 1 for attempt 1 and 0 for attempt 2; the remaining per-attempt captured commands exit 0.

   I checked all rows of `readiness_offline.json`, both attempts' `preflight_offline.json`, and both `preflight_live.json`, including optional rows. Every retained row reports PASS and every report is GREEN. The following covers every row ID present:

   | Rows | Recorded result / applicability |
   |---|---|
   | O01 game_down | PASS: no process offline, exactly one live |
   | O02 bridge_lease | Recorded PASS, **not applicable to SteveDesktop** |
   | O03 disk_space | PASS: C 25.1 GB, D 10019.4 GB |
   | O04 modsconfig_intent | PASS: intended ordered 14-mod list |
   | O05 list_sane | PASS: no duplicates/composed/uninstalled IDs |
   | O06 ship_coverage | PASS: deliberately partial test tier |
   | O07 known_wedgers | PASS |
   | O08 player_log_archive | PASS: archive paths retained |
   | O09 companion_match | PASS: repo/deployed bytes and build match |
   | O10 dependency_fp | PASS |
   | O11 bridge_lint_fresh | PASS: 431 declared tools |
   | O12 src_load_killers | PASS |
   | O13 deploy_match | PASS: five mods, 1211 files equal |
   | O14 effective_def_lint | PASS: cached effective lint |
   | L01 live_identity | PASS: process/log/listener identity |
   | L02 live_core_reset | PASS |
   | L03 live_first_exception | PASS: no missing types, no Config errors, no first exception |
   | L04 live_mods_ordered | PASS: direct ordered running-list read |
   | L05 live_companion | PASS: 431 tools, build 54acba048eda |
   | L06 live_tps_autostart | PASS |
   | L07 live_awareness_init | PASS |

   O02 is precisely the NOTES.md exception: `preflight_bridge.py:54,198` reads the clone's host-unspecific `infrastructure/state/BRIDGE`, not SteveDesktop's lock. Its “FREE” does not prove SteveDesktop ownership. The applicable host/identity receipts above supply that evidence; no other row is excused.

   The probe loads existing `RM_TestSite_calm_v3`, saves and reloads `CODEX_RoofWall_Begin_20261111T025305_037aabe8`, and finally reloads the same scene-begin save. No worldgen call or flight demonstration appears in the recorded calls. Ticks stay 3 → 3. All four post-probe censuses have zero pawns/things, 576 unroofed cells, and the empty-rectangle fingerprint. The legacy T2 alone leaves one `Filth_RubbleBuilding` at 105,102; one Filth-only destroy call removes it and preserves the measured 195 → 135 wall result. Planted roof and wood-wall controls each change the fingerprint, and removing them restores it. Final scene hash equals baseline: `77d77850802c774359012d945e7ffcbaf29d807aae0f525569b0978b764239a8`, beds=0, for rectangle `92,92,24,24`.

   All five touched HugeThings fields and three touched debug fields restore to their original raw `True` strings with successful readbacks. Difficulty restores threatScale=1.0 and allowBigThreats=True; all five recorded difficulty values match the original dictionary. Restoration reports attempted=True, ok=True, errors=[]. Raw final calls corroborate those summaries. Both attempts retain zero exception/config counts at startup and after probing; L03 independently supplies the startup inspection.

   Provenance: all eight current source/artifact entries and 76 allowed raw-file entries checked against `evidence_manifest.json` match size/hash; excluded review/prompt material was not opened. Final snapshots equal current files. All 50 HugeThings stamped source inputs match, and repo, recorded deployed and loaded DLL hashes agree at `e1d1b0623922831d9b3ce52f8da24678b1585e66c6c97c29dca8a3edc50ee5d0`. The successful wrapper records its current SHA-256 `da44636359faf6beadbafc8c72f1d680b734f75c6d9beca94bd029628e3da49a`. STATEMENT/NOTES match their initial frozen hashes.

   Exact limitations: restoration is a scene-begin reload plus equality of the measured rectangle and touched setting values, not a byte-for-byte comparison of the entire game/world or restoration of an earlier user session. `RM_PitPrisonProof.Rect` fingerprints terrain/underterrain, roofs, excavation/fluid state and listed thing identity/def/count/HP/position; it does not serialize every pawn, building or world field. Startup/post-probe evidence is retained inspection output, not a complete archived current-run log independently rescanned here. O09 expressly lacks companion source-stamp provenance; O14 uses a cache and excludes donor_types. These are reported bounds, not concealed nonpassing rows. Attempt 1's manifest snapshot pointers still name `source_final`; its matching older wrapper/tests are actually in `live_run_1/source_at_run`. Also `final_tests_detail` predates the six residue tests; `residue_fix_tests_detail` supplies the final 195-check detail. These packaging imperfections do not break the independently verified source/raw-result chain.

This verdict accepts the repaired diagnostic expectation and its bounded evidence only. Natural wall clearing, general crossing and flight remain unestablished by this work.

would show: yes
