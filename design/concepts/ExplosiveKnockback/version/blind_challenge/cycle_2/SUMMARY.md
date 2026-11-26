# ExplosiveKnockback 0.2.0, blind challenge cycle 2 (judge-1795662842)

## Start time
2026-11-26T03:16:08Z (2026-11-25 19:16 PST), before any input was opened.

## Changed files to bars
`git diff --name-only 8723f717a4 origin/main` over the brief's paths, less `/blind_challenge/`. The ledger shards and views,
`version/evidence/` and `version/in_game/` records are records, not inputs of a bar; `journal.md`, `polish.md`,
`test_table.*`, `run_spend.jsonl`, `scene_runs.jsonl`, `stage_record.json` are bookkeeping. No locked file changed
(`tree.json`, `sheet.md`, `plan.md`, `scenes.json`, `version/bars.md`, `version/VERSION.json`: empty diff), and the kernel
`RM_KnockbackMath.cs` did not change.

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` | inv_proof_scenes (offline), and every bar a proof scene decides |
| `src/RimMandrake/ExplosiveKnockback/knockback_runner.py` | inv_proof_scenes (offline) |
| `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py` | inv_proof_scenes (offline; decider T_PROOFGATE) |
| `src/RimMandrake/Utils/selftest_proof_restore_check.py` | inv_proof_scenes (offline; decider T_RESTORE) |
| `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackShow.cs` | blast_show_fire_and_flash, blast_show_screen_shake, blast_show_air_ripple, blast_show_smoke, blast_show_crater_scar, blast_show_scales_with_damage, blast_show_switches_off_clean |
| `src/RimMandrake/ExplosiveKnockback/Defs/ThingDefs/RM_KnockbackBlast_Scars.xml` | blast_show_crater_scar, blast_show_scales_with_damage |
| `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blast_show.py` | the blast_show_* bars (offline test of a stage-6 bar) |
| `src/RimMandrake/ExplosiveKnockback/Assemblies/RimMandrakeExplosiveKnockback.dll` (+ `.srchash`) | every bar (the built code) |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_blast_show.py`, `scene_settings_sweep_show_switches.py` | blast_show_* bars, blast_show_switches_off_clean |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_gas_chain_pawn_on_cover.py` | gas_shoves_pawn_on_pit_cover |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_lookup_sources.py` | per_weapon_tuning |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_pawn_arc_bruise_sizes.py`, `scene_pawn_land_on_pawn_sizes.py` | collision_bruise_by_size |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_pawn_arc_carried_thing.py` | carried_thing_own_arc |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_pawn_arc_sandbag_no_contact.py` | no_impact_without_contact |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_storeroom_mortar_rebound_legs.py` | rebound_goes_shorter, goods_arc_spin_rebound |
| `src/RimMandrake/ExplosiveKnockback/proof/scene_storeroom_pit.py` | thrown_into_pit_falls, blast_breaks_pit_cover |
| `design/concepts/ExplosiveKnockback/version/art/blast_show_art_0_2_0.json` | blast_show_fire_and_flash, blast_show_smoke, blast_show_crater_scar, blast_show_soot_on_pawns (art items) |
| `design/concepts/ExplosiveKnockback/version/mutants.json`, `small_list.json` | test apparatus (no bar's logic) |

Lane-1 scope: both offline bars (inv_kernel, unchanged kernel, judged once as the main work; inv_proof_scenes, changed),
and the stage-6 bars above whose logic lives in the kernel.

## Lane 1
Written from the bars (tree.json leaves, record.json rows), the shipped settings in `RM_KnockbackMod.cs` and the patches,
against the shipped kernel. `lane1/BlindLane1.cs` (C#, 26 rows), `lane1/lane1_proof_scenes.py` (inv_proof_scenes, 5 rows),
`lane1/not_kernel_rows.json` (35 game-side bars), run by `lane1/run_lane1.py`. Seeds are in each random row.

Result [measured]: 68 rows: 31 PASS, 0 FAIL, 2 INFO, 35 UNSETTLED (all `not_kernel`, every one naming only stage-6 bars).
Every one of the 73 bars is named by at least one row.

- inv_kernel: 26 kernel rows PASS: the mortar calibration (3 cells, over sandbags), the heavier_flies_less oracle (mass bands
  for 5/3/2 and 6/5/4 printed), monotone and capped throws (200000 random cases), the path walk (22 fixed geometries;
  60000 random grids for conservation; 40000 for never crossing a pit), Line steps, rebounds (keep 0..100), reflect, goods
  wild, per-weapon lookup and caps, fire at half (ratio near 0.5), collision bruise by size, immunity, shield, heavy knock,
  pit cover rules, containers and jolt, the explosion ledger, the frame probe, and a sweep of every kernel setting over its
  slider range with every switch off.
- inv_proof_scenes: 5 rows PASS: every scene family the bar names is in `SceneNames` and every name has a case label; no
  restore overwrites an earlier one and no setting is written without a restore before it (the instrument flagged a
  planted overwrite and a planted write); the gate exits 3 on a release answer only; the runner gates before staging and
  restores settings in a finally; every proof file is wholly under `RM_PROOFS` and the committed DLL holds no proof type
  (93 types read with a metadata reader).
- INFO, not judged: a mortar at 1 cell throws a pawn of 39.3-76.9 kg 3 cells (a pawn over 77 kg with gear flies 2); 98
  of 1800 rim cases throw 1 cell at both damages (raw 0.5-0.75 doubles to under 1.5).
- Three of my first oracles were too broad (a colonist up to 80 kg, a 60 kg colonist at twice the damage, rim 1-cell
  throws). They were my oracle's fault, not the mod's (class HARNESS), and were tightened to the leaf's own numbers
  before lane 1 was recorded; the edges are the two INFO rows.

## Lane 2 reruns
`lane2/rerun_offline.py`, every `kind: offline` test of `version/test_table.json` with its recorded command, on 751eb30f
(lane 1's commit, the mod as judged) [measured]: 36 rerun, 35 match their recorded verdict and last line (T_FUZZ differs only
in its own timing figure; the matcher ignores a `N.NNs` timing). All five offline deciders PASS: T_KERNEL, T_FUZZ
(inv_kernel), T_SCRIPT, T_PROOFGATE, T_RESTORE (inv_proof_scenes). T_SITUATION_MAP_OFFLINE (slow, 315 s recorded) PASS,
39 of 39 planted faults seen. One mismatch: T_JOURNAL_JOLT_OFFLINE, recorded PASS, reran FAIL (1 fault): see Faults.
After the fixes, `rerun_relation.py --old 751eb30f` names two touched checks, T_PROOFGATE and T_JOURNAL_JOLT_OFFLINE;
both PASS at 1a223189 (`lane2/reruns_after_fix.jsonl`; their last lines changed with the test edits, the verdicts match).
Every other decider keeps its `reruns.jsonl` row. Lane 1 rerun at 1a223189: `lane2/lane1_rows_after_fix.jsonl`, 31 PASS,
0 FAIL, 2 INFO, 35 UNSETTLED.

## Planted
`lane2/planted_faults.json`, 50 faults; `lane2/plant_faults.py` with WINBUILD_ROOT on the private `_mut` folder; a catch
needs a new failing line, never an rc alone. `lane2/planted_results.jsonl` [measured], baseline all green, tree clean after:
21 of 50 caught on 751eb30f.
- Kernel (inv_kernel), 5 of 5 caught: falloff halved, sandbag rest kept, rebound rounded up, bruise by own mass, corpse by
  the creature limit.
- Proof (inv_proof_scenes), 6 of 10 caught at first: the gate's two plants, a scene name dropped, WantCells' wild 1, pits
  always on, the runner's settings restore dropped. SURVIVED: AddExt's restore chain dropped, RunRestore never runs, the
  runner's gate call removed, Stage ignoring placeFault. After the repair (1a223189) all 7 proof plants re-run are caught
  (`lane2/planted_results_after_fix.jsonl`).
- Game-side callers and patches, 3 of 5: the plan's goods by the plain kernel, the walk's collide swapped, Flame at full
  force caught. SURVIVED: the landing-on-pawn bruise swapped (RM_PawnFlyerPatches.cs) and blast power dropped in the hook.
  Both are game-side logic of stage-6 bars (collision_bruise_by_size, heavier_flies_less) whose deciders are live scenes;
  no offline test claims them. Not a Problem against an offline decider; the stage-6 scenes must catch them.
- Changed files, two each: RM_KnockbackShow.cs 2 of 2, RM_KnockbackBlast_Scars.xml 2 of 2,
  selftest_explosiveknockback_blast_show.py 2 of 2, selftest_proof_restore_check.py 1 of 2,
  selftest_explosiveknockback_proofgate.py 0 of 2. The proof scene scripts under `proof/` (10 files), 0 of 20: no offline
  test reads them; they are stage-6 apparatus. The test-file survivors are a boundary (`>= 5` to `> 5` on a self-check)
  and an edit inside a comment string (an equivalent mutant), plus one crash (visible red, not counted as caught).
  The DLL, the art JSON, mutants.json and small_list.json were not planted (no logic to mutate).

## Faults
`lane2/faults.json` [measured]: 2 Problems, 0 Polish, both `against` check (class HARNESS), both FIXED, 1 is `miss_of: 1`.
- RIMMANDRAKE_REPAIR_KNOCKBACK_JOLT_CHECK_LOCAL_WILD: T_JOURNAL_JOLT_OFFLINE red on the real build. Its text check wanted
  GoodsThrowWild literally at each GoodCells call; WantCells keeps it in a local now (bedd128cf7). Behaviour unchanged.
  Worth the touch: it guards the oracle of the goods-flight scenes. miss_of 0 (the change came after cycle 1 opened).
- RIMMANDRAKE_SEE_KNOCKBACK_SCENE_RESTORE_DROP_RUNNER_GATE: four planted behaviour faults in the inv_proof_scenes kernel
  files survived every decider of that bar. miss_of 1 (AddExt and RunRestore are unchanged since cycle 1).
No mod fault was found: lane 1 has no FAIL, and the reading of the changed show code (scar rename, back-compat name patch,
the scar journal) and the kernel callers (blast power, landing bruise, rebound, container, mass limits) found nothing
significant. Engine facts read through RimSage [measured]: `GenExplosion` turns damAmount -1 into the type's default
before the hook reads it; `Filth` declares `DeSpawn`.
Both findings went into the mod ledger as `finding.open` with the fix and its sha (a JUDGE may not write claimed_fixed).

## Fixes
`lane2/fixes.jsonl`, both check repairs, red on a plant and green on the real build at the fix sha:
- c31fefefd0b661785aaf8bd8f8482272321bf248 (`selftest_explosiveknockback_journal_jolt.py`): red rc 1 with `float wild = 1f;`
  planted, green rc 0.
- 1a223189b3024d59421f0cbd9ee42af612fcf121 (`selftest_explosiveknockback_proofgate.py`, C1, R2, S1): four plants red rc 1,
  green rc 0.
Check repairs owe no fresh reader. No mod code changed. `maturation.py red-seen` recorded for T_PROOFGATE and
T_JOURNAL_JOLT_OFFLINE (`version/evidence/red_seen.json`).
Verified (judge-verify): RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES (map M04 0 of 243452) and
RIMMANDRAKE_SCOPE_KNOCKBACK_RESTORE_DECIDER_RED_ON_FLOWWORKS (rc 0; rc 1 on a planted poke), both `finding.verified` at 1a223189.

## Steward's decisions enacted
None were written for this cycle; the standing default held. No bar, criterion, version or stage was touched.

## Tests edited
`tests_edited.json`: selftest_explosiveknockback_journal_jolt.py (T_JOURNAL_JOLT_OFFLINE) and
selftest_explosiveknockback_proofgate.py (T_PROOFGATE). Neither weakens an assertion; each adds what it sees.

## Unsettled
35 `not_kernel` rows, each naming one stage-6 bar (the blast show, flight, gas, hose, pits, storage, the walk): owed to
Stage 6. Two survived plants mark where stage 6 must look: the landing-on-pawn bruise direction
(`RM_PawnFlyerPatches.cs`) and blast power in the hook (`RM_Patch_DamageWorker_ExplosionKnockback.cs`).

## Exit
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 0
exit_met: true

## Owed
Nothing from this cycle's exit. `maturation.py next ExplosiveKnockback` [measured, 2026-11-25 8:12 PM PST]: "blind cycle 2
(visit 1, total 2): exit met: the block says exit_met true and every file check agrees (2 offline bars, 5 deciders rerun
PASS)"; the 35 not_kernel rows are deferred to Stage 6. For the steward: its `judge_certificate` line refuses
inv_proof_scenes because T_PROOFGATE's `runs_today` row was recorded on build 083f85f71b before this cycle edited the test
(this cycle reran it PASS at 1a223189, `lane2/reruns_after_fix.jsonl`); the same line names in-game tests with no
empty-game adapter, which is not this stage's. The steward reads this SUMMARY.md and decides the move.
