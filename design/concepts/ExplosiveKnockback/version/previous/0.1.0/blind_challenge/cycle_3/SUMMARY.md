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
Resumed run (the first run of this cycle was killed after committing lane 1 at 7444e5a20a). `lane2/rerun_offline.py` (cycle-1 tool via cycle 2), `WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c3_mut/`.

- **Instrument trap first** [measured]: the private stage held the killed run's dotnet bin/obj; the first rerun read T_KERNEL (and T_HEAVY_KNOCK_RULE, same command) **173/174, FAIL K-22**, again once by hand, then 174/174 on later runs without a wipe. The stage was wiped and everything rerun; the stale rows are kept in `lane2/reruns_stale_stage.jsonl` and are not evidence about the mod. Lesson filed (`infrastructure/state/lessons/20261115T214812Z-BENCH-killed-run-s-private-winbuild-root.md`). Why the later runs turned green without a wipe is unknown.
- Before the fixes (`lane2/reruns.jsonl`, at f0863c4a49, clean stage): **15 of 16 match** on verdict and last line [measured]. The 16th, T_RESTORE, was recorded KNOWN RED and now **PASSES** (dac4c3f560 landed its fix after the brief was written). Every decider of an offline bar PASSES: T_KERNEL 174/174, T_FUZZ, T_SCRIPT, T_PROOFGATE, T_RESTORE. T_SETTINGS_SCREEN PASSES (856/856).
- After the fixes (`lane2/reruns_after_fix.jsonl`, at 6b3b3817fc): **16 of 16 PASS** [measured]; T_KERNEL now 180/180 (K-23 added), so its last line no longer matches the recorded 174.

## Planted
`lane2/planted_faults.json` (49), `lane2/plant_faults.py` (every offline suite of test_table.json plus the 8 builder selftests it does not list: 23 suites; T_LINT_PLANTED only for def-patch and lint faults; lane 1 without the proof build for kernel, settings and patch faults), `lane2/planted_results.jsonl` (baseline first, all 23 suites and lane 1 green; every batch ended `tree_clean_after: true`, `git diff --quiet` on the mod) [measured].

Spread: kernel 6 + 3 after the fix, settings 5, map component 8, damage patch 3 + 1 after the fix, flyer patch 2, def patch 2, proof scenes 2 + 2 + 3 + 2, proof gate 2, runner 2, storeroom proof 2, validation 2, lint 2.

- First pass (45 faults, before the fixes): **27 caught, 18 missed** [measured]. After the fixes, the 4 gate and storeroom faults re-planted are all caught, and the 4 fire-switch faults planted on the new code are all caught: 49 rows, 31 caught. No fault was caught by lane 1 alone.
- Misses that were Problems (fixed, re-planted, now caught): PF_GATE_RELEASE_OR, PF_GATE_NO_EXIT (T_PROOFGATE); PF_SPP_RESTORE_SWALLOWED, PF_SPP_PARTIAL_SNAPSHOT (T_RESTORE); the fire switch: PF_DW_ISFIRE_FLAME_ONLY and PF_DW_FIRE_SWITCHES_PROJECTILE_TUNING are superseded by the kernel move, and their kernel forms PF_KERNEL_FIRE_ELECTRICAL_DROPPED, PF_KERNEL_FIRE_SOURCE_IGNORED, PF_KERNEL_FIRE_BURN_DROPPED are caught by T_KERNEL, PF_DW_FIRE_SWITCH_READS_TRUE by T_SETTINGS_SWEEP_OFFLINE (evidence `lane2/fix_evidence/`).
- Misses that are not offline Problems: PF_MAP_CONTAINER_INTO_PITS is an equivalent mutant (ContainerCellFree refuses a pit cell either way); PF_MOD_FIRE_HALF_NOT_DRAWN wraps the checkbox in `if (false)`, contrived against a text check (the realistic removal, PF_MOD_FIRE_HALF_CHECKBOX_REMOVED, is caught); PF_MAP_GUARD_OFF_GOODS_RIDE, PF_DW_FIRE_OFF_NOT_ZERO, PF_FLYER_NO_RESUME, PF_VAL_CONTAINER_ROW_SETTING are game-side, on bars that prove at Stage 6, where T_SETTINGS_SWEEP_OFFLINE itself names the live scene as the decider; the five weakened proof verdicts and PF_MATH_JOLT_NO_DECAY are Polish (below).

## Faults
`lane2/faults.json`, each filed in rimflow (`--caused-by RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_THREE`). **3 Problems, all FIXED red first; 3 Polish, filed and open** [measured]. `miss_of: 2` (material unchanged since cycle 2): 1 Problem.

