## spec
Owner ruling (2026-11-12, via Conductor): KEEP the bridge validation observatory design and build it small. His words:
"Yes, keep this too." Design: `design/RimMandrake/bridge_validation_observatory.md` (2026-10-03 draft, "Nothing is built";
the item it named, BRIDGE_VALIDATION_OBSERVATORY_1, was never filed, and this item replaces that name).

### Standing ruling it keeps (owner by card 2026-10-03)
A bridge run report **leads with REQUIRED CHECKS PROVEN**, the per-mod must-have checks each with a trustworthy pass/fail.
Checks/sec, commands/min and checks passed are diagnostics underneath, never targets.

### First small slice
1. The bridge client appends one JSONL event per call (start, end, tool, run id) to a run stream. Reuse the existing
   bridge call log if it already holds this, and measure before adding anything.
2. An offline `obs report <run>` folds the stream after the run's own verdict is written. Its first line is "required
   checks proven: N of M", against the mod's required-check list. Below it go new / recurring / resolved findings and
   where the bridge time went (tick calls, reads, waits; see `design/RimMandrake/live_test_speed_assessment_2026-11-12.md`
   §2 for the split measured by hand).
3. No LLM and no quota. The report never gates a run.

### Done when
One real proof run (for example GSS `proof_all.py`) has a report whose first line is required checks proven, and the
time split matches a hand measurement within 10%.
