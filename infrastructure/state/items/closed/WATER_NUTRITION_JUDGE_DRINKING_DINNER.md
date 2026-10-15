# WATER_NUTRITION_JUDGE_DRINKING_DINNER

FlowWorks: water containers give nutrition (toxic too) - owner question

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C9-F7** PLAUSIBLE LOW — Water bottles/buckets (incl. toxic and salt) give nutrition 0.05/0.25. Defs/LiquidTypes/ThingDefs/RM_LiquidBottles.xml Nutrition on every water container. Owner design question: should water feed a starving pawn? Live: starving pawn, only toxic water bottles, read food need.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
