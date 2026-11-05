# ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS

## Why
Owner, 2026-11-04 22:16Z: "You could just poke the agents to continue where they were." The Dispatcher can resume only dead seat windows (dispatcher.py `recover()`, DEFAULT_RECOVER `claude_bounded.sh --bg --resume {session_id}`). A role run launched by role_launch.py `run-now` cannot be resumed, and neither can a timer LLM job such as findings_judge.sh. Both are always fresh. In the 14:47Z to 20:07Z outage, 8 Operations runs and Conductor rm-role-conductor-1793808830 ended on `429 usage_limit_reached` with 0 tokens. That case needs no resume, and later fresh runs served their tickets. A run cut off mid-work would lose all of its context, though.

## Spec
- role_launch: when a role run ends with `api_error`/`usage_limit_reached` (its roles/<unit>.json) after real usage, mark it resumable. Once the account answers, the next Dispatcher tick relaunches it through the same unit template, slice and budget with `--resume <session_id>` and a continue prompt. 0-usage deaths stay a fresh run on the normal schedule.
- A role run that died on the account must not count as a role failure in alarms. Today each one raised `role:Operations:failed`.
- Same for the daily findings judge (findings_judge.sh): on an account error, retry once after the account resets instead of waiting 24 h for the timer. On 2026-11-04 it failed at 15:20Z with cost 0 and was rerun by hand at about 22:20Z.
