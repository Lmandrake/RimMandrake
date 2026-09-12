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
