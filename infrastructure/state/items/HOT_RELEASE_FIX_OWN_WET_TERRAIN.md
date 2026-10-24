## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.4)
Verdict: CONFIRMED MINOR. IsFillOf uses OwnsFillTerrain which excludes freshwater-ladder rungs (FluidDef.cs:211-226); hot water never scalds/steams. Kit API has no in-repo caller (only human_review row), so latent

### GPT finding (verbatim)
### FA_core_sim_1.4 — Hot freshwater releases no longer recognize their own wet terrain
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_HotLiquid.cs`:54–56 (`IsFillOf`)
- evidence:
  ```csharp
  return t != null && fluid != null && fluid.OwnsFillTerrain(t);
  ```
- failure scenario: A script calls `RM_HotLiquid.Release` with `RM_Fluid_Water` beside an excavated channel. The flood fills the channel using the freshwater ladder, but both scalding and steam require `OwnsFillTerrain`, which excludes that ladder. A pawn standing in the released water receives no kit scald damage, and those cells produce no kit steam. `FluidDef.OwnsWetTerrain` already provides the broader ownership check. Outside this part, I opened `Defs/Canals/FluidDefs/FlowWorks_Fluids.xml` and confirmed freshwater-ladder staging is enabled.
- confidence: high
