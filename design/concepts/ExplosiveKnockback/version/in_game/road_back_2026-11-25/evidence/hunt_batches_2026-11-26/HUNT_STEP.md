# Hunt step: long batches with no model, SteveDesktop lane (2026-11-26)

Item RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS (kind C). Both ArchBig and ArchSmall were held by
other runs, so every batch ran through the SteveDesktop test lane (`testq.py submit --checks <53 takeable checks>`, proof
build, tier explosiveknockback_visit, 16 runner processes per job, one game session per job). Steve1 ran batches 1 and 3,
Steve2 ran batches 2 and 4. The lane did not take 12 of the 65 checks (11 "could not look" with no reader, 1 Archmagi-only);
the lane runs the runner's own groups, not `batch.py --daylight`: whether `--daylight` matters is UNMEASURED.

| batch | job | build | result | goods sightings |
|---|---|---|---|---|
| 1 | J20261126T083534Z-a4ed9e (Steve1) | 5796fe3cec, unfixed | 40 PASS, 13 FAIL | 2 (goods_fly_wall, goods_obstacles_control lane D) |
| 2 | J20261126T091116Z-0b8ff7 (Steve2) | 5796fe3cec, unfixed | 51 PASS, 2 FAIL | 0 |
| 3 | J20261126T091619Z-17e129 (Steve1) | 813366f4c6, fixed | 42 PASS, 11 FAIL | 1 (open_storage g3 merged; see below) |
| 4 | J20261126T095118Z-ef2396 (Steve2) | 813366f4c6, fixed | 49 PASS, 4 FAIL | 0 |
| 5 | J20261126T095128Z-b3d8ef | 813366f4c6 | INVALID DEPLOY (stale companion DLL), no run | UNRUN |

Four long batches ran. A job stores one verdict per group of checks, so one failing scene marks every check of its group
FAIL (batch 1: 10 rows of the impact_factor group; batch 3: 10 rows of the goods_fly_wild group). The table below names the
scene that failed.

## Sightings and printed cause lines

| batch | check (scene) | verdict text | printed cause line | 57 settings fields at defaults? |
|---|---|---|---|---|
| 1 | P_goods_fly_wall (goods_fly_wall) | FAIL comp not spawned | `gone(destroyed=False stack=1 holder=Pawn_CarryTracker:Krueger66123 job=HaulToCell)` | yes (all 80 reads of the job) |
| 1 | sc_goods_obstacles (goods_obstacles_control, lane D) | FAIL D BAD D not spawned | `gone(destroyed=False stack=2 holder=Pawn_CarryTracker:Krueger66123 job=HaulToCell)` | yes |
| 3 | sc_open_storage (open_storage, g3) | FAIL g3 not spawned | `gone(destroyed=True stack=0 holder=none)`, floor control moved 1 cell | yes |

Krueger is a colonist of the stage save, not a scene pawn (scene pawns are named by their key). No printed line came for
the visit 1 symptom "planned 0 cells" (goods_fly_rebound): it did not recur in any of the 4 batches.

## Reading

- Cause of batch 1 (2 printed lines, same pawn, same job): a free colonist of the stage save picks up the scene's good
  with a HaulToCell job. That is a STAGING cause: `Item()` placed the good unforbidden. The mod did not lose the good: it
  landed, then a colonist carried it. A haul between staging and the blast also explains "planned 0 cells" (the good has
  no cell when WantCells reads it) and the vanished heavy_knock stack, but no printed line proves those two. [guess ~70%]
- Fix (this run, test first): `Item()` forbids the good it places (`haulable: false` default); pawn_arc's stack and
  pit_goods_fetch's two stacks keep `haulable: true`. Offline check
  `selftest_explosiveknockback_scene_goods_forbidden.py`: 0 of 4 PASS on the parent, 4 of 4 PASS on the fix. In two long
  batches on the fixed build (3 and 4): goods_fly_wall, goods_fly_rebound, goods_obstacles, heavy_knock, impact_factor read
  PASS; no good was hauled. Two unfixed batches on the lane: 1 had the haul sightings, 1 had none, so two fixed batches with
  none is not proof of the fix. [measured: counts] [guess ~65%: that the fix removes the cause]
- Batch 3 open_storage g3: `destroyed=True stack=0 holder=none` means the good merged into another stack. g3 starts on
  the table at (0,-2) and the floor control f2 sits at (0,-4), the same line: a flight south can land on it. The scene
  passed in 3 earlier lane batches and in batch 4 of the fixed build. Whether the forbid change caused this merge is
  UNMEASURED (n=1 of 2 fixed batches; a forbidden good does not change vanilla stacking, to the best of this run's reading).
  It is the open question of this step; the next step is a few more fixed batches or a read of `open_storage` landing cells.
- Settings off defaults (the runner's restore): ruled out again. 320 of 320 "SETTINGS after verdict" reads in the four
  batches read "all at the run's defaults" (`logs_*`).
- Not goods sightings (recorded only): sc_pawn_arc `rehaul=False` (batches 1, 2 and 4 of 4; PASS in batch 3),
  sc_pit_fetch `free-will haul: main 1 control 1 (want 1, 0)` (4 of 4 batches, both builds), sc_hose_drop `no launch
  line` (batch 4 only), sc_settings_sweep FAIL (batch 4 only, no detail line kept). sc_pit_fetch fails in every batch,
  so it is no intermittent fault: it needs its own item.

## Files

`batchN_*lane_job.json` (the job's whole result), `logs_<job suffix>/run_NN.log` (the runner's stdout per process).
