# ARTPIPE_TWINS_PRUNE_FAILED_COPY

32 artpipe jobs (60 file names) are filed in BOTH `done/` and `failed/` of the live queue
(`D:\ClaudeWork\rimmandrake\artpipe`). No tool in the repo prunes them. Review wave 94 measured and traced them. It
did not prune, because no cleanup operation is documented.

## Evidence
All under `D:\ClaudeWork\rimmandrake\review_w94_twins\`:
- `twins.py`: the measuring script.
- `twins.json` and `twins.txt`: the per-id layout.
- `twins_seq.txt`: the registry timeline of each id.
- `twins_cause.txt`: the byte comparison with the legacy tree.

## Measured
- 28 ids have job + manifest in both dirs.
- 3 have job + manifest in done and only the manifest in failed.
- 1 has job + manifest in done and only the job in failed.

## Cause
- 3 ids were already twins in the legacy tree (`D:\Luke\dev\RimMandrake\infrastructure\artpipe`).
- 4 ids come from `artpipe_state.py migrate`, where `STAGE_RANK` gives done and failed the same rank. Fixed in review w94 (commit "artpipe_state migrate filed one job in both done/ and failed/"). Re-running migrate no longer recreates them.
- 24 ids exist only in the new state dir, with registry timelines between 09-24 and 10-05:
  - (a) The job failed, was re-run and passed, and its failed/ files were left behind.
  - (b) The job passed, was regenerated, and the regen failed (failed_canon). The old passing image stays in done.
  - Both patterns match a manual copy rather than a move. `requeue_flakes` and `requeue_quota_failures` move both files, and fill_queue refuses an id that already exists.
- 1 id, `cauldronsoilrich_breathes_a`, comes from 10-20: its `failed/X.manifest.json` got into pending and was claimed as job id `X.manifest` (bad_job_file). That left `failed/X.manifest.manifest.json`.

## Installs
- Only 1 twin has a `collected.jsonl` entry.
- `collect` requires a done/ manifest unless `--allow-failed` is passed.
- No twin carries `install_to`.
- No art was installed from a failed twin.

## spec
Write a documented prune, e.g. `artpipe_state.py twins [--apply]`:
- Report each twin with its registry's last validated event.
- Move the stale terminal copy to `_pruned_twins/` (move, never delete) with a provenance line.
- Keep the copy whose registry `validated` event is newest. For pattern (b) that is the failed record, while the done image stays the installed truth. That needs a rule, so a human or a ruling decides it before `--apply`.
- Also remove `failed/cauldronsoilrich_breathes_a.manifest.manifest.json`.
