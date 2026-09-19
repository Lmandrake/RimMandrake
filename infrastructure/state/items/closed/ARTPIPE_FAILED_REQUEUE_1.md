
## spec
`infrastructure/artpipe/failed/` held 46 job/manifest pairs at triage
(2026-09-13 ~09:20Z; new failures still accruing — `nysyllin_v1` landed
mid-triage). Per-job classification:
`Transient/artpipe_failed_triage_2026-09-13.tsv` (46 rows,
`job_id<TAB>cause<TAB>evidence`; ~14-day shelf life — re-derive from failed/
manifests if stale). Three actions, in order:

1. **Drop the 27 gemini-channel jobs** (buckets `gemini_banned_*`: 15
   validator rejects, 5 size-mismatch, 4 unreadable PNG, 3 worker crash).
   Gemini is banned outright (owner channel ruling 2026-09-11, artpipe
   README) — these can never be requeued as-is. Park or purge per the
   daemon's own lifecycle; if their targets still need art, they re-enter as
   fresh codex jobs.
2. **Requeue the 16 codex transients** (9 `codex_worker_error_no_output`,
   7 `codex_timeout_300s`). Codex auth is healthy — jobs were completing at
   triage time (`done/nuitae_v1` 09:08Z... wall clock 02:08 local) — so these
   read as intermittent, not systemic. Requeue through whatever the daemon's
   sanctioned path is (do NOT hand-move files without reading the lifecycle;
   registry events must stay consistent — see the wastewing "no queued event"
   NOTEs in the daemon log for what a bypassed lifecycle looks like).
3. **Fix the canvas-size bug before requeueing its 3 jobs**
   (`codex_size_mismatch`: tool returned 1254×1254 against a requested
   512×512). That is a daemon/worker-side defect — requeueing without the
   fix just re-fails them.

## verify
failed/ contains only entries younger than this triage; the 16 transients
either completed or re-failed with a NEW captured cause (empty
stderr_tail again = not done); registry/throughput events stay consistent
(no "no queued event" NOTEs for requeued ids).

## criteria
failed/ is an actionable signal again (near-empty, every resident entry
current), not a 46-job sediment; the size-mismatch bug has a fix or a
filed defect of its own.
