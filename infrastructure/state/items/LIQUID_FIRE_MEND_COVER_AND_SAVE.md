# LIQUID_FIRE_MEND_COVER_AND_SAVE

FlowWorks: liquid fire ignores covers/flyers; carried progress unsaved; blast-origin inheritance

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C4-F1** CONFIRMED LOW — Liquid fire: carried burn progress and burning-fluid identity are not saved. RM_LiquidFire.cs:55-58 carriedAcc/carriedTick/carriedFluid/burningFluid not in ExposeData (:90-107); after load TakeCarried treats a null fluid as matching any (:606).
- **C4-F7** CONFIRMED MEDIUM — Burning liquid sets pawns on an intact cover (and flyers) alight at the trapped 100% rate. RM_LiquidFire.ApplyEffects (RM_LiquidFire.cs:394-406) ignores cover and Flying; heldInPit = IsSuperdeepExcavation only.
- **C4-F9** CONFIRMED LOW — A later explosion at the same centre inherits an earlier liquid blast's source-hop limit (300 ticks). RM_LiquidFire.cs:548 keys blastHops by centre cell only.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
