# SB_islands_restore_reach "fill job stall": a slow worker, repaired in the scene

Item: RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE. Game b on Archmagi, FlowWorks at 496604468f,
13-mod flowworks tier, calm site loaded and verified before each run (`evidence/calm_site_fix_*.log`), 2026-11-22.

## Class: SITE (the staged worker), not MOD

The reach row spawns a random `Colonist`. The fill job's speed is that pawn's MiningSpeed. In vanilla
(`Stats_Pawns_WorkGeneral.xml`) MiningSpeed is 0.04 + 0.12 x Mining, with a minimum of 0.1. So it is 0.1 at Mining 0 and 1.0
at Mining 8. A notch at depth 8 with labour 0.25 takes about 2000 ticks at speed 1.0, and about 20000 ticks at 0.1. That is
more than the row's 15000-tick wait. The job, the gravel and the stand square look the same as a stuck job.

| run | worker | MiningSpeed | result | evidence |
|---|---|---|---|---|
| A, Mining set to 0 | random | 0.1 | FAIL, depth 8 of 8; the same job beside (171,226) for 30 reads | `evidence/diag_skill_m0.*` |
| B, Mining set to 10 | random | 0.98 | grounded 8 -> 0 on both squares, at most 4 reads per notch (verdict withheld: a SITE fault, the site was not reloaded after run A) | `evidence/diag_skill_m10.*` |

Refuted: GotoCell(A, Touch) from a diagonal stand square never completes. In run B and in the five real runs, the same
diagonal stand square (172,225) worked.

## Repair (the scene only; the mod is not touched)

`suspension_bridge_proof.py` `reach()` sets the worker's Mining to `REACH_WORKER_MINING` (8). It then requires
MiningSpeed >= `REACH_WORKER_MIN_SPEED` (0.5) and class SITE, or the row is withheld. The mock bridge answers
`jawa/set_pawn_skill` and `jawa/pawn_stats`.

- Offline: `python3 src/RimMandrake/FlowWorks/northstar/selftest_suspension_bridge_reach.py`. It adds a planted slow
  worker (mock MiningSpeed 0.1). The selftest is RED on the parent proof (the mock row read PASS) and GREEN on the fix
  (9 verdict cases + 4 mock runs, 0 fails).
- Live, planted (`RM_DIAG_REACH_LABOUR=500 diag_reach.py`, a fill too slow to ground): FAIL reached_not_grounded
  (`evidence/fix_planted.*`).
- Live, real build, the acceptance test (five runs): PASS 5 of 5, 16 jobs each, worst 6 reads of 500 ticks per notch,
  limit 30 (`evidence/fix_real1..5.*`). The random colonist arrived at MiningSpeed 0.1, 0.50, 0.1, 0.33 and 0.15. So 3 of 5
  workers would have stalled without the repair.

`maturation.py red-seen` cannot record this red. The fault would live in the test's own file, and a C# fault never reaches
a live check from the tree. sc_hung_bridge is not an offline decider, so no certificate reads it. The red is the planted
run above.
