## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.4)
Verdict: CONFIRMED MINOR. FlowWorks_Fluids.xml:128-145 RM_Fluid_SlimeWhite has no fireKind (only one fireKind in the file) while RM_Liquid_SlimeWhite is flammable; canal slime cannot burn

### GPT finding (verbatim)
### FD_defs_xml_1.4 — White slime’s canal form cannot ignite
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Defs/Canals/FluidDefs/FlowWorks_Fluids.xml:128–145` (`RM_Fluid_SlimeWhite`)
- evidence:
  ```xml
    <defName>RM_Fluid_SlimeWhite</defName>
    <label>white slime</label>
    <floodTerrain>RM_Fill_SlimeWhite_Trace</floodTerrain>
  ```
- failure scenario: Fill a trench with white slime and ignite it with fire or an explosion. It never enters the liquid-fire simulation: this fluid omits `fireKind`, although `RM_Liquid_SlimeWhite` declares it flammable and its fill terrains deliberately disable fire extinguishing. **Outside files opened:** `Source/FluidDef.cs:93` defaults `fireKind` to `None`; `Source/RM_LiquidFire.cs:199–217` rejects that value. `Source/LiquidTypes/LiquidIgnition.cs` requires a flammable terrain extension, which these canal fill definitions also lack. Searches of FlowWorks `Source/` and `Patches/` found no corrective assignment.
- confidence: high
