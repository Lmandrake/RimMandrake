## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.8)
Verdict: CONFIRMED MAJOR. Tar floodTerrain RM_Fill_Tar_Trace is non-temporary (Terrain.xml:383, no <temporary>) so open-ground path refuses it (Flood.cs:496-500) and cooling skips excavated cells (doc 523-531) -> RM_TarGlass edge never written

### GPT finding (verbatim)
### FA_core_sim_1.8 — The tar-to-glass flood path is unreachable with the current terrain ownership rules
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`:496–502, 554–557 (`PlaceFluid`, `CoolFrontToGlass`)
- evidence:
  ```csharp
  if (fluidDef.floodTerrain == null || !fluidDef.floodTerrain.temporary)
  ```
  ```csharp
  if (!RM_StockMath.MayCoolToGlass(IsFrontCell(c), excavation != null && excavation.IsExcavated(c)))
  ```
- failure scenario: Let a tar release exhaust its volume or frontier. Every successfully reached tar cell belongs to the excavation engine and is excluded from cooling. Tar cannot reach the alternative, non-engine placement path because its flood terrain is non-temporary. Thus the configured glass edge is never written. Outside this part, I opened `Defs/Canals/FluidDefs/FlowWorks_Fluids.xml`, `Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml`, and `Source/RM_StockMath.cs`, confirming the tar configuration and the unconditional exclusion of engine-owned cells.
- confidence: high
