## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.2)
Verdict: CONFIRMED MINOR. Thirst source gate uses CanSupply(stock>=volumePerTile) (RM_ThirstUtility.cs:488, RM_LiquidStock.cs:500-502, RM_StockMath.cs:373) so a limited pond under one tile-volume is refused though a drink needs 1.5 L

### GPT finding (verbatim)
### FA_core_sim_3.2 — Terrain drinking rejects ponds containing less than 1,000 L
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstUtility.cs:488` (`TryFindDrinkCell`); `src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs:501–502` (`CanSupply`)
- evidence:
  ```csharp
  float unit = fluid != null ? fluid.volumePerTile : 1f;
  return RM_StockMath.CanSupply(body.limitless, body.stock, unit);
  ```
- failure scenario: A limited pond retains 500 L. The drinking search calls `CanSupply`, which requires one complete stock unit: one 1,000 L notch for shipped fluids. The pawn rejects the pond despite needing only 1.5 L, and can dehydrate beside usable water. Outside this part, I opened `LiquidTypes/RM_LiquidBottleUtility.cs` and `RM_ContainerMaterialMath.cs`: the eventual drink debit correctly requests only `15 / 10000` stock units, confirming the search/debit mismatch.
- confidence: high
