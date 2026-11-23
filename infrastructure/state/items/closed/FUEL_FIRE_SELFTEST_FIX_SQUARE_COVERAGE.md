## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_1.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_1.2)
Verdict: CONFIRMED MINOR. FuelFireChecks.cs:93-99 coverage uses a Chebyshev square of spacing-1, not the Euclidean blast radius; a radius regression stays green

### GPT finding (verbatim)
### FE_cs_selftests_1.2 — Detonation coverage checks a square instead of the actual blast radius
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/FuelFireChecks.cs:90–99 (`CheckPlan`)
- evidence:
  ```csharp
  for (int dx = -(spacing - 1); dx <= spacing - 1 && !near; dx++)
      for (int dz = -(spacing - 1); dz <= spacing - 1 && !near; dz++)
          near = grid.Contains((x[k] + dx, z[k] + dz));
  ```
- failure scenario: The test reports that every cell lies under a blast whenever an anchor is within Chebyshev distance `spacing - 1`. Circular explosions require a Euclidean radius check. For the existing 30×30 fixture, spacing is 3; a radius regression to 2.4 would still satisfy the separate radius assertion and this square-coverage check, while cell `(29,29)` is approximately 2.828 cells from its nearest anchor and receives no blast. The coverage proof would remain green.
- confidence: high

Cross-file verification: opened `Source/RM_FuelFireMath.cs` to confirm anchor selection and `BlastRadiusFor`. Independently reproduced the fixture’s anchor geometry. The current default radius covers this fixture; the defect is the regression check’s false acceptance.