| id | class | bar | status | miss_of |
|---|---|---|---|---|
| RIMMANDRAKE_SWITCH_ELECTRICAL_BURN_WITH_FIRE_HALF_FLAME_HEIR | Problem | settings_scale_and_switch | FIXED bace1c29cc | 0 |
| RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN | Problem | inv_proof_scenes | FIXED f181d3b6ea | 2 |
| RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST | Problem | inv_proof_scenes | FIXED f181d3b6ea | 0 |
| RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN | Polish | inv_proof_scenes | PENDING (filed) | 0 |
| RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME | Polish | pawn_flight_arc | PENDING (filed) | 0 |
| RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED | Polish | closed_container_holds | PENDING (filed) | 0 |

The ElectricalBurn Problem: Anomaly's ElectricalBurn DamageDef has ParentName="Flame", so it inherits the Flame patch's force 0.5, but its hediff is ElectricalBurn, so `IsFire` (Flame, or hediff Burn) missed it and "fire throws nothing" left it throwing. The mod's own patch comment and IsFire's doc both name it as fire. No vanilla explosion uses ElectricalBurn [measured, game Data grep], so only another mod's blast shows it; the switch's live lane reads Flame's force only, so Stage 6 would not have seen it.

## Fixes
`lane2/fixes.jsonl`; every command run for real at both shas [measured]:
- f181d3b6ea: T_PROOFGATE G1 checks another type's "Type not found", a proof-type error and require_proof_build's exit 3 and return; T_RESTORE section 7 runs storeroom_pit_proof.py's waived snapshot and restore from the real source against a fake bridge, with two in-memory mutants. Red: `plant_faults.py --expect-caught` rc 1 at f0863c4a49 (both pairs missed); green rc 0 at f181d3b6ea.
- 7450887f29 moves the parent's fire rule unchanged into the kernel (`RM_KnockbackMath.FireSwitchedOff` / `IsFireDamage`, the caller passes `fireAtHalf`, source, defName, hediff) and adds T_KERNEL K-23: **red**, 179/180 (K-23 ElectricalBurn). bace1c29cc names ElectricalBurn: **green**, 180/180. Release DLL and `.srchash` rebuilt from source at both (winbuild, private root), never deployed.
- Lane 1 rerun at the fix (`lane2/lane1_rows_after_fix.jsonl`): 48 rows, 33 PASS, 0 FAIL, 3 INFO, 12 UNSETTLED, the same as recorded blind [measured].

## Steward's decisions enacted
Both recorded with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (OWNER.jsonl):
- A (sc_storeroom_mortar re-pinned to the whole-cell band): lane 1's INFO `info_wild_ratio_whole_cells` (ratio 1.00 to 2.00, mean 1.59) is the reason for the repair, not a fault; nothing filed.
- B (containers "thrown a short way"): judged so (at least one cell, never past the cap, action thrown); lane 1's `fx_closed_container_holds_and_short_throw` read it that way; no fault against the held tree/sheet wording.

## Tests edited
`tests_edited.json` (before/after blobs; no assertion weakened, skipped or deleted): `selftest_explosiveknockback_proofgate.py` (G1 extended), `Utils/selftest_proof_restore_check.py` (section 7 added), `Source/SelfTest/Program.cs` (K-23 added). Selftests run before each commit with `run_selftests.py --only`: GREEN.

## Unsettled
- Lane 1's 12 `not_kernel` rows (all naming Stage-6 leaves only) stay UNSETTLED, owed to Stage 6.
- Whether the live closedGuard lane (`lockerGoods == "lost"`) would see goods riding the container with the guard off (PF_MAP_GUARD_OFF_GOODS_RIDE) [guess ~50%]; worth one look at Stage 6.
- The cause of the stale-stage K-22 reading (above).

## Exit
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 0
exit_met: true

## Owed
- 🔴 **Two readings of the exit disagree** [measured 2026-11-15 13:49 PST]. The block above follows the brief's definition (offline bars green; no Problem PENDING or NOTED; a Problem FIXED red first is closed). `python3 src/RimMandrake/rimflow/maturation.py next ExplosiveKnockback` reads this cycle as **exit not_met**: "a new blind judge is owed: 3 Problem(s) were FIXED in this cycle ... a fixed mod goes back to a new blind judgement pass (advance --to blind_challenge opens cycle 4)". The steward decides which applies; this judge does not advance.
- The three Polish items (filed, open; not part of passing).
- Stage 6: the 12 not_kernel rows, the game-side planted misses named under Planted, and the live fireHalf lane, which reads Flame's force only.
- Spend: about $6 of the $20 bound [measured, session budget line].
