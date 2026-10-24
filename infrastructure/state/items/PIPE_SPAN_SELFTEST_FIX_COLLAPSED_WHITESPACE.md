## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_2.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_2.4)
Verdict: CONFIRMED MINOR. PipeSpanNetChecks.cs:183 searches for "\n\t\t}" in a Src string whose whitespace was collapsed (RiverSwitchFlipChecks.cs:44): always passes

### GPT finding (verbatim)
### FE_cs_selftests_2.4 — Pipe-span regression assertion searches for whitespace its helper has removed
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs:183 (`PipeSpan_P3_production_wiring_adapter_callback_join_order`)
- evidence:
```csharp
                Assert(!poles.Contains("SpansChangedCount++;\n\t\t}") , "the callback is no longer only a counter");
```
- failure scenario: `poles` comes from `RiverSwitchFlipChecks.Src`, which collapses all whitespace to spaces. Consequently, it cannot contain the searched newline/tab sequence, even when that exact retired callback is present in the original source. This assertion always passes. Other assertions in the case still provide protection; this particular regression guard provides none. I opened the outside-part helper, `Source/SelfTest/RiverSwitchFlipChecks.cs:44`, and reproduced the normalization mismatch.
- confidence: high
