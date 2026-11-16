# RIMMANDRAKE_HOLD_CODEX_DESIGNER_AT_THE_QUARTER_LEFT_LINE

## spec

The brief of RIMMANDRAKE_DRAFT_BIOME_DESIGNER_PASSES_WITH_CODEX_BEFORE_RESET: "stop launching drafts at 25% left and say
so." A detached run can watch that line only while it lives; the DesignerCodex lane keeps chaining stages after it ends
(every answer he gives chains the next stage), and its only Codex gate was agent_runner's 90% refusal. The role's
throttle bands do not bind it either: caps are advisory by default (ROLE_DEFAULTS caps_advisory, owner 2026-11-02).

Fix: `role_launch.codex_stop(cfg, reading)`: a Codex role with `codex_stop_week_left_pct` holds a launch (the request
stays pending, one alarm with a Conductor-log line per held job) while the measured Codex week left is under the line.
DesignerCodex sets 25. It is a hold until the weekly reset, not a token cap.

Acceptance test: `python3 src/RimMandrake/Utils/selftest_codex_runner.py`, test `test_codex_stop_line`. Failed on the
base (ERROR), passes after; selftest_role_launch, selftest_role_run_now, selftest_dispatcher, selftest_role_caps_advisory green.
