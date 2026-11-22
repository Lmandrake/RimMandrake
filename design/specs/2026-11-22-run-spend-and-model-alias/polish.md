# Polish: run spend and model alias (no ticket; a record)

- `dispatcher_schedule.json` `seats.BENCH.model` holds the typed id `claude-fable-5-2`, and `seat_restart.py:1241` passes it to
  `claude --model` as it is. Nothing has failed from it, and it goes stale only when the Fable id changes. It could hold
  `fable` and go through `role_launch.launch_model`, as the profile installer now does.
- `Utils/art_eval/runner.py:67` reads `ANTHROPIC_DEFAULT_<RUNG>_MODEL` itself. It follows the rule (read the
  environment), but it is a second reader of the alias table.
- `role_launch.run_spend` gives 0 for a record that carries neither a figure nor a `budget`. Every role run carries a
  budget (81 of 81, measured 2026-11-22), so ordinary operation does not reach it.
