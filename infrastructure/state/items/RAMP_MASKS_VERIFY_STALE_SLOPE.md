# RAMP_MASKS_VERIFY_STALE_SLOPE

FlowWorks: ramp spawn/despawn and climb settings bump generation without a cell delta

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C3-F6** PLAUSIBLE HIGH — Building/removing a ramp (or changing climb settings) bumps the climb generation but pushes no cell delta, so masks stay stale. RM_Building_PitRamp.SpawnSetup/DeSpawn (Superdeep/RM_PitRamp.cs:25,32) only BumpClimbGeneration; the ladder had the identical bug and now calls Notify_CellDelta (RM_LadderUtility.cs:104-107 comment). Live: build a ramp on a sealed pit, read ProofMask + a colonist route before any other terrain change.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
