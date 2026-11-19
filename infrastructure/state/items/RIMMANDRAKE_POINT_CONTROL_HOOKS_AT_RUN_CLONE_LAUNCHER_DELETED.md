## spec
`control.claude_settings` (the run's PostToolUse hook, the stop channel of `pipe stop --write-now`) and
`control.hook_cmd` (the unit's `ExecCondition` start check and `ExecStopPost` end receipt, inserted by `launch_unit`)
name `os.path.abspath(__file__)`: the control.py of whichever process launched the run. A continuation
(`left_open_continue.py`) can launch from the PREVIOUS run's pool clone, and that run's return deletes its clone, so
every hook of the new run points at a file that no longer exists.

Measured 2026-11-18 ~16:00 PST on unit `rm-detached-bench-rimmandrake-fix-slot-allocator-override-1795046257`: every
tool call of the run printed `can't open file '/home/mandrake/rm/relentless/clones/OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO.det/src/RimMandrake/rimflow/control.py'`
(only `OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO.det.lock` is left of that clone), and `systemctl --user show -p
ExecStopPost -p ExecCondition` named the same dead path. So the run cannot be stopped through the stop channel, and
its `ended` receipt (ExecStopPost=-, failure ignored) never reaches the control store.

Fix: the hooks name the RUN's own clone's control.py when it has one (it lives until the run's return, which is after
claude and after the ExecStopPost receipts), the launcher's only as a fallback. `claude_settings(p, clone=)`,
`hook_cmd(..., clone=)`, `launch_unit(..., clone=)`; detached_helper and role_launch pass the run's clone. Codex's
review (`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`, its finding 6) found the same flaw in the
stop order's escalation timer (`schedule_escalation`): it now runs through detached_helper's stop resolver, this
control.py first, then the seat clones'.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` case `t_hooks_in_run_clone` (12 checks). Watched
red on base 86c92d636 (TypeError: claude_settings() got an unexpected keyword argument 'clone'; every other case
passed); its escalation half watched red the same way (TypeError: no `runner`).

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/role_launch.py

## criteria
- `t_hooks_in_run_clone` passes; red on base.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
