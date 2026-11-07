## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.9)
Verdict: CONFIRMED MINOR. RM_TakenByLand.Returned (return timestamps) is cleared in the world component ctor (RM_TakenByLand.cs:313) and never scribed; reload drops the returned-prisoner grace and notice

### GPT finding (verbatim)
### FA_core_sim_4.9 — Reloading removes the returned-prisoner grace period and escape notification
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/TakenByLand/RM_TakenByLand.cs`:313, 450–453; `src/RimMandrake/FlowWorks/Source/TakenByLand/RM_TakenByLandKernel.cs`:200–204 (`RM_WorldComponent_TakenByLand`, `RM_TakenReturnGuard`)
- evidence:
  ```csharp
  public RM_WorldComponent_TakenByLand(World world) : base(world) { RM_TakenByLand.Held.Clear(); RM_TakenByLand.Returned.Clear(); }
  private readonly Dictionary<int, int> returned = new Dictionary<int, int>();
  ```
- failure scenario: A prisoner returns while no secure prison exists, so the service uses its explicitly supported unsecured interior fallback and promises an hour to prepare a cell. Save and reload during that hour. Return timestamps are neither saved nor reconstructed, so the prisoner immediately becomes eligible for ordinary escape. The same missing timestamp also disables the “recently returned prisoner escaped” letter, allowing the loss to be silent.
- confidence: high
