## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.1)
Verdict: CONFIRMED MAJOR. TryDebitTerrain debits only natural bodies; BodyAt returns null for dug cells (LiquidStock.cs:129) -> TryDebit true; bottle fill/wash/drink from canal water is free

### GPT finding (verbatim)
### FA_core_sim_1.1 — Filling containers from dug freshwater creates liquid without debiting the canal
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_LiquidBottleUtility.cs`:189–199 (`TryDebitTerrain`)
- evidence:
  ```csharp
  FluidDef fluid = ex.Stock.BodyAt(map, c, ex)?.fluid ?? ex.ActiveFluid;
  float stock = RM_ContainerMaterialMath.BodyStockFor(units, fluid != null ? fluid.volumePerTile : 1f, RM_PumpMath.TankUnitsPerLevel);
  return ex.Stock.TryDebit(map, c, stock, ex);
  ```
- failure scenario: Fill an isolated, dug freshwater cell until it displays `WaterShallow`, then repeatedly fill barrels from it. The terrain lookup recognizes freshwater, but payment goes exclusively through natural-body stock. A dug cell has no natural body, so that debit succeeds without removing any canal water. Containers can extract unlimited water; washing has the same payment defect. Outside this part, I opened `Source/RM_LiquidStock.cs` (`BodyAt`, `TryDebit`), `Source/RM_MapComponent_Excavation.cs` (`IsSourceCell`), and `Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml` to confirm the complete path.
- confidence: high
