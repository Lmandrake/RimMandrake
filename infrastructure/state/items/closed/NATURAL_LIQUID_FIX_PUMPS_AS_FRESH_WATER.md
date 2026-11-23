## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.2)
Verdict: CONFIRMED MAJOR. RM_LiquidDefRegistry.xml:215 ToxicWater has terrainSuite but no canalFluid; RM_FluidIdentity.cs:27 skips it and RM_LiquidStock.cs:143,232 default to RM_Fluid_Water, so a pump on a toxic pond yields fresh water

### GPT finding (verbatim)
### FD_defs_xml_1.2 — Natural liquids without canal forms silently turn into fresh water
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:215–258` (`RM_Liquid_ToxicWater`; also salt water, brine, acid and coloured waters)
- evidence:
  ```xml
      <shallow>RM_WaterPoisonedShallow</shallow>
      <deep>RM_WaterPoisonedDeep</deep>
    </terrainSuite>
  ```
- failure scenario: Place a pump beside a poisoned pond, or dig a channel from it. This registry row has no `canalFluid`, so the natural body is assigned `RM_Fluid_Water`; pumping it produces fresh water, and its canal discharge loses the original liquid identity. Salt water and brine similarly bypass desalination. **Outside files opened:** `Source/RM_FluidIdentity.cs:25–30` skips rows without `canalFluid`; `Source/RM_LiquidStock.cs:143,232` substitutes `RM_Fluid_Water`; `Source/LiquidTypes/Building_LiquidPump.cs:171–174,267–271` draws using that fluid and maps it back to the freshwater row.
- confidence: high
