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
