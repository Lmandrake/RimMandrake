## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.5)
Verdict: CONFIRMED MAJOR. RM_LiquidDefRegistry.xml:93-108 Crude distill listed before Industrial desalinate; CompLiquidConverter.cs:115-133 StepFor returns first eligible; desal plants list both (RM_IndustrialLiquidWorks.xml:124-127,174-177), so the industrial recipe never runs

### GPT finding (verbatim)
### FD_defs_xml_1.5 — Conversion ordering makes the industrial efficiency recipes unreachable
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:93–108,242–257` (`RM_Liquid_SaltWater`, `RM_Liquid_ToxicWater`)
- evidence:
  ```xml
        <tier>Crude</tier>
        <process>distill</process>
        <product>RM_Liquid_FreshWater</product>
  ```
- failure scenario: Run either desal plant tier on salt water, or either detox works tier on toxic water. Each machine accepts both processes listed for its liquid, but chooses the earlier crude recipe. Salt water therefore yields 200 L from 400 L instead of the industrial 400 L from 600 L; toxic water consumes 600 L instead of 400 L per 200 L produced. The later industrial rows are never selected by these machines. **Outside file opened:** `Source/Machinery/CompLiquidConverter.cs:115–133` returns the first conversion whose tier is at or below the machine tier, rather than selecting the highest eligible tier.
- confidence: high
