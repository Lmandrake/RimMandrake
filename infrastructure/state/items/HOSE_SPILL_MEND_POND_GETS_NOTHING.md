# HOSE_SPILL_MEND_POND_GETS_NOTHING

FlowWorks: hose drain spills instead of returning to a pond; spills nobody accepts vanish; wall-blocked outlet order

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F10** CONFIRMED MEDIUM — Stopped hose drains as filth instead of returning levels to an adjacent pond (and spill over water vanishes). PlaceHeld (RM_LiquidSpill.cs:149) accepts only RM_OutletKind.Channel, never Body; Spill() over water fails TryMakeFilth and the units leave with a WarningOnce (RM_LiquidSpill.cs:196-206). An Intake end lying in a pond drains into the pond cell -> lost.
- **C1-F11** CONFIRMED MEDIUM — Spill that no cell accepts still debits the source (silent-ish loss). RM_LiquidSpill.Spill is an always-accepting Sink (OutletLeg default, :84); on failure it counts Unplaced and breaks. Not the sanctioned overflow.
- **C1-F12** PLAUSIBLE LOW — Outflow end under a wall still pours into adjacent channel/pond. Outlet (RM_LiquidSpill.cs:28-70) tests Standable/IsExcavated of the end only after the adjacent searches. Live: wall over an Outflow end beside a channel, run a pump cycle, read channel fill.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
