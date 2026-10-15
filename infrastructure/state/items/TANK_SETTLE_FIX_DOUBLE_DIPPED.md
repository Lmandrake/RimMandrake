# TANK_SETTLE_FIX_DOUBLE_DIPPED

FlowWorks: a tank in two net components is settled twice per cycle

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F5** CONFIRMED MEDIUM — A tank in two net components is settled twice per cycle (budget and epoch-stock rule broken). SettleTick snapshots per component (RM_LiquidNet.cs ~710: view built per c from live storedUnits) while ComponentsOf(mover) can return several components for one tank. Rate not mass issue.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
