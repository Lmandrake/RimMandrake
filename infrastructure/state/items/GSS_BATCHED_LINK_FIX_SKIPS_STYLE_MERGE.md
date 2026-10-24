## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.1)
Verdict: CONFIRMED MINOR. Link() RunOf traverses spans not yet processed (RM_MapComponent_ConduitRuns.cs:272-276); with batched A-B and B-C both already strung, each check finds the other end through the other new span and returns 'already one run' -> mixed-style run never merged

### GPT finding (verbatim)
### FB_hose_gss_2.1 — Batched links can skip every required style merge
- severity: MAJOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_ConduitRuns.cs:275–276` (`Link`)
- evidence:
  ```csharp
  List<Thing> ra = RunOf(a, exclude, a, b);
  if (ra.Contains(b)) return;                                   // already one run
  ```
- failure scenario: A and C already belong to one Industrial conduit run; B belongs to a separate Modern run. Arrange the selected anchors so “Auto-link selected” adds A–B and B–C. Both spans exist before their queued checks execute. Checking A–B finds B through A’s existing conduit connection to C and the pending C–B span, so it returns. Checking B–C likewise returns through B–A–C. Neither check reconciles styles, leaving one connected run permanently mixed. `cstyles` can report one run ID containing both looks after `cprocess`.
- confidence: high
