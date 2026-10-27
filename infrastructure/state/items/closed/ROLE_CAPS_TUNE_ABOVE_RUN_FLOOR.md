# ROLE_CAPS_TUNE_ABOVE_RUN_FLOOR

The role token caps in `src/RimMandrake/rimflow/dispatcher_schedule.json` (taken from roles/conductor.md and
roles/operations.md) are below what one headless `claude -p` run costs before it does any work.

Measured 2026-10-27 (evidence `D:\ClaudeWork\rimmandrake\role_launch_2026-10-27\proof\RESULT.md`): a trivial
"reply OK" haiku run from the bench clone used 35,242 tokens (run 1) and 52,888 tokens (run 2), counting all four
usage fields (input, cache_creation, cache_read, output). Most of it is the cached system prompt + CLAUDE.md /
context load.

- Conductor quick_token_cap 30,000: every quick check, even an empty one, is over budget -> an overbudget ALARM
  each run (role_launch.py checks the result's usage). AMBER x0.6 = 18,000 and RED x0.4 = 12,000 are lower still.
- Operations run_token_cap 60,000 leaves ~10k for work.

Decide: (a) raise the caps, (b) count only non-cached tokens (input + output + cache_creation) against them, or
(c) both. role_launch.run_tokens() is the one place that sums them. Owed before any role is enabled.
