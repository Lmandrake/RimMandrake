# RA_S06_GUARD_ENFORCE_SEEN_RED_TWICE

Relentless Agent build, step 6. Design: `design/RimMandrake/relentless_agent_design_2026-11-01.md` section 13, ruling section 14. Contract: `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`.

## step

Base and guard red; evidence gate

## verify

A check that cannot go red is refused; a guard that leaves it green blocks. Pit case replayed: `false_pass` goes red; a `preserve` clause passes on guard red alone

Order is measure, wall, change: a step does not start before the step it is blocked on lands. New rules run report-only first. State the narrow thing the proof shows.
