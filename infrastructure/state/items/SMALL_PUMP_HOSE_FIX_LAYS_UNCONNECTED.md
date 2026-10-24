## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_1.1)
Verdict: CONFIRMED MAJOR. RM_LiquidPump is 1x1 PassThroughOnly (RM_LiquidPump.xml:25,28) so ApproachIfOnPort returns early on Walkable (CompHoseReel.cs:415); end laid on the pump cell gives SideOf(0,0)=-1 (HosePorts.cs:158-160) -> no coupling

### GPT finding (verbatim)
### FB_hose_gss_1.1 — Clicking a small pump lays the hose on the pump without connecting it
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs:412–415 (`ApproachIfOnPort`); src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs:132–140,158–160 (`FindAt`, `EndSideOn`)
- evidence:
  ```csharp
  if (map == null || !target.InBounds(map) || target.Walkable(map)) return null;
  return RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.SideOf(end.x - pump.Position.x, end.z - pump.Position.z);
  ```
- failure scenario: The player targets an isolated `RM_LiquidPump` with Deploy or Move. Its cell is walkable, so target resolution does not redirect the end beside the pump. Once laid on the pump’s cell, the offset passed to `SideOf` is `(0,0)`, which rejects the coupling. The order succeeds, but the hose remains hydraulically disconnected. Confirmed the pump’s `PassThroughOnly` definition in `Defs/LiquidTypes/ThingDefs/RM_LiquidPump.xml:28` and the rejection in `Source/Machinery/RM_PumpPortMath.cs:15–21`—both outside this part and opened.
- confidence: high
