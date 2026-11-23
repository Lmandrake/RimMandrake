## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.13). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.13)
Verdict: CONFIRMED MINOR. RM_PlacerWorks.cs:708-746 cleanup tracks new Thing ids only; ore merged into existing stack survives

### GPT finding (verbatim)
### FC_pits_superdeep_1.13 — The placer selfcheck leaves generated ore merged into existing stacks
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerWorks.cs:709,736-745` (`RM_PlacerProof.SelfCheck`)
- evidence:
  ```csharp
  HashSet<Thing> already = new HashSet<Thing>(map.listerThings.AllThings);
  if (!already.Contains(t) && t.def.category == ThingCategory.Item)
  t.Destroy();
  ```
- failure scenario: Run `selfcheck` where a sluice or the selected colonist is near an existing compatible ore stack. Production placement can merge the generated ore into that stack. Cleanup tracks only newly created Thing identities, so the added quantity survives in the pre-existing stack. Repeated checks alter the colony’s resources despite the helper’s stated cleanup behavior, contaminating later live-state measurements.
- confidence: high
