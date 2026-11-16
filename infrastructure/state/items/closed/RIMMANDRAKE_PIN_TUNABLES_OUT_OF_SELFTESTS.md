## spec
Selftests that read a shipped owner-tunable number went red when the owner changed the number: stage_ceiling_usd 60 -> 100
(fixed 948d214cdf82, FIXTURE_CEILING) and max_live 2 -> 4 (fixed 78654445c9fc, FIXTURE_MAX_LIVE), each found only when the
knob change went red. Sweep the selftests that load maturation_dispatch.json, dispatcher_schedule.json, slot_rules.json and
other owner-tunable config for assertions on a shipped tunable (caps, counts, ceilings, intervals); pin fixtures in each,
keeping at most one deliberate "shipped config is sane" range check per file.

## criteria
A1 L0: for each owner-tunable number in those configs, a scratch copy of the repo with that number changed (to another
sane value) runs the affected selftests with no new red caused by the change alone; the sweep's table is the evidence.
