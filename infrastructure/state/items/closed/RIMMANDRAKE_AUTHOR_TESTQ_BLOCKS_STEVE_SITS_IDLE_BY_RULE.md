---
state: proposed
needs: offline
---

# RIMMANDRAKE_AUTHOR_TESTQ_BLOCKS_STEVE_SITS_IDLE_BY_RULE

## spec

Filed 2026-11-15 ~05:50 PST by the BENCH launch-and-queue helper, answering the owner's 05:25 question "Are the two live
games being maximized?" for SteveDesktop.

**Measured cause of an empty SteveDesktop queue (2026-11-15 ~13:40Z):**
- The machine is reachable and has no brake. `ssh_state` down_since null; `fault_state` reachable true, boot 08:57Z,
  clean 4.4 h, bad_cpus [] (idle, so no load since boot); `brake_release.py` state `none`; no pause file.
- The steward reads `IDLE_BY_RULE` since 08:59Z: "pipeline tests only: nothing admissible (35 mods)". This is the owner's
  card 18c (`src/RimMandrake/Utils/testq/pipeline_admit.py`; spec `design/specs/2026-11-13-maturation-pipeline.md`
  Stage 6 "Entry rule"). The lane is working as ruled.
- The real gap: **no `test_table.json` in the repo has a `testq` block** (grep of `design/concepts/*/version/test_table.json`
  for `"testq"`: 0 hits). The three mods past blind are FlowWorks (32 stage-6 checks), ExplosiveKnockback (56) and
  Pyrelands. None of them can send one check to SteveDesktop. Nothing in the pipeline writes the blocks: the tables
  were made by a throwaway script (`version/advance_scripts/`), and `maturation.py` only counts them (lines ~1816, ~1925).

**Smallest fix:** for each locked version past blind, add a `testq` block `{chains, rows, proofs}` to every stage-6
entry that a SteveDesktop chain already runs, naming only chains/rows/proofs that exist in testq for that mod.
- **FlowWorks first.** It is the original testq-wired mod (`src/RimMandrake/Utils/testq/wired_mods.json`), and its
  in-game visit 1 (RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_1) is the next Archmagi Dispatch launch. Checks
  that SteveDesktop can take off that visit free the one live game.
- **ExplosiveKnockback cannot use the lane yet.** Its scenes need a proof build, and testq has no proof-build route:
  RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE.
- **Pyrelands waits.** RIMMANDRAKE_APPLY_PYRELANDS_JUDGE_EDITS_ALL_TWENTY_ATTAINABLE is editing its concept files.

**Watch the first job.** SteveDesktop had a SIMD CPU fault: garbage IL on 10 of 10 kept logs, in fault windows. The fault
monitor now reboots early when a window opens (03bd4d241f). Treat the first admitted job as the probe that
RIMMANDRAKE_DIAGNOSE_STEVE_WORLD_START_SIX_MODS_ONE_FAILURE owes: watch for the HAR error and the early-reboot pause
reason. The owner's hardware decision on STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A is still unrecorded.

**Done when:** `testq.py submit` admits at least one FlowWorks stage-6 check (pipeline_admit returns None), and the steward
leaves IDLE_BY_RULE. Run `src/RimMandrake/Utils/testq/selftest_testq_pipeline_admit.py --mutants` green.

Do not change the rule. An empty queue under 18c is not a stall. This item only gives the rule something to admit.
