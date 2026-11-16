# RIMMANDRAKE_READ_CODEX_SPEND_OF_A_KILLED_DESIGNER_RUN

## spec

A Codex Designer run's usage was recorded UNMEASURED whenever its unit ended without printing agent_runner's result line:
a role stopped at `run_max_s`, or any outside kill. agent_runner held Codex's stdout in memory (`capture_output`) and wrote
the events and spend files only at the very end, so a killed run left nothing on disk, and `role_launch.close_concept`
passed `res.get("codex_usage", "UNMEASURED")` into `designer_stage.close_run` (which records UNMEASURED for a missing usage).

Fix (pipeline fixes its own defects, owner 2026-11-15):
- `agent_runner.run` streams Codex's `--json` stdout straight into the events file, so every completed turn's usage is on
  disk while the run works; a timeout reads it back.
- `agent_runner.usage_of_files(spend, events)` reads usage from the spend envelope, else the streamed events.
- `role_launch.codex_usage(run, res)` uses the result line's usage, else those files beside the run's out file. Both
  Codex close paths (supervision and `close_concept`) use it.

Acceptance test: `python3 src/RimMandrake/Utils/selftest_codex_runner.py`, test `test_killed_run_usage_is_read`
(a fake Codex that writes one turn and times out; a run with no result line and only an events file). It failed on the
base commit 75a320386b (FAIL plus ERROR) and passes after: 14 tests, 0 failures. Real-path probe: a live Codex call through
the changed agent_runner wrote 4 event lines and usage {input 15379, output 5}.
