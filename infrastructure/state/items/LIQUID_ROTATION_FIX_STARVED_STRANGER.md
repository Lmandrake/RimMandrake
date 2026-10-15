# LIQUID_ROTATION_FIX_STARVED_STRANGER

FlowWorks: converter rotation keyed map-wide stalls supplied machines; multi-input never rotates

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F4** CONFIRMED HIGH — Consumer rotation keyed map-wide by liquid: a starved machine on another network stalls a supplied one forever. MayDraw (RM_LiquidNetKernel.cs:447) keyed by LiquidDef only; CompLiquidConverter.cs:230-239 marks Starved when budget allows but liquid is short, so B (isolated, under one batch) re-starves every cycle and A (served last) never draws again.
- **C1-F16** CONFIRMED MEDIUM — Multi-input converter always runs its first liquid; never rotates. RM_ConversionMath.FirstRunnable (Machinery/RM_ConversionMath.cs:46) returns the first positive; liquid_network_semantics §3.2 says a move carrying several liquids rotates per cycle.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
