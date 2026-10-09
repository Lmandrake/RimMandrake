# enact.py full-file review, 2026-10-09 (BENCH)

Scope: enact.py (1020 lines), ingest.py + serve_gated.py parts touched by 6f7940ee8 / 374c9b87b.

## Findings
1. STALE LETTERS (gap). A touched decisions file keeps its OLD snapshotId when the snapshot is rebuilt. ingest checks used letters
   against the ruled snapshot (git history) but skips a letter the ruled snapshot never had. Scenario: rebuild1 adds letter F, he
   clicks F, rebuild2 re-sets F to other pictures; ingest installs the new F. Fix: rows whose used letter is absent from the ruled
   snapshot AND whose click predates the current snapshot `built` are skipped and listed as CONFLICT.
2. REJECTED PICTURES FROM THE WRONG SNAPSHOT. rejected_events() read the CURRENT snapshot's IN GAME labels: a redo clicked
   before an install, ingested after a rebuild, rejects a picture he never saw. Fix: use the ruled snapshot's row.
3. RE-INSTALL OVER A NEWER PICK. Re-enacting an older decisions file for the same row reinstalls its pick over a newer pick from a
   later sheet (protection ignored same-row keeps). Fix: a same-row keep from another file with a later `at` is a CONFLICT.
4. clear_followed race: read -> replace window against a live sidecar save. Fix: verify bytes unchanged before replace, retry.
5. Not findings: dry run writes only the documented --mark-done event; --no-deploy gates deploy; purge of live/kept is a
   CONFLICT; job ids are deterministic and fill_queue dedups.
6. Noted, not changed: 374c9b87b treats a no-note `redo` with any past followed note as fulfilled when no job matches
   (a fresh bare redo click after a followed note and a dropped job is swallowed). Owner's stated intent; left.

## Result
Fixed 1-4 with selftests (selftest_enact 100% PASS; run_selftests 254 pass, 1 FAIL selftest_utinnipatches_dump = unrelated def-dump drift). enact.py, ingest.py, serve_gated.py read in full; marked clean after the fix commit.
