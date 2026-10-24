## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.2)
Verdict: CONFIRMED MAJOR. Drill room = depth-FillAt ignores partGrid; TrySetDriverFill to brim zeroes partGrid (Excavation.cs:3454-3457) -> spent units > water added, unlogged loss

### GPT finding (verbatim)
### FA_core_sim_1.2 — A drill silently loses liquid when filling a fractional outlet to the brim
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Drilling/Building_LiquidDrill.cs`:172–210 (`TickRare`)
- evidence:
  ```csharp
  if (excavation.TrySetDriverFill(outlet, fill + levels, canalFluid))
  {
      pendingUnits -= levels * unitPerLevel;
  ```
- failure scenario: A one-notch outlet already contains 5,000 dL. `FillAt` reports zero whole notches, so the drill considers it to have one notch of room. It spends one pending unit, worth 10,000 dL, and sets the outlet to its 10,000 dL brim. Only 5,000 dL was added; the other 5,000 dL disappears without a loss entry. Outside this part, I opened `Source/RM_MapComponent_Excavation.cs`: `FillAt` excludes fractional water, and `TrySetDriverFillOutcome` clears the fractional remainder at the brim.
- confidence: high
