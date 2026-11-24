# Polish: one failure classifier (a record; nobody takes lines from it)

- `Stillsand/validation.py` fish and `Contagion/validation.py` extraction surgery decide a random result by 2 and 3 tries.
- `testq/archmagi_switch.py` latches the Archmagi lane on INVALID runs of class TEST too, which are not the lane's fault.
- `testq/visit_feed.py` logs "every waiting mod refused: {}" when the only waiting mod is in flight.
- `failure_counter_lint.py` does not read shell or PowerShell counters.
- `testq/ingest.py` `tries_after`: an ingest that crashes the same way on one record every time is tried every `RETRY_S` forever, and `ops_watch` `testing.ingest_gave_up_7d` never sees it (0 such crashes in 1297 done records, 2026-11-23). not handled: no count of crash retries per record.
- `testq/steward.py` `settle_wake`: a wake killed at its spend or wall cap is tried again after each 4 h cooldown for the whole incident (at most about $30 a day on one stuck lane; 1 such wake in 5268 steward lines); the `maybe_wake` docstring still says "at most once per incident".
- `rimflow verify --outcome` takes any word: a misspelt one reads UNCLASSED and leaves the run out of the pilot streak without a word at the command (its only writer, `testq/ingest.py`, sends COULD NOT LOOK).
- `rimflow/stop_resume.py`: the give-up branch can no longer be reached by a launch refusal (`of_launch` never counts), so that branch is dead code; a resume that the launcher refuses every time (its item still open) is tried every `REFUSED_WAIT_S` with no end, as the page promises.
- Codex review 2026-11-24, not significant in ordinary operation (maturation_page_counts_killed_cycle, `maturation_now.py:745`): A detached helper is killed by a fleet stop and its replacement later completes the same stage. The next maturation page shows `CYCLED: this stage has run 2 times` even though only the replacement counts. Reproduced in memory with both records assigned to the same stage and the first correctly marked `died`.
