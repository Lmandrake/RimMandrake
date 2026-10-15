# BOTTLE_STOCK_MEND_FREE_REFILLS

FlowWorks: bottle fill/wash from terrain never debit the body; containers heal on transition

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C2-F2** CONFIRMED HIGH — Filling a bottle/bucket/barrel from pond terrain never debits the body's stock. JobDriver_FillBottle / RM_LiquidBottleUtility.TryGetLiquidAt read terrain only; no RM_LiquidStock call anywhere in the bottle jobs (grep). Bottle then poured into a tank = liquid created from a limited pond.
- **C2-F3** CONFIRMED MEDIUM — Washing a container consumes no water. JobDriver_WashBottle has no debit; liquids_framework_design.md:161 says the wash job consumes water.
- **C2-F9** CONFIRMED LOW — Every container transition resets hit points (free repair). RM_LiquidBottleUtility.MakeContainer makes a fresh Thing and the original is destroyed; HitPoints not copied.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
