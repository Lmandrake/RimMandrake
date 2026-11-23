## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_2.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_2.5)
Verdict: CONFIRMED MINOR. LevelSetChecks.cs:37-41 settled is the last changed pulse; a move/idle oscillation returns 299 of 300, not -1, and callers accept any >=0

### GPT finding (verbatim)
### FE_cs_selftests_2.5 — Integer-water tests accept a single idle final pulse as settling
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/LevelSetChecks.cs:38–41,92 (`Run`, `LowVolumeWideBasinOnePatch`)
- evidence:
```csharp
				if (now != prev) settled = p;
				prev = now;
			}
```
- failure scenario: A regression alternates between two conserved, contiguous depth-1 patches, moving on odd pulses and idling on even pulses. After 300 pulses, `Run` returns 299, and the low-volume case accepts `restA >= 0`; its total, maximum depth and connectivity assertions also pass. The test reports settling despite continuing oscillation. The same weakness affects other cases that only require a nonnegative returned settling pulse.
- confidence: high
