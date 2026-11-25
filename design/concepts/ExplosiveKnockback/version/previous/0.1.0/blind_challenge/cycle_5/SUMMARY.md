# ExplosiveKnockback 0.1.0, blind challenge cycle 5 (judge-1794890427)

## Start time
2026-11-17T04:41:13Z (2026-11-16 20:41 PST)

## Changed files to bars
`git diff --name-only d3cf239cf2 origin/main -- <the brief's paths> | grep -v /blind_challenge/`: 432 files [measured]; 395 are ledger shards/views, criterion-repair evidence and in-game run logs (no bar input). The rest, mapped by what each file feeds (lane-1 scope):

| changed file | bars whose inputs it touches |
|---|---|
| `Source/RM_KnockbackMath.cs` (+49) | **inv_kernel**; every kernel-fed leaf; barrage_frame_budget, frame_time_probe (KbFrameStats p99 window) |
| `Source/RM_KnockbackProof.cs`, `_StageThree.cs`, `_StoreroomBombPit.cs`, `_GoodsObstacles.cs`, `_PitProbe.cs` (new) | **inv_proof_scenes**; the scenes they stage (sc_barrage_perf, sc_storeroom_bomb_pit, sc_goods_obstacles, pit scenes) |
| `Source/RM_KnockbackCompat.cs` (+63) | inv_hook, inv_pits_receive, thrown_into_pit_falls, blast_breaks_pit_cover, our_gases_burn (FlowWorks/Cauldron bridges) |
| `Source/RM_MapComponent_Knockback.cs` (+36) | the hook's game side: every_good_moves, closed_container_holds, gas_goes_clump_by_clump, thrown_into_pit_falls, the_spared |
| `Source/RM_PawnFlyerPatches.cs` (+41) | pawn_flight_arc, inv_pawn_flyer, thrown_into_pit_falls, recovery_immunity |
| `Source/RM_ThingFlyer_Knockback.cs` (+8) | goods_arc_spin_rebound, heavy_stack_knocks, no_teleport, inv_goods_fly |
| `Source/RimMandrake_ExplosiveKnockback.csproj`, `Assemblies/*.dll(.srchash)` | build of all of the above |
| `Source/SelfTest/Program.cs`, `selftest_explosiveknockback_{barrage_p99,gas_clumps,gas_into_pit,landing_job_search,pit_fetch,stage6_visit2,storeroom_bomb_pit,walk_raid}.py`, `Utils/selftest_settings_screens.py` | tests of inv_kernel (T_KERNEL) and of the stage-6 bars named in their files |
| `validation.py` | walk_storeroom_raid (FRAME_BUDGET now mod-on vs mod-off) |
| locked: `tree.json`, `scenes.json`, `plan.md`, `version/bars.md` (changed lines name only barrage_frame_budget, walk_storeroom_raid, sc_barrage_perf, sc_walk_raid, dl_perf_budget); `sheet.md`, `record.json` changed with no bar id on a changed line | barrage_frame_budget, walk_storeroom_raid |
| `stage.json`, `version/stage_record.json`, `run_spend.jsonl`, `test_table.*`, `pilot_throwaway/make_test_table.py`, `journal.md` | pipeline state, no bar input |

Lane-1 inputs read: tree.json, sheet.md, plan.md, version/VERSION.json, version/bars.md, the record.json inventory rows inv_kernel and inv_proof_scenes (their bar text), scenes.json's entry_point fields, RM_KnockbackMod.cs, Patches/, Defs/ (listed only), RM_KnockbackMath.cs, RM_KnockbackProof*.cs, proof_build_gate.py.

