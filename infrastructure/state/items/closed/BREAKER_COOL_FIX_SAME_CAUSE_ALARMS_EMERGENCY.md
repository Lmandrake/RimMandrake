## Why
Requirement DI2 in `design/RimMandrake/operating_requirements_2026-11-01.md`. Read that entry first; it names the signal, threshold file and owner.

## Done when
Plant a pool refusal: breaker does not open. Plant a failing launcher: it opens, reopens on the same cause, and raises an emergency. No cool exceeds `breaker_cool_max_s`. Thresholds in `relentless_rules.json`.

Proved by the planted fault on the real path, not by a statement.
