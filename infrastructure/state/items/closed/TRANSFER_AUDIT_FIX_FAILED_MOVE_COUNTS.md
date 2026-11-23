## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_4.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_4.2)
Verdict: CONFIRMED MINOR. TransferChecks.cs:551 `==\s*\w` also matches `== 0` (nothing committed), so the lint accepts a credit inside a failed-Move branch (latent: no such site today)

### GPT finding (verbatim)
### FE_cs_selftests_4.2 — Transfer audit accepts failed transfers as committed transfers
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/SelfTest/TransferChecks.cs:542–551` (`CommittedBlocks`)
- evidence:
  ```csharp
  if (!Regex.IsMatch(cond, @"\)\s*(==\s*\w|>\s*0)")) continue;   // != (a refusal branch) is not a committed block
  ```
- failure scenario: An audited credit call is placed inside `if (RM_LiquidTransfer.Move(...) == 0)`. Zero means nothing committed, but `\w` matches `0`, so the audit recognizes the failure branch as a committed block. Keeping the existing credit call and tag preserves both coverage counts. `Lint` therefore permits precisely the uncommitted hose credit it is intended to reject. The supplied negative controls test credits outside blocks, not this case. I confirmed that the exact .NET regular expression accepts the zero-result condition.
- confidence: high
