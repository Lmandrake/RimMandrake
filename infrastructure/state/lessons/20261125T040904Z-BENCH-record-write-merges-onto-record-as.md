A step that works for minutes on a record it read at its start must merge its own fields onto the record as it is at the write, never write its old copy back: detached_helper.return_clone wrote back the run record it read before landing and bundling, and erased the continuation step's 'waits for the account switch' mark, so the timed pass said 'left_open: none waits' and four carry-ons were never started (2026-11-24). The same holds for any whole-file read-modify-write of a run record by two steps of one run.
item: RIMMANDRAKE_RETRY_CARRY_ON_REFUSED_BY_DRAIN_FOUR_RUNS_STRANDED
home: NONE
