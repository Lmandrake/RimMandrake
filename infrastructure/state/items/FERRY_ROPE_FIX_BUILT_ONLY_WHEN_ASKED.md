# FERRY_ROPE_FIX_BUILT_ONLY_WHEN_ASKED

FlowWorks: ferry rope cells built only on read (undrafted routing ignores rope); same-bank pairing

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C6-F1** CONFIRMED HIGH — Ferry rope cells are only built when something reads them; undrafted routing can ignore a valid ferry (after load AND after pairing). ropeCells is derived, not scribed (Rivers/RM_MapComponent_RiverCurrent.cs:54); MarkWorksDirty (:72, called by TryPair/SpawnSetup) only sets a flag; EnsureWorks runs from InPool/OnRope/RopeCellCount (:82-110), i.e. only when Scan meets a thing in a river lane (LaneAt :265) or a proof reads RopeCellCount; ApplyRope reads RopeIndicesNoRebuild (FerryAndLevee :221). The r9 ferry proof called RopeCellCount first, which masks it. Live: pair a ferry with the river empty, read RopeIndicesNoRebuild.Count and an undrafted path BEFORE any RopeCellCount read.
- **C6-F8** CONFIRMED LOW — Ferry posts pair with the NEAREST unpaired post whose line touches any water, even on the same bank. Rivers/RM_FerryAndLevee.cs:47-90 TryPair/LineCrossesWater; no opposite-bank test.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
