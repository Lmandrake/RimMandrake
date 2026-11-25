# Explosive Knockback 0.1.0 — blind challenge, cycle 2

Judge: new blind judge (detached helper, item RIMMANDRAKE_CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED). Precondition: stage_record.json reads `blind_challenge`, cycles.visit 2 [measured].

## Start time
2026-11-15T08:36:10Z (UTC), before any input was opened.

## Changed files to bars
`git diff --name-only f5e310809f origin/main` (mod paths, `/blind_challenge/` excluded), read 2026-11-15:

| changed file | what changed (from the diff, not the why) | bars whose inputs it touches |
|---|---|---|
| `Source/RM_KnockbackMath.cs` | `WildCells` (goods throw x wild, rounded and capped like the kernel); `KbConfig.scaleOwnCap` (gas cap exact); rebound doc at keep 100 | inv_kernel, goods_arc_spin_rebound, inv_goods_fly, every_good_moves, per_weapon_tuning, inv_weapon_ext_fields, gas_goes_clump_by_clump, the_spared (rim), inv_too_weak_skip, heavier_flies_less; the whole kernel file is inv_kernel's input, so every kernel rule was re-tested once |
| `Source/RM_KnockbackMod.cs` | `GoodsThrowWild = 1.6f` constant; keep-percent comment | goods_arc_spin_rebound, settings_scale_and_switch, inv_settings |
| `Source/RM_MapComponent_Knockback.cs` | goods and corpses thrown by `WildCells`, pawns by the kernel; `kernelCells`/`wildCells` on both `item_move` lines; gas burst `scaleOwnCap = false` | goods_arc_spin_rebound, every_good_moves, inv_too_weak_skip, the_spared, gas_goes_clump_by_clump, inv_goods_fly |
| `Source/RM_KnockbackProof.cs` | three goods expectations use `WildCells` | inv_proof_scenes (T_SCRIPT, T_PROOFGATE, T_RESTORE) |
| `Assemblies/*.dll`, `.srchash` | rebuilt | (follows the sources) |
| `selftest_explosiveknockback_blind_cycle1.py` | added by cycle 1 | inv_kernel, goods_arc_spin_rebound (its lane-1 rows) |
| `version/stage_record.json`, `journal.md` | stage state, journal | none (not bar inputs; journal unread until lane 1 was recorded) |

