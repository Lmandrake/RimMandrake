## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.5)
Verdict: CONFIRMED MINOR. Thermostat HeatInterval uses FillAt; sheets <1 notch get no heat

### GPT finding (verbatim)
### FA_core_sim_2.5 — Thermostats ignore liquid shallower than one notch

- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/MapControls/RM_LiquidThermostat.cs:49–53` (`HeatInterval`)
- evidence:
  ```csharp
  int levels = ex.IsExcavated(c) ? ex.FillAt(c) : (ex.IsSourceCell(c) ? NaturalCellLevels : 0);
  if (levels <= 0)
  {
  ```
- failure scenario: A roofed bath contains a 0.3 m sheet and has an active thermostat targeting 40°C. Every excavated square reads zero levels, so the thermostat reports no liquid and supplies no heat. In contrast, `RM_LiquidHeat.Push` in this part explicitly supports fractional notches through `WaterDlAt`. Outside this part, opened the excavation adapter to verify `FillAt`.
- confidence: high
