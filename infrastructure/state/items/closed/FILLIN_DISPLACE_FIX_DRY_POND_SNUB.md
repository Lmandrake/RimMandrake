# FILLIN_DISPLACE_FIX_DRY_POND_SNUB

FlowWorks: fill-in never offers a fully drained pond; 6000-cell walk cap destroys

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C5-F8** CONFIRMED MEDIUM — Fill-in beside a FULLY drained pond destroys liquid the pond had room for. Displace walks IsExcavated||IsSourceCell (RM_MapComponent_Excavation.cs:1135); IsSourceCell needs IsNaturalLiquid (:764-770), false on a dry bed, so phase 2 never offers the pond; ReportOverflow (:1162) destroys it although CanReturnLevels would accept.
- **C5-F9** CONFIRMED LOW — Displacement walk gives up after 6000 cells and destroys the rest. RM_MapComponent_Excavation.cs:164,1089 MaxComponentCells=6000 caps the walk before ReportOverflow; huge channel networks only.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
