# LIQUID_THEFT_VERIFY_FALSE_ACCUSATION

FlowWorks: theft detector charges for any foreign tank change

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F14** PLAUSIBLE LOW — Theft detector: any stock change on a foreign tank counts as player theft. RM_LiquidTheft.TheftTick compares snapshots only (Machinery/RM_LiquidTheft.cs ~40); a foreign tank changed by corrosion/heat/its owners also charges goodwill; balanced take+put between cycles escapes. Live: foreign tank with no player link, change its stock via static_call, read caught/charges.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
