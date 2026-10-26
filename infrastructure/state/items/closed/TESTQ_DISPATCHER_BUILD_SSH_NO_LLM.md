# TESTQ_DISPATCHER_BUILD_SSH_NO_LLM

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md, sections 3 and 6, helper #4 (H-A).

## spec
- `src/RimMandrake/Utils/testq/`: schema.py (the job/result interface H-B consumes), queue (submit/show/cancel/list,
  files under D:\ClaudeWork\rimmandrake\testq\{pending,running,done} with atomic renames), dispatch tick.
- The tick (systemd user timer, 60 s; no LLM anywhere) reconciles running jobs by polling the worker over ssh, fetches
  each finished attempt's result, moves the job to done/, and admits the next ready job (priority, not_before,
  owner_gate, supersedes) to SteveDesktop, preferring the current train (same profile).
- SSH down: no new sends, a probe every 5 min, the attempt id is asked for before any retry.
- Archmagi backfill exists behind an explicit switch and only takes the archmagi host guard when the bridge is free.

## verify
- selftest_testq.py on a temp queue with a fake ssh: submit, admit, duplicate tick, ssh down, cancel, supersede.
