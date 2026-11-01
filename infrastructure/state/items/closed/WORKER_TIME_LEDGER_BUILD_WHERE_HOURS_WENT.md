## Why
Requirement RW1 in `design/RimMandrake/operating_requirements_2026-11-01.md`. Read that entry first; it names the signal, threshold file and owner.

## Done when
A fixture transcript of known split reads within 5%; a replay of hand-labelled real runs reports both missed waste and wrongful stops. Thresholds in `relentless_rules.json` block `circling`. Reuse `pulse/agents_timeline.py`. Read-only.

Proved by the planted fault on the real path, not by a statement.

## verify
- L0, offline, each by its planted fault on the real path: S1 fixture transcript of known split reads within 5%. S2 replay of hand-labelled real runs reports missed waste and wrongful stops.
- Stopping point: finish.
