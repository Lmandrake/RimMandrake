## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.6)
Verdict: CONFIRMED MINOR. RM_SuperdeepTrap.cs:784-786 absolute mode (pitRelativeClimbEnabled off) compares raw ExcavatedDepthAt, so a shove off a deck over the same excavation is 4->4, no descent

### GPT finding (verbatim)
### FC_pits_superdeep_2.6 — Absolute-mode descent detection misses falls from a deck over the same excavation
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:786 (`IsFallingArrival`)
- evidence:
  ```csharp
  return RM_PitTrapMath.IsPitDescent(eng.ExcavatedDepthAt(prev), eng.ExcavatedDepthAt(pos));
  ```
- failure scenario: With relative climbing disabled, a forced mover shoves a pawn from an intact surface deck into an adjacent uncovered square of the same superdeep excavation. For an arrival handled by this detector, both raw excavation depths are four, so no descent is recorded: the pawn receives neither fall damage nor the spike descent event. The origin should be evaluated at the deck’s walking height. I opened the outside-part `Source/RM_PitTrapMath.cs`, `Source/Pits/Building_SpanDeck.cs`, and `Source/Pits/Building_PitCover.cs` to confirm the descent predicate and deck semantics.
- confidence: high