## Lane 1
`python3 lane1/run_lane1.py` (BlindLane1.cs on the shipped RM_KnockbackMath.cs, built with the Windows dotnet under `D:\ClaudeWork\rimmandrake\scratch\explosiveknockback_blind_c5_lane1\`; BlindLane1.py on the settings, the type patch, the proof gate and the scenes' entry points): **96 rows: 33 PASS, 6 INFO, 0 FAIL, 57 UNSETTLED** [measured], every UNSETTLED a `not_kernel` row on a stage-6 bar (none names inv_kernel or inv_proof_scenes). Seeds 50501-50510 are in each random row's detail. On my first runs three rows FAILED on my own oracle bugs, fixed before recording (wall impact expected for the wrong cell count; the entry-point tokenizer read `src` out of a path; fall-through `case` labels with a trailing comment). Six INFO rows name things lane 2 must read in the callers: a thrown pawn landing on a cover (the kernel leaves it to FlowWorks), the gas shove onto a pit (ShoveCellFree refuses pits, so the gas shove must not use it), the max-6 cap clipping goods' 1.6x near a blast, fire's exact half rounding to 1 cell of 3 at the calibration point, independent landing-stun min/max sliders, no extra tuned types.

## Lane 2 reruns
`python3 lane2/rerun_offline.py` at a898e049d4: **16 of 16 offline tests PASS; verdicts match runs_today 16 of 16** [measured]; last lines match 15 of 16 strictly (T_FUZZ differs only in its timing figure, 1.49 s vs 1.63 s; the compare now masks seconds). Deciders of the offline bars: T_KERNEL 191/191, T_FUZZ OK (inv_kernel); T_SCRIPT, T_PROOFGATE, T_RESTORE PASS (inv_proof_scenes). After the fix at 42225e0686: 16 of 16 PASS (`lane2/reruns_after_fix.jsonl`; T_KERNEL 198/198 with K-25, so 14 of 16 last lines match).

## Planted
`lane2/plant_faults.py` (WINBUILD_ROOT private), 55 faults over 13 offline suites plus blind lane 1, baseline all green, **tree clean after** [measured]:
- **Kernel RM_KnockbackMath.cs: 20 of 20 caught** by the builder's T_KERNEL/T_FUZZ, and 20 of 20 by blind lane 1 too.
- Proof gate: 2 of 2 caught (T_PROOFGATE). Proof scenes: a dropped scene name (T_STAGE3_SCENES) and the proof type not built (T_PROOFGATE) caught; **9 verdict/plan faults survived** every offline test (calibration any cells, storeroom plan mass limit and plain kernel, goods-obstacle control never fails and door lane without rebound, hose control always passes and three-cells dropped, pit probe INVALID never and INVALID text) -> RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN.
- Settings (RM_KnockbackMod.cs): 3 of 3 caught. csproj: 2 of 2 caught.
- Game-side callers: 7 caught offline (gas cap 3, gas reburst, closed-guard switch, vent-gas burst, closed-container read), **11 survived**: 10 Verse callers (grid pawn read, in-bed skip, inventory mass, rebound, heavy knock, landing cover break, no-redirect, landing door, unpatched percent, fire switch) and validation.py's FRAME_BUDGET judge (2 faults).
- Totals: **34 of 55 caught** (34 by a builder suite, 26 by lane 1) [measured].

## Faults
`lane2/faults.json`, each filed as a rimflow item (`--caused-by RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FIVE`) and as a mod-ledger finding.open:

| id | class | bar | status | miss_of |
|---|---|---|---|---|
| RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER | Problem | pawn_hits_pawn_stops | FIXED 42225e0686 | 4 |
| RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND | Problem | thrown_into_pit_falls | PENDING (acceptance test `lane2/accept_covered_pit.py`, 2 of 6 on 42225e0686) | 4 |
| RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN | Problem | inv_proof_scenes | NOTED_FOR_CONDUCTOR (re-pin: verdict honesty is a live read) | - |
| RIMMANDRAKE_SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS | Polish | gas_goes_clump_by_clump | PENDING | 4 |
| RIMMANDRAKE_TEST_WALK_FRAME_JUDGE_OFFLINE_TWO_MUTANTS_LIVED | Polish | walk_storeroom_raid | PENDING | - |
| RIMMANDRAKE_NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX | Polish | stage-6 caller bars | NOTED_FOR_CONDUCTOR | - |

Both code Problems are in material unchanged since cycle 4 (RM_MapKbGrid.At, the kernel's CoveredPit rule, K-08, the pit_colonist scene), so they are misses of the earlier judges. Both came from reading the callers after lane 1's INFO rows on pits (as FORMAT_NOTES predicted: the kernel was right in itself; the grid and the landing were short).

**Verification of claimed fixes** (`maturation_dispatch.py judge-verify`): 16 findings, **16 verified, 0 reopened** [measured], each by rerunning its claim's test or my own planted faults and lane-1 rows at 42225e0686 (mod-ledger finding.verified).

## Fixes
`lane2/fixes.jsonl`: RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER at **42225e0686**: `RM_KnockbackMath.PitCell` (a pawn on a cover's deck or an open pit's floor blocks a thrown pawn), `RM_MapKbGrid.At` answers superdeep cells through it and ignores a pawn beneath the lid (`RM_KnockbackCompat.IsBeneathCover`), K-25 in SelfTest/Program.cs, release DLL and .srchash rebuilt (proof build compiles too). Red: `lane2/check_pit_pawn.py --rev a898e049d4` rc 1, and T_KERNEL with K-25 against the parent kernel rc 1 (CS0117, no PitCell). Green at 42225e0686: check rc 0 (6 of 6 and the wiring), T_KERNEL 198/198. Lane 1 rerun after the fix: `lane2/lane1_rows_after_fix.jsonl` 33 PASS, 0 FAIL. The four changed source files were already DIRTY by `code_review_status.py` before this cycle; not marked clean (no full-file review here).

## Steward's decisions enacted
- 2026-11-15 7:37 PM PST re-pin (sc_barrage_perf, RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO): barrage_frame_budget judged as the p99 unpaused frame inside 0.9-8.25 s at most 50 ms. Lane 1 K_BARRAGE_P99_AND_PROBE tests KbFrameStats that way (PASS); planted worst-frame and window-ignored faults are caught by T_KERNEL. Recorded `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (OWNER.jsonl).

## Tests edited
`tests_edited.json`: `src/RimMandrake/ExplosiveKnockback/Source/SelfTest/Program.cs`, K-25 added (7 checks); no assertion changed or removed. New judge-side checks (not builder tests): `lane2/check_pit_pawn.py`, `lane2/accept_covered_pit.py`.

## Unsettled
- 57 lane-1 `not_kernel` rows (every stage-6 bar's game-side half), owed to Stage 6; none names an offline bar.
- Whether the proof scenes' verdicts are honest cannot be shown offline (NOTED, above).
- K-08's "cover is ground" encodes the older design; the fix for the covered-pit Problem must change it to follow sc_pit_fall (a test edit the next fixer lists).

## Exit
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 2
exit_met: false

## Owed
- RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND: the holder fixes it (smallest fix in faults.json; acceptance `lane2/accept_covered_pit.py` 6 of 6; live sc_pit_fall covered lane).
- RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN: the steward re-pins inv_proof_scenes' offline half, or the verdicts are lifted into a kernel.
- A new blind judge (this cycle fixed a Problem).
- test_table.json's runs_today predate the fix: `maturation.py next` refuses the judge certificate on T_KERNEL's build hash (now d0aad1b433, recorded c7742f1424); the table's next refresh takes the reruns in `lane2/reruns_after_fix.jsonl`.
- `maturation.py next` after this record: only substance reasons remain (exit_met false; the two Problems not FIXED). Wall time: 04:41-~06:15 UTC [measured from `date`].
