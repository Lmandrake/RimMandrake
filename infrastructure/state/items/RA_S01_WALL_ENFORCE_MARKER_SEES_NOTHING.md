# RA_S01_WALL_ENFORCE_MARKER_SEES_NOTHING

Relentless Agent build, step 1. Design: `design/RimMandrake/relentless_agent_design_2026-11-01.md` section 13, ruling section 14. Contract: `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`.

## step

Wall profiles on the real launch path; Marker gets exported tree, no store, no env root

## verify

Unit run tries to read store, `.git`, `conversations/`: denied. Real check still reaches a verdict

Order is measure, wall, change: a step does not start before the step it is blocked on lands. New rules run report-only first. State the narrow thing the proof shows.
