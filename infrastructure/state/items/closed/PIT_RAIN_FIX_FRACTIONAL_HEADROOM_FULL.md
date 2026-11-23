## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.7)
Verdict: CONFIRMED MINOR. Rain uses whole-notch RoomNotches (RM_MapComponent_Excavation.cs:1348-1352, 3139-3145); a part-filled cell with <1 notch headroom sends all rain to surface overflow

### GPT finding (verbatim)
### FC_pits_superdeep_1.7 — Rain treats fractional headroom as a brim-full excavation
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs:1348-1352,3139-3147` (`RoomNotches`, `ApplyRain`)
- evidence:
  ```csharp
  return room <= 0 ? 0 : (int)(room / RM_LevelSolve.U);
  int room = RoomNotches(i);
  Sheet.RM_MapComponent_Sheet.RainOverflow(map, c, levels, fluid);
  ```
- failure scenario: A shallow, one-notch excavation contains only a thin fractional sheet of water. Its remaining capacity is less than one whole notch, so `RoomNotches` returns zero. Every accumulated notch of rain is sent to surface overflow instead of filling the available headroom first. With sheet overflow disabled or refused, that rain contributes nothing to the excavation. This affects ordinary exact-level water states, not just malformed saves.
- confidence: high
