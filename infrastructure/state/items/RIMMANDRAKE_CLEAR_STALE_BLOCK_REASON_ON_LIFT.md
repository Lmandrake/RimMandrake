# RIMMANDRAKE_CLEAR_STALE_BLOCK_REASON_ON_LIFT

## spec
The Conductor's brief (D2b) said Pyrelands' version/VERSION.json reads locked while stage.json reads blocked at
Designer step 5. Which is right: both, on different axes.
- VERSION.json is the Design Version lock (owner, 2026-11-13). It is right.
- stage.json blocked at 5 was coverage_judge's real stop after the round-6 released look came back not_covered
  (3696436297). A locked change after the lock re-enters the Designer for a re-pin, an exam retake and one coverage
  look (maturation_autonomy locked_change chain). The grant was released at 0289f8f3a5, after which it reads ready, 4.

The writer defect: every path that lifts a block set `status` and left `blocked_on`:
- coverage_judge.release
- designer_stage.unblock
- close_run's done and return branches

maturation_now.py:250 shows `blocked_on` as the Designer's why under any status. So Pyrelands at status ready
still showed "released for one more look at round 6; that look was not_covered" on the page.

Fix: `designer_stage.lift_block(st)` sets ready and drops the reason (history keeps it). All four paths use it.
`unblock` on a ready concept that still carries a leftover reason is the repair verb, and it records that repair.

Repair of the files: Pyrelands has an open Designer run (bench-pyre-exam-st4-r7-20261115, opened 21:18Z). It is
not hand-written. That run's close goes through close_run, which now drops the leftover reason. If it is still there
after that close: `python3 src/RimMandrake/rimflow/designer_stage.py unblock design/concepts/Pyrelands --why "..."`.
The locked concepts (ExplosiveKnockback, FlowWorks, GimmeSomeSlack) keep their reason text: under `locked` it is the
lock's why, and the page shows it as such.

## acceptance
- selftest_designer_stage and selftest_coverage_judge_loop: after unblock, after release and after a close to ready,
  stage.json has no blocked_on. Watched red on d08616308, green after, and a mutant (lift_block keeps the reason)
  turns 4 checks red.
- Live: design/concepts/Pyrelands/stage.json on origin reads no blocked_on once its open run has closed.

Evidence: D:\ClaudeWork\rimmandrake\harden_dispatch\st_d2b_base.txt, st_d2b_fix.txt, st_d2b_mut.txt
