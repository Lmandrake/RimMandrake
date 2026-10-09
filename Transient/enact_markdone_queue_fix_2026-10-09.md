# enact: marked-done / followed notes must not re-queue (2026-10-09)
Root cause: in `enact.build_plan` the queue branch tested `elif dec == "redo"` BEFORE the `done_marks` branch, so a row with decision redo queued a job even though `--mark-done` (or notes_followed) showed its note was carried out.
Fix: `fulfilled` flag (note present: (sheet,row,note) in done_marks; no note: row has notes_followed or any done mark) -> redo skipped, listed under done. A new typed note still queues.
Selftest: 3 cases added to selftest_enact.py. Stray job moved to D:\Luke\dev\_artpipe\_withdrawn\enact_markdone_refire_2026-10-09\; not in pending/.
