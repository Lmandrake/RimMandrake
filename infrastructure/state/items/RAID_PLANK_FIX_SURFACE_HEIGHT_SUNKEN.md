## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.9)
Verdict: CONFIRMED MAJOR. RaidPlankFits accepts equal banks at any depth (RM_DrawbridgeMath.cs:342-360) but the raid plank record never sets deckNotches (RM_DrawbridgeRaid.cs:295-303) -> plank between sunken banks registered at surface height

### GPT finding (verbatim)
### FC_pits_superdeep_1.9 — Raid planks laid between sunken banks are registered at surface height
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeRaid.cs:294-303` (`RM_RaidPlanks.TryLay`)
- evidence:
  ```csharp
  tier = SuspensionTier.Timber,
  origin = lip,
  raidPlank = true,
  ```
- failure scenario: Use a crossing whose two dry banks are both four notches down and whose intervening cells are deeper. `RaidPlankFits` accepts equal-height banks at any depth, but the new record never sets `deckNotches`, leaving it zero. The laid plank becomes a surface deck instead of connecting the ledges, producing incorrect access, draw height, underpass classification, and fall distance. This is directly reachable through `ProofGivePlank`. Outside this part, opened `Source/Superdeep/RM_RaiderTrench.cs` to confirm the production plank-job call.
- confidence: high
