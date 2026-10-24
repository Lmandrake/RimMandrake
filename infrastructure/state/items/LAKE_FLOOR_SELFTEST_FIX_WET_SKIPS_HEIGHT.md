## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_2.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_2.2)
Verdict: CONFIRMED MINOR. LakeFloorChecks.cs:85 boundary returns reachable on any wet cell before comparing heights; the ruler can call a sunken lake reachable

### GPT finding (verbatim)
### FE_cs_selftests_2.2 — Lake-access ruler accepts wet neighbours without checking the final height difference
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/LakeFloorChecks.cs:85,97 (`EdgeReachable`)
- evidence:
```csharp
                    if (Wet(s)) return true;                                  // the water touches the land
                    if (Wet(m)) return true;                                  // a dry floor square beside the water
```
- failure scenario: Give the helper a one-cell lake with floor depth 10 notches, surface `-9 * RM_LevelSolve.U`, and climb limit 1. The cell contains water, so the boundary branch immediately reports it reachable, although its surface is nine notches below land under this helper’s stated height model. Similarly, its BFS accepts a wet neighbour before checking the step into it. The drained-lake access proof can therefore miss an inaccessible final descent to water.
- confidence: high
