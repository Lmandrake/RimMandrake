## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.7)
Verdict: CONFIRMED MINOR. RM_LiquidDefRegistry.xml:378-386 tar refine has product AND productThing; CompLiquidConverter.cs:239-241 uses tank room whenever product!=null, so the can fallback the descriptions (RM_IndustrialLiquidWorks.xml:325,348,396) promise never runs

### GPT finding (verbatim)
### FD_defs_xml_1.7 — Tar refineries advertise an item-output fallback that cannot run
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:378–385`; `src/RimMandrake/FlowWorks/Defs/Machinery/RM_IndustrialLiquidWorks.xml:348,396` (`RM_Liquid_Tar`, both working refineries)
- evidence:
  ```xml
        <inputLitres>800</inputLitres>
        <outputLitres>200</outputLitres>
        <productThing>Chemfuel</productThing>
  ```
- failure scenario: Connect a refinery to tar input without an available chemfuel output tank. Its description promises cans stacked beside the machine, but it stops for lack of output storage. The configured `productThing` is unreachable because the same conversion also specifies a liquid `product`. **Outside file opened:** `Source/Machinery/CompLiquidConverter.cs:239–242,274–286` always uses tank output when `product` is non-null; item output is available only when it is null.
- confidence: high
