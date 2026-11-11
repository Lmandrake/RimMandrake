## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_1.2)
Verdict: CONFIRMED MAJOR. EndSideOn/ReelSideOn measure from pump.Position as if 1x1 (HosePorts.cs:146-160) but RM_PumpingStation* are 3x2 Building_LiquidPump (RM_PumpingStation.xml:36-40) -> most edge cells refused

### GPT finding (verbatim)
### FB_hose_gss_1.2 — Pump port arbitration assumes every pumping station occupies one cell
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs:145–170 (`ReelSideOn`, `EndSideOn`, `PumpSideTakes`)
- evidence:
  ```csharp
  IntVec3 n = pump.Position + new Rot4(s).FacingCell;
  return RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.SideOf(end.x - pump.Position.x, end.z - pump.Position.z);
  if (map == null || side < 0) return false;
  ```
- failure scenario: Put a hose end against the east edge of a 3×2 kludged or repaired pumping station. The end is two cells east of `pump.Position`, so `SideOf` returns `-1`; the visible edge connection is refused. Reel-body connections suffer the same origin-based assumption. Targeting the station can consequently select a distant surviving approach or report no available port despite clear sides. Confirmed the 3×2 `Building_LiquidPump` definition in `Defs/Machinery/RM_PumpingStation.xml:38–43` and unit-offset-only `RM_PumpPortMath.SideOf` outside this part; both opened.
- confidence: high
