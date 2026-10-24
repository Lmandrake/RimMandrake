## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.7)
Verdict: CONFIRMED MINOR. CordWorldAdapter.KindOf never returns MachineKind.Lamp (CordWorldAdapter.cs:209-215), so lamp plug point and no-slide rule (CordGraph.cs:153,652) are dead in live play

### GPT finding (verbatim)
### FB_hose_gss_2.7 — The live adapter never selects lamp-specific cord geometry
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/CordWorldAdapter.cs:209–214` (`KindOf`); `src/RimMandrake/GimmeSomeSlack/Source/Core/CordGraph.cs:153,652` (`Slides`, `PlugPoint`)
- evidence:
  ```csharp
  if (c is CompPowerBattery) return MachineKind.Battery;
  if (transmitter) return MachineKind.Transmitter;
  return MachineKind.Consumer;
  ```
- failure scenario: A standing lamp reaches the connector path as a consumer. `KindOf` never returns `MachineKind.Lamp`, so the live map never uses the lamp-specific plug point or the explicit exemption from sliding approaches. Standing lamps receive generic consumer routing instead. Tests constructing `MachineKind.Lamp` records directly can exercise branches that the production adapter cannot reach.
- confidence: high
