# PANNING_SPOT_VERIFY_EMPTY_RIVER

FlowWorks: panning offered after the placer pool is mined out

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C5-F7** PLAUSIBLE LOW — Panning keeps being offered after every placer rock is mined (stock > 0, pool empty). Quarry/RM_PlacerWorks.cs:487 ShouldSkip reads stock only; Draw returns null when the pool is empty (:106). Live: mine the pool, read stock/poolCount and whether jobs keep coming.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
