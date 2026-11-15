# ExplosiveKnockback 0.1.0 — blind challenge cycle 3 (visit 1, cycle 1 of the visit)

Judge: BENCH detached helper, item RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_THREE.

## Start time
2026-11-15T19:42:04Z (11:42 AM PST). Precondition: `blind_challenge {'visit': 1, 'total': 3}` [measured].

## Changed files to bars
`git diff --name-only ee62a69994 origin/main -- <brief's paths> | grep -v /blind_challenge/` lists 180 files [measured] (origin/main 6dcc361c5 after `./sync`). Grouped, with the bars whose inputs each touches (lane-1 scope = these bars):

| changed file(s) | bars in scope |
|---|---|
| `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs` (KbShove/ContainerShove removed; ContainerThrowCells, JoltOffset added) | inv_kernel, inv_container_shove, inv_closed_guard, closed_container_holds, settings_scale_and_switch |
| `Source/RM_KnockbackMod.cs` (fireAtHalf, closedContainerGuard declared, saved, drawn, reset) | inv_settings, settings_scale_and_switch, every_harmful_blast_throws, closed_container_holds, inv_proof_scenes (Reset) |
| `Source/RM_KnockbackProof.cs`, `RM_KnockbackProof_GoodsObstacles.cs`, `_StageThree.cs`, `_StoreroomBombPit.cs`, `proof_build_gate.py` (unchanged), `knockback_runner.py`, `proof/storeroom_pit_proof.py`, `validation.py` | inv_proof_scenes, and the leaves those scenes prove (closed_container_holds, every_good_moves, thrown_into_pit_falls, walk_storeroom_raid, settings_scale_and_switch) |
| `Source/RM_MapComponent_Knockback.cs`, `RM_Patch_DamageWorker_ExplosionKnockback.cs`, `RM_PawnFlyerPatches.cs`, csproj, Assemblies DLL + srchash | game-side callers: closed_container_holds, every_harmful_blast_throws, pawn_flight_arc, gas_goes_clump_by_clump, inv_hook, inv_pawn_flyer, inv_container_shove |
| `Source/SelfTest/Program.cs`, `KnockbackSweep.cs`, `selftest_explosiveknockback_*.py` (11), `Utils/lint_explosiveknockback_defs.py`, `Utils/selftest_settings_screens.py` | the deciders of inv_kernel, inv_proof_scenes and settings bars (read only in lane 2) |
| locked `tree.json`, `sheet.md` (lines 36/49/64 and tree 11/19/374-390/708: closed_container_holds wording) | closed_container_holds (sheet now: "thrown a short way at or under the 250 kg container mass limit, else a jolt") |
| locked `scenes.json` (sc_blast_kinds lines and the container scenes) | every_harmful_blast_throws, closed_container_holds, settings_scale_and_switch |
| `record.json`, `stage.json`, `exam.json`, `bars.md`, `locked_bars.json`, `bar_lists_map.json`, `test_table.*`, `stage_record.json`, `run_spend.jsonl`, `criterion_repairs/**`, `in_game/visit_1/**` (stage-6 evidence), `pilot_throwaway/make_test_table.py`, `journal.md` | record-keeping; no kernel input (in_game evidence is stage 6, closed to lane 1) |

## Lane 1
Inputs read: `sheet.md`, `version/VERSION.json`, `version/bars.md`, record.json rows inv_kernel and inv_proof_scenes (their bar text), `Source/RM_KnockbackMath.cs`, `Source/RM_KnockbackMod.cs` (defaults, sliders, Reset), `Patches/*.xml`, `Source/RM_KnockbackProof.cs` (public entry points and its kernel calls only), `proof_build_gate.py`. Pattern copied from Pyrelands cycle 1 `run_lane1.py` (stage + per-user dotnet), not its tests.

Harness: `lane1/BlindLane1.cs` (my tests, the shipped kernel compiled beside it) + `lane1/run_lane1.py --kernel <file>` (stage `/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c3_lane1/`; also settings/patch/gate rows and a proof-build compile, `-p:RmProofs=true` through winbuild with the release DLL put back after).

Result [measured]: **48 rows: 33 PASS, 0 FAIL, 3 INFO, 12 UNSETTLED (all `not_kernel`, naming stage-6 leaves only)**. Random rows seed 20261115 (20000 random grids for Resolve, 50000 monotonicity cases, 3000 Prioritise, 400 ledger runs vs a reference model). Sweep: global settings through every slider range and switch (4320 configs x 3 blast configs), goods-side settings.

Two of my own test bugs were fixed before recording (not mod faults): a ledger case that ran the clock backwards (the ledger clears on a backwards clock by design) and a regex that took `goodsSpinDegPerTick` for a removed per-tick cap.

INFO worth a reader: whole-cell wild/plain ratio runs 1.00 to 2.00, mean 1.59 (the bar says "about 1.6"); the kernel passes a covered pit cell mid-flight as ground; `landingStunMin`/`landingStunMax` are independent sliders (min may exceed max).

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
