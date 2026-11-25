# The account plan in more detail

Source: `src/RimMandrake/Utils/account_plan.py` (the plan file, the decision, the week ahead, Burn Mode, the gate, the
notice of each machine, the commands, the timed pass), `account_plan_machines.py` (ssh to another machine),
`selftest_account_plan.py` (one check per promise), `account_plan_mutants.py` (the planted faults). Door: `./acct`.
Page of promises: `design/specs/2026-11-24-account-plan-one-file/boundary.md`. Design and the census of past plan
changes: `design.md` and `census.md` beside it.

Files in `~/.local/state/rimmandrake/account_plan/` (written only by the tool):

- `plan.json`: the plan. `history.jsonl`: each change, with the plan before and after (undo reads it).
- `log.jsonl`: one line for each timed pass: the decision, its reason, what each listed machine got.
- `decision.json`, `burn_mode.json`: the published state of the last pass, which the gate and the allocator read.
- `frame.json`: the slow readings of the last pass (Codex, JPL GenAI). `machine.<name>.json`: the last notice that
  reached that machine.

The actuator's folder is `D:\ClaudeWork\rimmandrake\switching_plan\` on each machine: `notice.json` (what a launcher
and the hooks read; ignored when over 20 min old), `markers/` (a switcher call in flight or failed), `state.json`, and
on a following machine `follows.json` (the mark that its notice comes from the deciding machine). A `HOLD` file made by
hand there is still obeyed and shown by `./acct status`; `./acct hold` is the door.

One pass: read the plan file, read the meter (poll when a reading is old near a line), decide, hand the decision to
the actuator (`switching_plan._check`: warn, save order, pause, arm, use, disarm, or a fleet stop), publish the state,
write each listed machine its notice, start again the runs that waited for the switch. Unit timeout 2700 s.

Test a change without the live plan: `./acct whatif -- <a write>`; or a copy of the plan folder named by
`RM_ACCOUNT_PLAN_DIR` (with `RM_SWITCH_PLAN_DIR` for the actuator's folder), as the selftest does.
