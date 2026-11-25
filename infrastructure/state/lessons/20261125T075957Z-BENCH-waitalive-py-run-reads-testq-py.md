waitalive.py run reads 'testq.py wait <job>' as HUNG after 10 min, because testq wait prints nothing while the job runs. Run testq wait in a foreground Bash call with its own --timeout, or give waitalive a --progress file that grows.
item: HARNESS_REPAIR_CAUSE_C1B99C19_3
home: infrastructure/state/facts/tool_traps.md
