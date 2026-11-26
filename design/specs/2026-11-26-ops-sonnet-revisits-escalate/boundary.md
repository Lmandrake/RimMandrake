# BOUNDARY: Operations revisits on Sonnet, with an escalation to Opus, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/ops_escalate.py` (`record`, `due`, `continuation_text`), `rimflow ops-escalate` in
`src/RimMandrake/rimflow/cli.py`, `incident_run`, `incident_execute` and `escalation_pass` in
`src/RimMandrake/rimflow/dispatcher.py`, `job_model`, `launch_role`, `launch_argv` and the covered-slot branch of
`decide_roles` in `src/RimMandrake/rimflow/role_launch.py`, the Operations `model_by_mode` key `revisit` in
`src/RimMandrake/rimflow/dispatcher_schedule.json`, and the Run hygiene line "On Sonnet, hand on what is fishy" in
`src/RimMandrake/rimflow/roles/operations.md`. Item: `RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT`, from the
owner's card of 2026-11-19 ("Sonnet for follow-ups only"; his words: "If we escalate to (4) then we would likely give
Sonnet Escalation: recognize something is fishy, so call out Opus to continue."). It builds on
`design/specs/2026-11-19-incident-clerk/boundary.md` (the revisit rings and the daily deep read). Each promise has a
test of its name in `src/RimMandrake/rimflow/selftest_ops_escalate.py`.

## ACCEPTS (the only inputs these readers are built for)

- **a-batch-of-fresh-run-rings.** The `fresh_run` rings of one incident pass (`incident.step`), each with or without
  `revisit: true` and `deep: true`.
- **an-escalation-row.** One line of `escalations.jsonl` beside `told.jsonl`, written by `rimflow ops-escalate --what
  "<text>" [--incident <id>]` inside a launched role run: `unit` from `RM_ROLE_UNIT`, `model` from `RM_ROLE_MODEL`,
  `continuation` from `RM_ROLE_CONTINUATION` (each set by `launch_argv`).

## DOES NOT SURVIVE (not promised)

- **a-sonnet-run-that-never-escalates.** A Sonnet run that misses what is fishy and does not type the verb gets no
  Opus run. The daily deep read (Opus) and the 07:30 and 19:30 runs (Opus) still read every open incident.
- **an-escalation-typed-by-hand.** Outside a launched run there is no run to continue; the verb refuses and names the
  repair (a note on the item).
- **a-torn-escalations-file.** A line that does not parse moves no escalation; the pass says so each tick until the
  file is repaired.

## PROMISES (each one is owed a test of the same name)

- **a-revisit-only-run-launches-on-sonnet.** A pass whose fresh rings are all revisits and none deep asks one
  Operations run marked `revisit: true`; `launch_role` and `job_model` launch it on the shipped
  `model_by_mode["revisit"]` (`sonnet`).
- **a-first-look-and-a-mixed-batch-stay-on-opus.** A batch with one ring that is not a revisit, or a deep batch, is
  not marked revisit and launches on Opus.
- **the-economy-pass-and-a-covered-slot-stay-on-opus.** A revisit run that covers the next scheduled slot runs that
  slot's mode on Opus (the 07:30 economy pass, the 19:30 run); the scheduled economy pass launches on Opus.
- **a-sonnet-escalation-launches-one-opus-continuation-with-its-notes.** A row from a Sonnet run asks one Operations
  run pinned to Opus, `escalation_of` that unit, whose message carries the row's text, its incident and the path of the
  Sonnet run's result (`<state>/roles/<unit>.json.last.txt`); its unit carries `RM_ROLE_MODEL=opus` and
  `RM_ROLE_CONTINUATION=<unit>`. The next pass asks no second run for it; a second row of the same unit asks none; a
  row met by a run already asked or the hour's budget waits and is asked on a later pass.
- **a-continuation-escalation-launches-nothing.** A row from a continuation, or from a run on Opus, asks no run and is
  read once.
