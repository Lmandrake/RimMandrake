## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.7)
Verdict: CONFIRMED MINOR. Flood spreads one tile per TicksPerTile (Flood.cs:279-283); brimming pass-through cells cost a step but no volume (466-471) while expiry = 2*TicksPerTile*PayableTiles (102,117,211) -> release expires mid-channel, rest spilled/lost

### GPT finding (verbatim)
### FA_core_sim_1.7 — Flood expiry counts paid tiles but ignores traversal through full cells
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`:102–117, 468–471 (`FloodingTicks`, `ExpiryTick`, `PlaceFluid`)
- evidence:
  ```csharp
  private int FloodingTicks => TicksPerTile * Mathf.Max(1, estimatedFloodedTiles);
  private int ExpiryTick => spawnedTick + 2 * FloodingTicks;
  if (cellRoom <= 0 && same)
  ```
- failure scenario: Release one notch of water upstream of a long, already-brimming channel with empty capacity beyond it. Each full cell is reached without spending volume, but still consumes a spread interval. The release’s lifetime permits only about two intervals because its initial payable-tile estimate is one. It expires before traversing the channel, spilling or recording its water as lost despite a valid destination farther along. Outside this part, I opened `Source/RM_MapComponent_Excavation.cs` and confirmed `CanLiquidEnter` permits full excavated cells.
- confidence: high
