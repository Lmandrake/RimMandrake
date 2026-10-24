## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.6)
Verdict: CONFIRMED MINOR. RM_LiquidWorksScatter.xml:14 every ruin scatter MayRequire mandrake.rm.environmentalhazards, About.xml declares no such dependency, industrialWorksBuildAnywhere=false (RM_MachinerySettings.cs:42): FlowWorks without EH has no industrial works (pack ships EH, so standalone only)

### GPT finding (verbatim)
### FD_defs_xml_1.6 — Default industrial progression requires an undeclared extra mod
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Defs/Machinery/RM_LiquidWorksScatter.xml:14–16,40,66,91` (all four industrial ruin scatters)
- evidence:
  ```xml
  <GenStepDef MayRequire="mandrake.rm.environmentalhazards">
    <defName>RM_DesalPlant_RuinScatter</defName>
    <order>760</order>
  ```
- failure scenario: Start with FlowWorks, GSS, Harmony and all declared DLC dependencies, using default settings. No industrial ruins generate because every scatter requires Environmental Hazards. Industrial construction simultaneously requires those ruins, leaving desal plants, detox works, tar refineries and pumping stations unavailable through normal progression. `About.xml` does not declare this additional requirement. **Outside files opened:** `Patches/Machinery/RM_LiquidWorksScatter_Register.xml` also gates registration on that kit; `Source/Machinery/RM_MachinerySettings.cs:42` defaults build-anywhere to false; `Source/Machinery/RM_LiquidWorksRuins.cs:18–43` enforces the ruin requirement.
- confidence: high
