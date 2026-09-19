## spec
Owner's 2026-09-11 card-sitting ruling ("rembg exempt+capped", commit `c1fc08412`):
rembg cutouts are exempt from the daemon's general N-way worker concurrency
and instead capped to run one at a time — measured 2026-09-09, 3 concurrent
rembg/ONNX loads died in multiprocessing's resource_tracker under a bounded
cgroup. That serialization already existed, but only inside
`skills/generating-images/scripts/gemini_image.py`'s `--cutout` path (an
inline `fcntl.flock` on `~/.cache/rwgfx_rembg.lock`, duplicating the actual
rembg call rather than calling the shared script). `rembg_cut.py` itself —
the general-purpose, documented entry point any other caller (codex-channel
sprites, a future worker) would reach for — had no guard at all.

## verify
Moved the flock into `rembg_cut.py`'s `main()` (same lock path,
`~/.cache/rwgfx_rembg.lock`, so it stays mutually exclusive with any
in-flight `gemini_image.py` cutout too), held only around the `remove()`
call. Refactored `gemini_image.py`'s `--cutout` block to shell out to
`rembg_cut.py --input --out` instead of re-implementing the rembg call
inline — one flock owner, not two copies of the same guard. Both files
parse clean (`ast.parse`); no `rwgfx` venv available in this offline
environment to run rembg end-to-end, so this is a static/logic review, not a
live-execution proof — flagged here rather than claimed as tested.

## criteria
(a) `rembg_cut.py` self-guards against concurrent ONNX loads regardless of
caller — MET. (b) No caller left duplicating the guard — MET
(`gemini_image.py` now calls the shared script). (c) Live proof under actual
concurrent load — NOT done, needs the rwgfx venv; whoever next runs the
Gemini channel with 2+ workers hitting `--cutout` simultaneously can confirm
no crash and close this residual gap, or the daemon's own throughput log
will simply show no more ONNX resource_tracker deaths.
