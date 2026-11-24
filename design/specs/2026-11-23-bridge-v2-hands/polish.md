# Polish: the generic hands (no ticket, nobody works this list)

- `thing.field` of the condition language still reads any property; the `value` probe is the reviewed reader (2026-11-23).
- A track on a number that changes every tick makes one box and one row a tick.
- A batch takes a string for an array argument only when the tool declares it; JSON text arguments are passed as text.
- Codex review 2026-11-24, not significant in ordinary operation (later_batch_rewrites_run_act, `JawaBenchHandsCore.cs:596`): Schedule `jawa/map_info` as act `snapshot` at offset 10 in a run that hits at offset 1. Its closed status correctly reports `snapshot` as `not_tried`. Execute a standalone batch with the same act id and read the first run's status again. The closed run now reports `snapshot` as `done` at offset 10 and supplies the later ...
- Codex review 2026-11-24, not significant in ordinary operation (refused_bind_renews_lease, `JawaBenchHandsCore.cs:294`): Let an open session expire and confirm `leaseEnded: true`. The original driver then attempts to bind an alias to a thing that no longer exists. The bind returns `UNKNOWN_THING`, but state now shows a renewed lease and a second caller's abort returns `NOT_THE_DRIVER`.
