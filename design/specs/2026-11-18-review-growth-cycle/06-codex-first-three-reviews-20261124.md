# The first three Codex reviews of pipeline code after the 2026-11-23 restart, counted (2026-11-24, about 12:05 AM PST)

Item: `RIMMANDRAKE_READ_FIRST_THREE_CODEX_PIPELINE_REVIEWS_COUNT_SIGNIFICANT`. The reviews were made by the run
`RIMMANDRAKE_SPEND_CODEX_ALLOWANCE_BEFORE_TUESDAY_RESET_48_LEFT`, read-only, under
`src/RimMandrake/rimflow/roles/code_review.md`. Prompts, raw answers and fix jobs:
`D:\ClaudeWork\rimmandrake\conductor\codex_spend_1124\reviews\<name>\result.txt` and `...\fixes\<name>\`.

The question: does Codex obey the brief's significance rule? Before these reviews it was UNMEASURED.

## The count

"Codex: Problem" is the class in Codex's raw answer. "Reader: significant" is the finding that the launching run sent
to a fix job. "Shown" is a red test on the old code that went green on the fix. Every number is read from the files
above.

| review | findings | Codex: Problem | reader: significant | shown and landed |
|---|---|---|---|---|
| `pipe_run_end_wake` (the run-end wake, `run_end_wake.py`) | 3 | 3 | 0 | 0 |
| `pipe_bridge_hands` (bridge v2 hands, C# cores) | 4 | 4 | 2 | 1 (`slice_cancel_bypasses_driver`, 7aa1752ee4) |
| `pipe_launch_permissions` (`launch_permissions.py`) | 6 | 5 | 2 | 1 (`wt_server_template_invisible`, 7aa1752ee4) |
| **first three** | **13** | **12** | **4** | **2** |

- Of the 4 sent to a fix, 1 was NOT TRUE: `all_masks_unreadable_value`. The condition page uses Strong Kleene logic,
  so a false child decides an `all` condition before the unreadable value matters. The fix job quoted the page.
- Of the 4 sent to a fix, 1 went to polish after its fix was built: `publish_skips_modcheck_launch`. The fix made each
  ordinary `./publish` pay 25 to 35 s, and the nightly look already reads the case. The line is in
  `design/specs/2026-11-23-launch-permissions/polish.md`.
- The 8 Problems that were not sent need an input that ordinary operation does not reach, or name a test that is
  missing but no misbehaviour. This run read each one again and agrees:
  - `pipe-reason-counted-as-switch`: a `./pipe off` reason with a newline whose second line reads like a family switch.
  - `default-account-reader-untested`, `done-heading-untested`: a missing test; nothing is wrong now.
  - `later_batch_rewrites_run_act`: a second batch that reuses the id of an act that never ran.
  - `refused_bind_renews_lease`: the old driver binds to a gone thing after its lease ended.
  - `live_masks_explicit_mode`: a launch with an explicit `--permission-mode default`, which no launcher writes.
  - `broken_shell_reads_clean`: a launcher with a Bash syntax error, which fails at once when it runs.
  - `missing_steve_fleet_reads_clean`: one moment in a fresh SteveDesktop setup.

## The answer

Codex does not apply the significance rule by itself. In these three reviews it called 12 of 13 findings Problems;
the reader kept 4, and 2 landed. Its traces are mostly true (3 of the 4 that a fix job tested), so its fault is the
bar, not the facts: it calls a rare input a Problem.

A second count, of six reviews on 2026-11-24 evening on files with no boundary page, kept 15 of 18 Problems
(`05-codex-reviews-no-page-20261125.md`). Why the two counts differ is UNMEASURED (one
guess: those files had no page and fewer tests, so more faults lay on ordinary paths). Both say the same thing for the work: the run that reads a Codex review judges each Problem by the significance rule
itself. It never sends a Problem to a fix because Codex called it one.
