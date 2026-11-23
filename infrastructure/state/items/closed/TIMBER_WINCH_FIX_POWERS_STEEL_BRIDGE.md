## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.2)
Verdict: CONFIRMED MINOR. Winch links by adjacency only (RM_Drawbridges.cs:699-703), no tier match; a timber winch reports Powered with no power comp (RM_DrawbridgeControl.cs:44-45) -> steel leaf moves unpowered

### GPT finding (verbatim)
### FC_pits_superdeep_1.2 — A timber winch powers a steel drawbridge without electricity
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs:700-703` (`LinkWinch`), `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeControl.cs:45` (`Building_DrawbridgeWinch.Powered`)
- evidence:
  ```csharp
  if (w.Position.AdjacentToCardinal(r.Cell(lane, HingeIndex(l))))
  l.winch = w;
  return c == null ? !RM_DrawbridgeMath.IsPowered(Tier) : c.PowerOn;
  ```
- failure scenario: Build a timber winch beside a steel drawbridge’s hinge. Linking checks adjacency but never checks `w.Tier == r.tier`. The timber winch reports `Powered == true` without a power comp, while movement uses the bridge record’s steel tier. After the lever order, the steel leaf moves automatically without electricity. Outside this part, opened `Defs/Pits/ThingDefs/RM_Drawbridge.xml`; the winch defs have no placement restriction preventing this pairing.
- confidence: high
