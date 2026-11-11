## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_1.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Fixed in `0b4357b3d70a457d3d116bc6db2bcf42449f6bda`; the original finding below describes the pre-fix fixture.

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

## closure — 2026-11-11

Codex Whittle repaired the test fixture only. Recognized cA1/cB1 pipes now require exact near T reachability and far TV isolation; both real components must exist and attach T. The old-name fixture and an isolated complete-kernel tank-conduction mutant each fail exactly the two repaired assertions while the other 38 pass. Final fast proof: 40/40. Relevant authorized wrapper: PASS 1/1, 1240/1240 main cases, 456/456 hose assertions. Fresh independent Opus accepted all frozen bullets; actual Whittle validator returned 0 with done_problems empty.

Test identity: base `40f1b06c765e73e7f19b03e86cfe8c0bef3d817c` plus the exact one-file test patch published at `0b4357b3d70a457d3d116bc6db2bcf42449f6bda`. All 6,009 proof input hashes match through parent inspection; Windows staged inputs match. Raw proof, source identities, unchanged independent judgment, cache-refusal qualification and limits: `whittle/fw-drain-hose-isolation/PARENT_ACCEPTANCE.md` and its evidence directory.

L1 instrument repair only. Single-cell injected graph; live-map geometry, transport/gameplay and fresh visual approval remain UNVERIFIED. No shipping/GSS source or media change, bridge, game launch, deployment, ModsConfig or save write. No owner question needed.
