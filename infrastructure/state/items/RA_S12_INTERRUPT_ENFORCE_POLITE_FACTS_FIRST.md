# RA_S12_INTERRUPT_ENFORCE_POLITE_FACTS_FIRST

Relentless Agent build, step 12. Design: `design/RimMandrake/relentless_agent_design_2026-11-01.md` section 13, ruling section 14. Contract: `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`.

## step

Interrupts: fact hook, then stop

## verify

Planted workers stopped within limit; long build and long read left alone

Order is measure, wall, change: a step does not start before the step it is blocked on lands. New rules run report-only first. State the narrow thing the proof shows.
