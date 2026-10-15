# POND_CAPACITY_FIX_DOUBLING_BED

FlowWorks: detach/reattach pond bed squares multiplies capacity; truncated limited bodies

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C2-F1** CONFIRMED HIGH — Detach/reattach of a pond's bed squares can multiply its capacity (liquid created). RM_StockMath.CapacityWithoutBed keeps capacity when the LAST square leaves (RM_StockMath.cs:77-80) and ReattachBedCell skips scaling while sum==0 (RM_LiquidStock.cs:294); beds 2+4 cap 6 -> detach 2 (4) -> detach 4 (4) -> reattach 2 (4) -> reattach 4 = 12. Hand-verified.
- **C2-F7** CONFIRMED LOW — Sticky-limitless off: a truncated (>4000 cell) body is limited but grows cells without capacity. RM_StockMath.IsLimitless returns false when sticky off (RM_StockMath.cs:104-110); RM_LiquidStock.cs:140-146 appends far cells assuming truncated => limitless. Non-default setting.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
