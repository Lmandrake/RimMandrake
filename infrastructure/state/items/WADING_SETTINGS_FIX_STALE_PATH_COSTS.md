## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.6)
Verdict: CONFIRMED MINOR. Path cost recalculated only on rep.TierChanged (RM_MapComponent_Sheet.cs:559-563); toggling pawnEffectsEnabled or wading-cost settings (RM_SheetSettings.cs:144) leaves stale path costs

### GPT finding (verbatim)
### FA_core_sim_4.6 — Changing overflow wading settings leaves cached movement costs unchanged
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:559–563; `src/RimMandrake/FlowWorks/Source/Sheet/RM_SheetSettings.cs`:144, 173–174 (`EnginePulse`, `DoSettingsSection`)
- evidence:
  ```csharp
  foreach (var (cell, _, _) in rep.TierChanged)
  map.pathing?.RecalculatePerceivedPathCostAt(c);   // Stage 2: the wading cost follows the tier
  ```
- failure scenario: Let a stable pool establish its movement cost, then disable pawn effects or change the wading-cost slider. Those controls change the value used by `PathCostAt`, but do not invalidate existing path-grid entries. A pool that stays in the same tier keeps its previous cached cost until an unrelated recalculation or tier change. Turning effects on has the corresponding missing-cost problem.
  
  The in-part `WriteSettings` reapplies river, thirst and swimming state, but contains no sheet-cost refresh.
- confidence: high
