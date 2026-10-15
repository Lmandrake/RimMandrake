# PLACEMENT_FAILURE_MEND_LOST_IN_POSTING

FlowWorks: TryPlaceThing failures after a debit (reaction, fill-from-tank, revert, dig find, weir catch)

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F13** CONFIRMED LOW — Reaction item products lost when placement fails. RM_LiquidReaction.Drop (Kits/RM_LiquidReaction.cs:223-232) ignores TryPlaceThing's result; converter has a pending ledger, reaction does not.
- **C2-F6** CONFIRMED LOW — Fill-from-tank and liquid revert ignore TryPlaceThing failure after the debit. JobDriver_FillBottleFromTank debits then places with result ignored; RM_CompLiquidRevert destroys then places. Rare (Near placement seldom fails).
- **C5-F12** CONFIRMED LOW — Dig find merged partly into an existing stack is not charged to the find budget. RM_DigDiscovery.cs:136-141 returns before 'budgetLeft -= cost' when TryPlaceThing returns false after a partial merge.
- **C6-F9** CONFIRMED LOW — Weir catch partly merged into a stack then 'failed' creates fish without debiting the fish stock. Rivers/RM_Weir.cs:361 Deposit returns 0 on TryPlaceThing false even after a partial merge; TryCatchFish skips Notify_Fished (:306-312).

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
