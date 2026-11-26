To find where a slow rm-scratch-reap run spent its time: last_run.json holds phase_s for the last run only, but each row in runs.jsonl keeps act_s (and archive), so per-run apply time and its slowest paths can be summed for every past run. The /tmp phase looked guilty and took 15 s; apply held 70 to 90 percent.
item: RIMMANDRAKE_BOUND_SCRATCH_REAP_RUN_THAT_GREW_FOUR_MIN_TO_TWO_HOURS
home: skills/rimflow-operations/references/traps.md
