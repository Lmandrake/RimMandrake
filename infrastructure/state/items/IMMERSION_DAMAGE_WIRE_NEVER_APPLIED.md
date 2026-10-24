## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.10). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.10)
Verdict: CONFIRMED MINOR. damageOnImmersion is authored (RM_AcidWater.xml) but no consumer; LiquidCorrosion applies only damageOnContact (87-92); code comment admits TODO

### GPT finding (verbatim)
### FA_core_sim_1.10 — Authored immersion damage is never applied
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/LiquidTypes/LiquidCorrosion.cs`:87–91 (`DoCorrosionPass`)
- evidence:
  ```csharp
  LiquidDamageSpec spec = props.damageOnContact;
  ```
- failure scenario: Stage a pawn in `RM_AcidDeep`, whose terrain extension specifies 1 contact damage and 3 immersion damage. Every corrosion pass applies the contact specification; depth never selects the immersion specification. An immersion-only specification would do nothing. Outside this part, I opened `Defs/LiquidTypes/TerrainDefs/RM_AcidWater.xml` to confirm those authored values and searched the package’s C# references: `damageOnImmersion` has no damage-applying consumer.
- confidence: high
