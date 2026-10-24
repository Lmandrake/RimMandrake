## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.1)
Verdict: CONFIRMED MAJOR. ExactTouchSource treats LevelBodyOf -2 (disabled input) as limitless mouth; every other source path checks world.CanSupply (kernel 1186,1744,1904,2010); exact path does not

### GPT finding (verbatim)
### FA_core_sim_2.1 — Disabled natural liquids become limitless sources in the exact kernel

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs:782–786` (`ExactTouchSource`)
- evidence:
  ```csharp
  if (bid < 0)
  {
      exLimMouths.Add(cell);
  ```
- failure scenario: Disable a liquid in Mod Settings, then let an adjacent excavated channel resolve with exact levelling enabled. The adapter returns `-2` to exclude that source, but this branch treats it as limitless supply. The channel receives the disabled liquid without depleting the finite pond. Outside this part, opened `RM_MapComponent_Excavation.cs:2999–3007` confirms the `-2` sentinel; `CanClaim` checks palette availability, so it does not prevent this.
- confidence: high
