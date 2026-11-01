# RA_S18_CORE_MIGRATE_SHAPE_UNCHANGED

Relentless Agent build, step 18. Design: `design/RimMandrake/relentless_agent_design_2026-11-01.md` section 13, ruling section 14. Contract: `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`.

## step

Extraction, toy adapter, conformance

## verify

Same selftests pass before and after; word lint clean; fault table passes on both adapters

Order is measure, wall, change: a step does not start before the step it is blocked on lands. New rules run report-only first. State the narrow thing the proof shows.
