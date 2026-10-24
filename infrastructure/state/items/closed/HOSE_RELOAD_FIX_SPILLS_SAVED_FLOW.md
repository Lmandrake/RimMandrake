## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_1.5)
Verdict: CONFIRMED MAJOR. flowUntil is never scribed (CompHoseReel.cs:67) and drain check fires once per cycle when !Flowing (RM_MapComponent_Hoses.cs:611-614) -> after load a working hose spills its held liquid before the first transfer

### GPT finding (verbatim)
### FB_hose_gss_1.5 — Loading a flowing hose can spill its saved liquid before flow is restored
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs:67,224–225 (`flowUntil`, saved held contents); src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:611–614 (`MapComponentTick`)
- evidence:
  ```csharp
  && RimMandrake.FlowWorks.Machinery.RM_HoseHold.ShouldDrain(r.heldUnits, RM_HoseSettings.hoseHoldsLiquid, RimMandrake.FlowWorks.Machinery.RM_HoseLinks.Eligible(r),
      RimMandrake.FlowWorks.Machinery.RM_LiquidNetKernel.Flowing(r.flowUntil, now)))
      RimMandrake.FlowWorks.Machinery.RM_LiquidSpill.DrainHeld(r, map, RimMandrake.FlowWorks.Machinery.RM_LiquidSpill.DrainCell(r, map));
  ```
- failure scenario: Save with liquid held in a working hose, then load shortly before that reel’s staggered drain check and before the pump’s next transfer. Held contents survive, but `flowUntil` starts at `NoLease`; the drain check treats this initialization gap as stopped flow and spills the contents. An off-screen hose can also initially lack its runtime lay. Confirmed `ShouldDrain` drains on either `!live` or `!flowing` in `Source/Machinery/RM_LiquidNetKernel.cs:541`, and pumps wait for their staggered cycle in `Source/LiquidTypes/Building_LiquidPump.cs:94–105`; both outside this part and opened.
- confidence: high
