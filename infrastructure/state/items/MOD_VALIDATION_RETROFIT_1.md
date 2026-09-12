# MOD_VALIDATION_RETROFIT_1 — every shipped mod gets a validation.py

Owner ruling 2026-09-12: FULL wave, not campaign-critical-only. Starts only
after MOD_VALIDATION_PIT_PILOT_1 ratifies the sheet format. Spec:
`design/RimMandrake/mod_validation_runner_spec.md`.

## spec
For every shipped RM_/RSW_/RUT_ mod: write its validation.py (settings toggles as
floor, beyond-toggle components for complex functions), batch runs into shared
minimal-list sessions, record each green run. Failures file findings and do not
stop the wave.

## verify
- Every shipped mod has a registry entry; `modcheck status` lists no mod
  without one. A red mod has a filed finding, never a silent gap.

## status (FOUNDRY, 2026-09-12)

Still correctly blocked, one gate narrower. `MOD_VALIDATION_RUNNER_1` (the
library) is built, offline-verified, and now live-proven. `MOD_VALIDATION_
PIT_PILOT_1` RAN GREEN live (3/3 components, zero findings) — the only
remaining gate for this item to start is the owner ratifying the sheet
FORMAT itself, not whether the pilot works. Sheet awaiting his look:
`D:\Luke\dev\Rimworld\Transient\modcheck\Pits_20260912T231116Z.html`.

Also worth knowing before this wave starts: `runner.run()`'s modlist-swap
orchestration (`cli.py run <mod>`) has a fixed-but-unexercised-live bug
(subprocess targets were being launched via `sys.executable`/`python.exe`
instead of plain `python3` — see `MOD_VALIDATION_RUNNER_1`'s item file),
and `swap_to_test_list()` still only swaps to the fixed MINIMAL list
rather than composing MINIMAL + each mod under test. Confirm both work
live (or fix them) before batching this wave through `cli.py run`, rather
than discovering it mod #1 into the retrofit.
