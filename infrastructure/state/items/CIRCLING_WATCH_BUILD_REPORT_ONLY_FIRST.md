## Why
Requirement RW2 in `design/RimMandrake/operating_requirements_2026-11-01.md`. Read that entry first; it names the signal, threshold file and owner.

## Done when
Planted workers for test share, no change and A-B-A are named; trivial churn named; a long read-only investigation and a long build with a moving diff left alone. Stopping stays off until a labelled replay beats `false_stop_limit`.

Proved by the planted fault on the real path, not by a statement.

## verify
- L0, offline, each by its planted fault on the real path: S1 planted test-share, no-change and A-B-A workers are each named. S2 trivial churn is named. S3 a long read-only investigation and a long build with a moving diff are left alone. S4 stopping stays off until a labelled replay beats `false_stop_limit`.
- Stopping point: finish.