No locked file changed (`tree.json`, `sheet.md`, `scenes.json` absent from the diff). Lane-1 inputs: tree.json leaves, sheet.md,
plan.md, VERSION.json, bars.md, the kernel, the settings file, the def patch, and the inventory bar text of the in-scope rows
(`record.json` `inventory[].what`, read for bar text only: inv_kernel's bar lives there).

## Lane 1
Recorded 2026-11-15 ~08:55Z, before any closed input was opened. Harness `lane1/BlindLane1.cs` + `lane1/run_lane1.py` (net8.0,
per-user Windows dotnet, staged on `D:\ClaudeWork\rimmandrake\scratch\ek_blind_c2_lane1`), rows `lane1/lane1_rows.jsonl`.

- **27 rows: 20 PASS, 0 FAIL, 2 INFO, 5 UNSETTLED (all `not_kernel`)** [measured].
- Fixed: mortar calibration 3 cells (60-76 kg), heavier_flies_less oracle numbers (5/3/2/0, x2 6/5/4/0, limit 250 thrumbo 1/3),
  blast power, wild fixed points, rim, per-weapon caps incl. the gas cap exact under every own-max scale, lookup order, mass
  limits, rebound 6,4,2,1,0, path walk (wall, door, water, sandbags, pits, covered pit, pawn, edge, corner), impact and factor 0,
  container shove (as locked), heavy knock, one request per thing per explosion, no cap.
- Random: 40 000 blasts (seed 20261115, monotone in distance/mass/force, wild >= kernel), 20 000 grids (seed 20261116, path
  conservation, failures shrunk by opening cells and cutting cells).
- Sweeps: every kernel-facing slider through its shipped range (strength x max x own-max scale x own max, both mass limits,
  ref percent, impact, other-mods percent, rebound keep 0-100).
- **INFO `L1_goods_wild_ratio_whole_cells`**: whole cells make the wild/kernel ratio range from 1.0 to 2.0 per stack; ~1.6 only on average.
- **INFO `L1_rim_band_kernel_zero_wild_one`**: a rim good whose kernel throw rounds to 0 can fly 1 cell by its wild throw, while
  inv_too_weak_skip and every_good_moves' oracle define "reached" by the kernel throw. A criterion question, not a kernel defect.
- Guard check: three planted kernel breaks (wild ignored, gas cap rescaled, intoPits off ignored) each turned the harness RED.

## Lane 2 reruns
Before any fix (`lane2/reruns.jsonl`, cycle-1 `rerun_offline.py` with a recorded-prefix match): **15 of 16 offline tests match** on
verdict and last line; T_RESTORE matches on verdict (FAIL, known red) but not on its last line (the recorded line was a stderr
SyntaxWarning) [measured]. T_SETTINGS_SCREEN is known red and decides no offline bar.

After the fixes (`lane2/reruns_after_fix.jsonl`, at 04bb4c93fa): **15 of 16 PASS**; the 16th is T_SETTINGS_SCREEN, known red
(855/856, was 851/856). T_KERNEL now runs 174 checks (was 164). T_RESTORE PASS.

## Planted
`lane2/planted_faults.json`, `lane2/plant_faults.py`, `lane2/planted_results.jsonl` (+ `planted_results_recheck.jsonl`).
**29 faults** planted, at least two per changed file (kernel 7, settings 4, map component 7, damage patch 1, proof 4, Stage-3
proof 1, storeroom proof 1, proof gate 1, lint 1, def patch 2), one or more per new switch, journal line and the rim rule; run
against 11 offline suites plus lane 1 for kernel faults, under `WINBUILD_ROOT=D:\ClaudeWork\rimmandrake\scratch\ek_blind_c2_mut`,
restored on SIGTERM/SIGINT/SIGHUP; every batch ended `tree_clean_after: true` [measured].
- First pass: **23 of 29 caught** by the builder's suites or lane 1; **6 missed** by every offline suite:
  PF_MOD_WILD_CONSTANT_ONE, PF_MAP_GAS_CAP_SCALED, PF_PROOF_GOODS_WANT_PLAIN, PF_PROOF_SCENE_NAME_DROPPED,
  PF_STAGE3_FIRE_LANE_ALWAYS_OWN, PF_STOREROOM_NO_RESTORE; and 2 kernel faults (WildCells ignored, gas cap rescaled) were caught by
  blind lane 1 only, not by inv_kernel's own deciders [measured].
- After the new checks (04bb4c93fa): **all 8 re-planted are caught**, the kernel two by T_KERNEL too, so **29 of 29 caught** [measured].
- Limit: PF_STOREROOM_NO_RESTORE was invisible to T_RESTORE because the reset lines carry a reviewed `restore-check: ok`
  annotation; it is caught by T_JOURNAL_JOLT's wiring check instead.

## Faults
`lane2/faults.json`, each filed in rimflow. **10 Problems, all FIXED red first; 2 Polish, filed** [measured]. `miss_of: 1`
(material unchanged since cycle 1): 7 Problems and both Polish.
| id | class | bar | status | miss_of |
|---|---|---|---|---|
| RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS | Problem | inv_proof_scenes | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_SKIP_GOODS_WHEN_FLIGHT_OFF_OLD_HOP_LINGERED | Problem | settings_scale_and_switch | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_BUILD_CLOSED_GUARD_FIRE_HALF_SWITCHES_SHEET_NAMED | Problem | settings_scale_and_switch | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_DRAW_CONTAINER_JOLT_DUST_PUFF_WAS_ALL | Problem | closed_container_holds | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_DELETE_DEAD_CONTAINER_SHOVE_KERNEL_TESTED_75_KG | Problem | closed_container_holds | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_PIN_KNOCKBACK_NONPUSH_FORCES_IN_LINT_TABLE | Problem | every_harmful_blast_throws | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_CORRECT_FLYING_OFF_WALK_ROW_TO_ITS_BAR | Problem | settings_scale_and_switch | FIXED 587529cee1 | 1 |
| RIMMANDRAKE_DECIDE_RIM_THROW_BY_KERNEL_NOT_WILD_FACTOR | Problem | inv_too_weak_skip | FIXED 587529cee1 | 0 |
| RIMMANDRAKE_COVER_WILD_GAS_CAP_IN_KERNEL_DECIDER | Problem | inv_kernel | FIXED 04bb4c93fa | 0 |
| RIMMANDRAKE_WIRE_CHECKS_SIX_PLANTED_FAULTS_PASSED_OFFLINE | Problem | inv_proof_scenes | FIXED 04bb4c93fa | 0 |
| RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST | Polish | inv_proof_scenes (instrument) | PENDING (filed) | 1 |
| RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER | Polish | FlowWorks, not this mod | PENDING (filed, baselined) | 1 |

Found by me without a steward pointer: the flying-off hop, the rim decided by the wild factor (lane 1's INFO row, confirmed in the
caller), the two kernel-decider gaps, the six wiring gaps, the checker's variable-args blind spot.

## Fixes
`lane2/fixes.jsonl`: one row per Problem with the red command, rc and line on the parent and the green on the fix sha.
- **587529cee1**: storeroom_pit_proof.py snapshots every saved setting before its first reset and restores it in a finally;
  closedContainerGuard and fireAtHalf (saved, default on, reset, on the page, read in HeldReason/InClosedContainer/ThrowContainer
  and ConfigOf); flyingGoods off skips goods `flying_off` (and the prefix's ItemWillBeThrown); a blocked container is drawn
  shaking (StartJolt, MapComponentUpdate, kernel JoltOffset: 20 ticks, at most 0.15 cells, at most 64 at once); ContainerShove/KbShove
  deleted, ThrowContainer plans with the new kernel ContainerThrowCells; a rim good needs a kernel cell; lint ek-pins; the walk row.
  Release and proof builds both compile with 0 errors; the committed DLL is the release build [measured].
- **04bb4c93fa**: K-23 (WildCells), K-24 (exact gas cap) in T_KERNEL; six wiring checks in T_JOURNAL_JOLT.

## Steward's decisions enacted
Each acted on with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` where the ledger allowed it (OWNER.jsonl published).
1. **T_RESTORE green: done** (587529cee1; `run_selftests --only selftest_proof_restore_check.py` prints `RESULT: GREEN` [measured]).
   The brief's premise was stale: RM_KnockbackProof.cs lines ~755/~1285 no longer leak (Stage and Verdict restore on throw; the
   checker learned the helper-built restore at af61b9c206, 2026-11-15 00:38 PST). The red came from 7 other hits: 3 resets in this
   mod's storeroom_pit_proof.py (a real Problem: the player's values were lost; fixed), a reviewed annotation one line too high in
   HugeThings' showcase_common.py and a restore planner in Utils/wrapup_debt.py (both annotated after reading them), and 2 FlowWorks
   hits baselined under a filed item (the checker's own filed-not-fixed table). Dropped from the known-red list.
2. Goods factor 1.6 stays a constant: honoured; T_JOURNAL_JOLT now pins it at 1.6.
3. sc_storeroom_mortar repair: **not landed** (no scenes.json commit since f5e310809f) - owed by the neutral fixer; no verdict built.
4. Wild cells on the move line: **already there**: both `item_move` lines carry `kernelCells` and `wildCells` in the code at f5e310809f..origin/main
   (the diff since the stage opened adds them); it is the *request* line that does not. No code change; the offline format test was added (T_JOURNAL_JOLT,
   passes on the parent too, so it is not red-first; a planted drop of wildCells turns it red [measured]).
5. Non-push forces pinned in T_LINT: done; red against a planted Flame 0.7 (parent lint rc 0, new rc 1) and a planted EMP 0.2.
6. Two switches and a jolt: done (above); the settings sweep covers both; RM_KnockbackMod.cs now saves 48 settings.
7. Closed containers thrown: rewording **not landed** - owed by the steward; no verdict on sc_closed_containers. The dead slide
   kernel is deleted with every inbound reference (K-14, KnockbackSweep, both blind lane-1 harnesses) and the throw is kernel-tested.
8. Walk row yields to its bar: done in validation.py, bar_lists_map.json, the walk's must-be-true list (outside the north-star
   section) and required_checks.json; the code now follows the bar as well, and the goods_fly_off proof scene expects no throw.
9. Questions 10 to 14: not re-asked.

## Tests edited
`tests_edited.json` lists every test file touched, with before and after sha; none loosens a check. The one matching rule widened
is T_STAGE3_SCENES' F2: a saved key also counts as named when the locked action names it in the sheet's words (an explicit
two-entry alias: "closed guard", "fire at half"), because the fixer may not edit the scene text. Added:
`selftest_explosiveknockback_journal_jolt.py` (T_JOURNAL_JOLT; not yet in test_table.json, which is the steward's).

## Unsettled
- Lane 1: 5 `not_kernel` rows (carrier arc/spin and the keep-100 bounce limit, every good counted, the gas chain, each switch's off
  state, the proof scenes): game-side, owed to Stage 6.
- The jolt is drawn by code that compiles and is offline-tested for bounds and wiring; whether it reads as a jolt on screen is
  UNRUN. Every live test touched is UNRUN (goods_fly_off, the closedGuard/fireHalf sweep lanes, storeroom_pit_proof.py's restore).
- Lane 1 INFO: whole cells make a good's flight 1.0 to 2.0 times the kernel's per stack (mean 1.582 [measured]); the sheet's
  "about 1.6" holds on average. That is the sc_storeroom_mortar criterion the neutral fixer owns; no verdict here.

## Exit
```
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 0
exit_met: true
```
inv_kernel: T_KERNEL 174/174 and T_FUZZ OK on the rerun at 04bb4c93fa. inv_proof_scenes: T_SCRIPT, T_PROOFGATE and T_RESTORE PASS
on that rerun [measured]. Lane 1: 0 FAIL rows. All 10 Problems FIXED red first; the 2 Polish are filed and do not block.
The two locked-text repairs (decisions 3 and 7) are owed by others and carry no verdict here.

## Owed
- **Steward:** re-pin sc_closed_containers to "thrown a short way" (decision 7), and sc_storeroom_mortar's words "each good's request
  line carries..." to the move line (decision 4); add T_JOURNAL_JOLT to test_table.json; name closedContainerGuard and fireAtHalf in
  sc_settings_sweep's action when it is next re-pinned.
- **Neutral fixer:** the sc_storeroom_mortar ratio criterion (decision 3).
- **Stage 6 (live):** look at the container jolt (is it visible, does it read as a jolt); run goods_fly_off, the closedGuard and
  fireHalf sweep lanes, and storeroom_pit_proof.py (row SETTINGS_RESTORED).
- **Filed, open:** RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST; RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER (FlowWorks).
- Trap seen once: `run_selftests --only` ran T_KERNEL and T_SETTINGS_SWEEP_OFFLINE in parallel and reported RED, then GREEN on a
  rerun; both stage into the same `ExplosiveKnockbackSelfTest` folder [guess ~75% that the race is the cause].

## Reconcile (2026-11-15 02:15 PST, Conductor night order; not the judge)
- `maturation.py next` read exit not met on 4 FIXED Problems (lint pins, walk row, kernel decider, six wiring checks): each row
  ran its check the failing way round (red rc 0, green rc 1). A record gap: redone for real as tests whose rc 0 means the fix
  holds (`lane2/plant_faults.py --expect-caught`, `lane2/walk_row_check.py`), red at each fix's own parent (ecd0b23322,
  57e61fef0b) in a scratch clone, green at 587529cee1 / 04bb4c93fa; outputs in `lane2/fix_demos/` [measured].
- Four more rows (flying-off skip, drawn jolt, dead shove kernel, rim) named a `<parent Source>` placeholder or an
  uncommitted worktree; rerun with named paths (`fix_demos/jj_*`), red rc 1, green rc 0 [measured]. maturation.py now refuses
  a placeholder command and names an inverted row; its brief says so (a9851ef3e8).
- Judge's work checked: no edited test loosens an assertion; offline deciders rerun at HEAD, 15 of 16 PASS, T_SETTINGS_SCREEN
  then 855/856 and now 856/856 (838685395999) [measured].
- Owed items above, done: sc_storeroom_mortar's ratio clause repaired by the neutral fixer
  (`version/criterion_repairs/sc_storeroom_mortar_2026-11-15/`); the container tests follow his "thrown a short way" card;
  the bar's own words in tree.json and sheet.md wait on his re-certification (RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING).
