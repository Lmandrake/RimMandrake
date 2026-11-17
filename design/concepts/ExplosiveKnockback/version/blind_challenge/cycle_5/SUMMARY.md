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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
