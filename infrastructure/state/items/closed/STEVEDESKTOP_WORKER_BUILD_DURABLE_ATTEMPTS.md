# STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md, section 4 helper #3 (H-A).

## spec
- `infrastructure/stevedesktop/worker.py` runs on SteveDesktop in ~/rm/runner, started over ssh by the testq dispatcher.
- `start` takes a job (testq/schema.py `testq.job/1`) on stdin, makes a unique attempt dir `<job>.a<n>`, and detaches the
  attempt as a transient systemd user unit (fallback: a new session), so a dropped ssh never kills it.
- The attempt runs under `host_guard.held("RUNNER", ...)`, pins the runner HEAD (refuses SOURCE_SHA_MISSING), deploys,
  loads the game, runs modcheck, writes a heartbeat every 15 s and one `testq.result/1` JSON into the outbox.
- Watchdog: a run that outlasts `timeout_s` is killed, the game restarted once, and the run retried once (section 6).
- Duplicate delivery: `start` for a job with a live or finished attempt returns that attempt, never a second run.

## verify
- selftest_steve_worker.py (mock phases): DONE, INVALID, HANG -> retry, duplicate start, guard held.
- One real attempt on SteveDesktop with a result JSON in the outbox.
