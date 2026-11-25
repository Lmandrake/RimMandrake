# Hunt RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS: the sitting of 2026-11-25 (ArchSmall)

Kind C (an intermittent hunt): it looks for evidence of a failure and is never part of a bar.

## What ran

All on ArchSmall, proof build of Explosive Knockback, tier explosiveknockback_visit (25 mods), stage save
RM_Stage_ExplosiveKnockback, `batch.py --daylight` (each process jumps the clock to 12 h).

| run | build | processes | checks | result |
|---|---|---|---|---|
| long batch 1 | cee212dff6 | 16 | 54 runner checks | 53 PASS, 1 FAIL (sc_heavy_knock) |
| repeats | 2429a0d894 | 20 (two groups x 10) | 200 scenes | 200 PASS |
| long batch 2 | 2429a0d894 | 16 | 54 | 50 PASS, 3 FAIL, 1 UNMEASURED (P_goods_fly_rebound) |
| long batch 3 | bedd128cf7 | 16 | 54 | 54 PASS |

The two groups of the repeats are the processes that held every goods sighting: the goods_fly_wild group (with
heavy_knock) and the impact_factor group (with goods_fly_wall and goods_fly_rebound).

## Sightings

- Long batch 1, heavy_knock: the 30-steel stack hit colonist ph (a `heavy_hit` record) and then read `gone`. The scene's
  colonists are spawned drafted. `jawa/thing_lineage` read both ids UNRECORDED: its destroy hook kept no event for this
  thing, so the lineage tool could not look. Evidence `hunt_batch1_sc_heavy_knock.txt`.
- Long batch 2, goods_fly_rebound: INVALID "planned 0 cells leaves no rebound (back=0)" at staging, the symptom of visit 1.
  Evidence `hunt_batch2_P_goods_fly_rebound.txt`.
- Long batch 2 also read three other single FAILs that batches 1 and 3 passed: sc_pawn_arc (rehaul=False), sc_settings_sweep,
  and sc_barrage_perf (the frame probe read the game paused for 709 of 1396 rows). They are recorded here only
  (`hunt_batch2_*.txt`). None is a goods sighting.

Per scene in this sitting: heavy_knock 1 sighting in 13 runs, goods_fly_rebound 1 in 13, goods_fly_wall 0 in 13. Every
sighting came in a long batch. None came in the 20 short repeats.

## What is ruled out

- Settings left off their defaults (the runner's snapshot and restore): ruled out. In 3 long batches and 20 repeats, the
  read of all 57 settings fields after every verdict (knockback_runner, cee212dff6) and before and after every process
  (batch.py) never differed from the run's defaults. Each sighting had its settings at the defaults.
- A failed placement at staging (a Direct place onto a cell that holds another item spawns nothing, and the unspawned
  good's start is no cell, which plans 0 cells): unlikely. `Prepare` destroys every destroyable thing in the 15x15 patch,
  and nothing ticks between it and `Item()`. Staging now refuses such a placement by name (bedd128cf7). Batch 3 shows this
  causes no false INVALID. It has not been seen to catch a real placement fault.

## Instruments in place for the next sighting

- Every proof verdict that reads a good as not spawned prints `gone(destroyed, stack, holder, carrier and its job)` (2429a0d894).
- The INVALID lines of goods_fly_wall and goods_fly_rebound print WantCells' inputs: distance, mass, stack, spawned, cell,
  origin, the wild factor and the kernel's multiplier, base, max, light-mass limit and reference mass (bedd128cf7).
- Staging names a good that it could not place, and the things on its cell (bedd128cf7).

The next long proof-build batch prints one of these lines when a sighting comes. That line names the input that went
wrong. Run it with:

    python.exe design\concepts\ExplosiveKnockback\version\in_game\visit_1\scripts\batch.py --env <identity file> --tests <the 54 runner checks> --biome "" --daylight --sha <sha> --stash Transient/<folder> --rows <rows file>
