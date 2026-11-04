# RELENTLESS_LINE_FIX_REFUSED_HOLD_PLACES

## What happened
2026-11-04 22:25Z, after the token outage (14:47Z-20:07Z): Relentless read places_live 0 with the breaker closed.
The reading showed 19 `concept_refused` acts and one wait, "health degraded: content paused while system items wait".

Cause: 19 queued SYSTEM items were refused by the Designer's gate (`first_touch.hold`). Each names a mod whose Designer
pass is only `proposed`: FlowWorks (FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS), and Contagion, EnvironmentalHazards,
FeverWood and Stillsand (BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS). Examples: nine HARNESS_REPAIR_CAUSE_* items,
STEVE_LANE_UNSTICK_BRAKED_UNOWNED_B4F8, BRIDGE_FLOOD_FIX_RUNS_EVERY_THREE_HOURS and MODCHECK_FINDINGS_FIX_WRITTEN_AS_REPR.

How the line jammed:
- `lease()` walks past a refused item.
- `enrol()` still counted each refused item as a line place, because `parked()` did not know the gate.
- So in_turn was 19 against max_queued 8. Both sys_room and room were negative, and nothing enrolled.
- The other system items were blocked, held or waiting on `not_before` (OPS_METRONOME_MIGRATE_CLOCKS_FENCED and
  NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS: "time, not work").
- Content is owner-held under `only_system_and_live`.
- Result: no worker could start.

## Fix
`relentless.parked()` treats a gate-refused item like its other parked cases. It keeps its order but holds no max_queued
place, so the line tops up with system items that can run.

Test: `selftest_relentless.py::t_gate_refused_items_hold_no_line_place`, with an unrefused control.

## Still true after the fix
- The refused items wait for the two Designer passes. Those are the owner's sitting, `needs=owner`.
- `content_paused()` still counts a refused queued system item as "waiting". That is harmless while
  `only_system_and_live` holds content back. Once he lifts that hold, a refused system item would pause content
  indefinitely. Revisit then.
