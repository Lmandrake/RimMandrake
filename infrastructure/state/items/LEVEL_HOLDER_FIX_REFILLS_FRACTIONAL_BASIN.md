## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.3)
Verdict: CONFIRMED MAJOR. LevelHolder.Measure sums FillAt (whole notches) so part-notch sheets read 0 held -> holder over-pours/drains

### GPT finding (verbatim)
### FA_core_sim_2.3 — A level holder repeatedly fills an already satisfied fractional basin

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/MapControls/RM_LevelHolder.cs:96–118` (`Measure`, `HoldChannel`)
- evidence:
  ```csharp
  held += ex.FillAt(c);
  ```
- failure scenario: Put five connected depth-one squares in the holder’s reach, select 50%, and set its rate to three levels per pulse. Three levels spread across those squares produce a 60% sheet, but `Measure` reads zero held levels. The holder fills the basin to its brim, subsequently drains it back to three levels, and repeats. It creates continuing external input and output instead of holding its setpoint. Outside this part, opened `RM_MapComponent_Excavation.cs` confirms the whole-notch `FillAt` and spreading `TryPourLevel` behavior.
- confidence: high
