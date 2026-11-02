# AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS

The owner, 2026-11-01: "Every day we should ask if each agent can be improved based on our evidence. That's the beauty
of making them agents. Same with reusable skills not agent specific."

Design: design/RimMandrake/daily_agent_improvement_2026-11-02.md (transfer audit counts in its section 1).

## built (BENCH, 2026-11-02)
- Step 0 gather: src/RimMandrake/Utils/agent_improve.py, selftest_agent_improve.py (mutation-proven), paused
  `measure` row `agent_improve` in dispatcher_schedule.json (no unit installed).
- It is also the harvest of Relentless learned.md (107 files) and reject reasons, which nothing read before.

## built (BENCH, 2026-11-02), steps 1 to 3 and section 4 except 4.3
- `agent_improve.py run [--apply]`:
  - the Curator and the Judge are each a fresh `claude -p` with no tools; one diff per target, at most 15 lines a side;
  - the edit region is the AST span for relentless.py's worker_prompt;
  - the apply step runs check, validate_skills and the target's selftests, then commits with `Delegated: technical`,
    tags agent/<target>/v<N>, and writes the change record and the verdict JSON;
  - the next day's recheck folds into the change record, and a held target needs a passing recheck;
  - the ramp (L0/L1/L2) counts committed verdicts only;
  - `materialize` writes any tagged version into a directory.
- Shas: 427c3c7f0e and d0e7cf984a (build), 48a6e0fbbc (apply hardened, 12 GPT rounds), 383b26a722 (selftest
  oracles, 4 rounds). Both files are CLEAN.
- Hand run of 2026-11-01: D:\ClaudeWork\rimmandrake\agent_improve\day1.md. One KEEP applied: 1394a96c,
  agent/rimworld-modding/v1. Two proposals filed: RELENTLESS_CLONES_REPAIR_REMOVE_OF_GONE and
  PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET.
- The schedule row runs `run --apply` and stays enabled:false with no unit installed: switching it on is the owner's.

## owed elsewhere
- 4.3 generalization check: AGENT_IMPROVE_BUILD_GENERALIZATION_CHECK.
- Curator "none" with no reason: AGENT_IMPROVE_REPAIR_SILENT_NONE.
- The rm-agent-improve.{service,timer} unit, when the owner enables the timer.

## verify
- selftest_agent_improve GREEN; a dry gather of 2026-11-01 gives <= 6 targets, agents first, <= 25 pieces each.
- After step 3: one day's applied diff appears in Transient/delegated_digest_<day>.md.
