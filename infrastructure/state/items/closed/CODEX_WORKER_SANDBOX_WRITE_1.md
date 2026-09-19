# CODEX_WORKER_SANDBOX_WRITE_1 — not a sandbox-write bug; the daemon was running stale code

Filed as "Codex art worker generates the image but cannot resize/copy it into
its job workspace: worker exits 1, daemon sees no image (validator never
runs), dies at ~241s = the edit-timeout+grace, not a slow run" — observed on
`codexcal_mantrap`/`codexcal_lockjaw_a`/`codexcal_lockjaw_b` (+ retries),
9/9 codex-channel jobs, all `worker_error`, all `attempt_elapsed_s` ≈ 240.5s,
all `timed_out: false`.

## What was actually true

Two real defects, neither one "the worker can't write to its sandbox":

1. **No diagnostic ever reached the manifest.** `process_gemini_job()` always
   stored `worker_stdout_tail`/`worker_stderr_tail`; `process_codex_job()`
   captured `out`/`err` locally but never put them on `result` — every
   codex-channel failure said only "worker exited 1, image_present=False"
   with no way to see codex_image.py's own `ERROR ...` line or its
   `--- last codex output ---` dump. Fixed in `artpiped.py` (this item,
   commit `847f6b71`) — codex failures now carry the same tails gemini
   already did.
2. **The live daemon process was running stale code.** The console process
   (`artpiped.py`, pid 464) had been running continuously since
   **2026-09-09 18:50:42** — before both `DEFAULT_TIMEOUT_EDIT_S`'s bump
   210→420s (comment dated "measured 2026-09-10") and fix #1 above. Python
   reads module-level constants once at import; neither change could ever
   reach that process without a restart, and nobody restarted it. Every
   "still failing after the fix" observation afterward was the daemon
   faithfully re-running the *old* 210s-ish edit ceiling under real N=3
   concurrency, over and over.

## Reproduced, then fixed, live this session

- Solo `codex_image.py edit` call against a fresh isolated `--codex-home`:
  **OK, 90s** — rules out a genuine sandbox-write/copy failure; the agent's
  own `Copy-Item` into its workdir succeeded cleanly (full transcript
  captured, confirming the mechanism the title suspected is not broken).
- 3 real jobs filed via `fill_queue.py` and drained by the **still-stale**
  live daemon (real N=3, the actual failure condition): **3/3 failed**,
  `worker_error`, `attempt_elapsed_s` ≈ 240.7s each — reproduced exactly,
  and confirmed via the new (but not-yet-loaded) diagnostic fields being
  absent from the manifest that the running process predates commit
  `847f6b71`.
- Stopped the daemon (`kill -TERM 464` — queue was idle, clean exit, no
  crash-recovery needed) and relaunched it from current source.
- Same 3 jobs re-filed, drained by the **restarted** daemon: **3/3 completed
  in 1 attempt each**, 103–156s, no `worker_error`, no timeout. They then
  failed for an unrelated, working-as-designed reason — `validate_sprite.py`
  REJECT (`worker_reported_ok_but_invalid`) — the validator judging the
  generated art itself, out of this item's scope.

## criteria
- [x] Reproduced live (not inferred) under the real failure condition (N=3
      concurrency via the live daemon, not a solo call).
- [x] Root cause identified with live evidence: a stale long-running daemon
      process, not a sandbox permission defect.
- [x] Fixed: manifest diagnostics shipped (commit `847f6b71`) + daemon
      restarted onto current source.
- [x] Verified: re-ran the identical failure condition against the fix;
      failure mode is gone (0/3 worker_error, was 3/3 before restart).
- Residual, explicitly out of scope: `n3verify2_*`'s validator REJECTs are a
  normal art-quality outcome, not a pipeline defect — no action taken on
  those prompts/references.

## Standing implication for whoever runs this daemon next
Restart `artpiped.py` after editing its own source, or any config constant
change (timeout, budget caps, thresholds) silently never takes effect. There
is no live-reload. Worth a one-line startup banner or a source-hash check if
this recurs.
