## spec
Conductor quick run rm-role-conductor-1795232363 (7:43 PM PST 2026-11-20) used 436026 weighted tokens against
its 360000 advisory budget (Dispatcher escalation role:Conductor:overbudget, 2026-11-21T03:44:16Z). That run
triaged an incident, filed an item with its oracle and launched a fixer. Find what a quick check spends on and
cut it (move triage to a helper or Operations), or raise the budget in `dispatcher_schedule.json` with the
danger it guards named beside the number.

## verify
Read the weighted totals of the next three scheduled Conductor quick runs in the Dispatcher journal.

## criteria
The next three quick runs each stay under the advisory budget, or the budget line names its danger and evidence.
Acceptance test: none, a cost trim judged on the next runs' measured totals.

## refs
file: src/RimMandrake/rimflow/roles/conductor.md
file: src/RimMandrake/rimflow/dispatcher_schedule.json
