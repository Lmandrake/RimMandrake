# ARTPIPE_SALVAGE_REJECTED_SIZE_MISMATCH_1 — recover the 71 already-generated renders `failed/` is sitting on

Caused by `ARTPIPE_DOWNSCALE_INSTEAD_OF_REJECT_1` (closed 2026-09-26): the daemon now
downscales an oversized-same-aspect render instead of discarding it, but the fix only
applies going forward. 71 jobs already sit in `infrastructure/artpipe/failed/` marked
`size_mismatch`, each with its real generated source PNG still intact in `_artsrc/<id>/`
(spent quota, real art, just never resized). They were left untouched when the fix
landed because the live daemon (pid 1038839 at the time) was actively writing
`failed/`/`done/`/`registry.jsonl`, and hand-editing those shared files concurrently
would have raced it.

## spec
1. Confirm the daemon is idle (or briefly pause it) before touching `failed/`,
   `done/`, or `registry.jsonl` — these are actively written by a running process.
2. For each of the 71 `size_mismatch` jobs: re-run the same aspect/size check the fixed
   `_check_size_and_validate()` now applies against the already-generated `_artsrc/<id>/<id>.png`
   (no need to regenerate — the source is already on disk). If it qualifies (oversized,
   matching aspect within tolerance), downscale it the same way the live fix does and
   move it from `failed/` to `done/` with a normal manifest, preserving the oversized
   original as `<id>_source_WxH.png` per "generated art is not disposable."
3. If a job's aspect genuinely doesn't match (the fix's remaining, correct rejection
   case), leave it in `failed/` — it was correctly rejected then and now.
4. Update `registry.jsonl`/`art_status.json` accordingly so the recovered jobs read as
   done, not failed.

## criteria
- [ ] All 71 jobs re-evaluated against the fixed size/aspect check.
- [ ] Every qualifying one recovered into `done/` with source preserved.
- [ ] Genuinely-mismatched ones left correctly failed, not force-recovered.
- [ ] `registry.jsonl`/`art_status.json` reflect the corrected state.

## why
Real generated art and real spent weekly quota sitting unused is exactly the waste
`ARTPIPE_DOWNSCALE_INSTEAD_OF_REJECT_1` was filed to stop; this is that fix's backlog.
