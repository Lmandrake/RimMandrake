# BELT RiverWorks slice 2 — 2026-10-05

## Milestones
- start

## NEW ROWS NEEDED
- settings + IsWaterCell seam written
- weir/silt/drift/ferry/levee C# written; RiverCurrent pool+rope wiring
- TerminalBiomes rewired (dep on riverworks, arrester->RM_CompRiverArrester, 1x2 genstep spot, seams registered, sea silt patch); both DLLs build
- RiverWorks+TB build ok; selftests 182/184, 2 FlowWorks fails (checking)

## Landed (written by the FlowWorks builder; the slice-2 builder went silent after its commit)
- 456d00ca2 River Works slice 2 (weir 1x2 + slack pool, fish + biome drift catch, breach washes catch, stake-line levee, silt table, rope ferry; bank works moved out of TerminalBiomes, which now depends on River Works); bd25c2f21 art-ledger records for its 4 placeholder textures (the push guard had refused them).
- NEW ROWS NEEDED (River Works validation.py, live): static_call RM_RiverWorksProofWorks.ProofWeirPlace / ProofWeirPool (slack ~8 cells upstream) / ProofWeirCatch (fish + biome-relevant drift) / ProofBreach (catch washed downstream) / ProofSilt / ProofFerry / ProofLeveeFact (continuous stake-line holds a spring flood). settings: bankWorksEnabled, breachEnabled, stakeLineLevee, weirCatchesFish, weirCatchesDrift, breachWashesCatch, siltRichening, ferryEnabled.
