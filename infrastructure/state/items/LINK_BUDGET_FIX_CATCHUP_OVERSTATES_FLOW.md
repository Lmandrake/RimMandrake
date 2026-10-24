## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.10). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.10)
Verdict: CONFIRMED MINOR. n=65,maxLinks=64 -> every=2 -> each visited link gets 2x rate; aggregate ~2x

### GPT finding (verbatim)
### FA_core_sim_2.10 — Link-budget catch-up overstates passive flow rates

- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/RM_LevellingMath.cs:144–146` (`Plan`)
- evidence:
  ```csharp
  int visit = Math.Min(n, maxLinks);
  int every = (n + visit - 1) / visit;
  long rate = ratePerLink * Math.Min(every, MaxCatchUp);
  ```
- failure scenario: With 65 rate-limited links and a budget of 64, every visited link receives twice its configured allowance, although links are visited on 64 of every 65 cycles. Sufficiently large source/receiver gaps therefore permit 128 link-rate units per cycle instead of approximately 65. Adding the 65th link almost doubles aggregate throughput. Outside this part, opened `Machinery/RM_Levelling.cs:35,167–168`, confirming the production budget is 64.
- confidence: high
