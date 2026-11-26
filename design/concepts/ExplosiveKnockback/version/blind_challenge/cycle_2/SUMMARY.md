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
(not started)

## Planted
(not started)

## Faults
(not started)

## Fixes
(not started)

## Steward's decisions enacted
(not started)

## Tests edited
(not started)

## Unsettled
(not started)

## Exit
offline_bars: {inv_kernel: red, inv_proof_scenes: red}
problems_open: 0
exit_met: false

## Owed
(in progress)
