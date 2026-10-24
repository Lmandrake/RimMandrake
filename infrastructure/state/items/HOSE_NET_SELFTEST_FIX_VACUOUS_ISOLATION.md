## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_1.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_1.1)
Verdict: CONFIRMED MINOR. HoseNetChecks.cs:31-35 RoleOf makes Pipe only of names starting "c"; the g3 fixture (165-169) uses a1/b1 (role None), so the isolation check passes vacuously

### GPT finding (verbatim)
### FE_cs_selftests_1.1 — The two-pipe-runs isolation test constructs no recognized pipes
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/HoseNetChecks.cs:165–169 (`TankEndpoints`)
- evidence:
  ```csharp
  G.Add(g3.PipeOf, "P1", "a1");
  G.Add(g3.PT, "a1", "T");
  G.Add(g3.PT, "b1", "T");
  ```
- failure scenario: `G.RoleOf` recognizes pipe vertices only when their names start with `"c"`. Both `"a1"` and `"b1"` therefore have role `None`. The pump reaches neither run, so asserting that it cannot reach `"TV"` passes on an empty result—even if tank conduction is broken. This regression check cannot detect the cross-network merge it claims to test. Rename the vertices to recognized pipe names and assert that the near tank is actually reached before checking isolation.
- confidence: high

Cross-file verification: opened `Source/Machinery/RM_LiquidNetKernel.cs`. `Seeds` explicitly filters origin pipe cells through `g.RoleOf(c) == RM_NetRole.Pipe`.
