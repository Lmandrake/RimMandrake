# artpipe worker_error fix 2026-10-09

Status: code landed; restart + requeue below.

## Counts (measured 06:30)

- Journal, last 48 h: 757 PASS, 89 `worker_error`, 94 `master_failed`, 91 `failed_canon`.
  `worker_error` rate is ~10% in both modes (edit 57/779, generate 32/291).
- The 89 `worker_error` lines are 77 job ids. Their state now: 63 done (requeued earlier and passed),
  11 failed later as `failed_canon` (out of scope), 2 absent from the queue (withdrawn),
  **1 still failed as `worker_error`**: `sketto_fly_plate_v3_east` (no later success for
  `sketto_fly_plate/east`). It has no derived children.
- `master_failed` in failed/: 6 have a `worker_error` parent, and all 6 parents are older than 48 h.
  None is a child of `sketto_fly_plate_v3_east`.

## Root cause

`codex exec` runs with `--output-schema manifest.schema.json`, which forces **every** assistant
text message into the manifest JSON. When the model sends any text before it calls `image_gen`
(a preamble or progress line, the house style of gpt-5.5 in codex), that message is coerced into a
`"status":"fail"` manifest and the turn ends: codex exits 0 with no image, and `codex_image.py`
prints `ERROR no image produced after Ns (exit 0)` and exits 1.

Evidence: the rollout of the failing `sketto_fly_plate_v3_east` attempt
(`w4/sessions/2026/10/09/rollout-2026-10-09T03-08-11-…jsonl`) shows 38 reasoning tokens, then two
assistant messages that are both the schema JSON, with no tool call. Of 267 parked/failed
`worker_error` manifests, **117 carry the model's own note "final response schema was accidentally
invoked before generating"**, and about 30 more say the same in other words ("response-format/channel
mismatch", "accidental formatted progress response"). The prompt does contain `Use $imagegen to …`
(`codex_image.build_prompt`), so a missing invocation line is not the cause, and prompt length is not
either (same rate for short generate prompts and long canon-retry edit prompts).

## Changes (`src/RimMandrake/Utils/artpipe/`)

- `artpiped.py`
  - Every codex prompt now ends with `NO_PREAMBLE_LINE`: call `$imagegen` before sending any message,
    because every message is read as the final manifest. This targets the cause.
  - New retryable class `_is_no_image_failure`: a run that completed (no timeout) with a nonzero exit,
    no PNG, and codex_image.py's "no image produced" line. It gets up to **2 retries (3 attempts)**,
    against 1 for other tool errors. Every retry carries `NO_IMAGE_RETRY_LINE`, a firmer line telling
    the model to call the image tool first and not reply in text. Throttles are still never retried.
  - The manifest records `attempt_log` (per attempt: exit, timeout, no_image, firm_prompt, elapsed),
    `no_image_retries` and `firm_retry_prompt`, and the failure note names the retries.
  - `default_reconcile_min_age` now uses the 3-attempt worst case, so a long no-image retry chain is
    never stolen back as an orphan.
- `mock_codex_worker.py`: new `no_image_prose` behaviour that mimics the real failure.
- `selftest_artpipe.py`: `test_no_image_failure_is_classified_retryable` and
  `test_no_image_gets_two_firm_retries_end_to_end`. `run_selftests.py`: 350/352 PASS, 0 FAIL.
- `orphan_masters.py`: candidate search now also checks the worker's own reported `out` path, which
  for pre-2026-10-02 jobs points at the retired `D:\Luke\dev\Rimworld\infrastructure\artpipe\_artsrc`.

## RustPuff orphan and active/

- The master `rot_rustpuff_v2.png` existed at the retired path
  `D:\Luke\dev\Rimworld\infrastructure\artpipe\_artsrc\rot_rustpuff_v2\rot_rustpuff_v2.png`.
  It is byte-identical (sha256 0de2d53c…) to the shipped `RustPuff_A.png`. I copied it into the
  state dir's `_artsrc`. The same was done for the second orphan, `RSW_Stareling_east`.
  `orphan_masters.py` now reports 0 orphans. The daemon claimed `contagion_RustPuff_var2` at 06:29.
- The `active/` "1 entry with 0 job json" is `.gitkeep`. That is not a stray job, so I left it.

## Requeue

(filled after restart)

## Restart

(filled after restart)
