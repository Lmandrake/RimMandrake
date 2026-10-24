## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_3.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_3.6)
Verdict: CONFIRMED MINOR. CordMotion.Sway allocates a new list per visible lifted strand per frame plus CordRng.Hash params (RM_MapComponent_CordGraph.cs:693-695)

### GPT finding (verbatim)
### FB_hose_gss_3.6 — Default CPU sway still allocates per visible strand every frame
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:690–696` (`DrawMotion`, CPU sway)
- evidence:
  ```csharp
                      List<V2> sw = CordMotion.Sway(s.Pts, s.SwayW, gt, CordRng.Hash("sway", p.Key), 0.12 * GimmeSomeSlackSettings.swayAmplitude, wind);
  ```
- failure scenario: View many unroofed hanging wall-terminal tails with the shipping CPU sway setting. Every visible tail allocates a new output list and backing array every frame, including while paused. The hash call additionally creates its `params` array and formatted key strings. Unlike whipping, CPU sway has no animated-tail cap. Large installations therefore generate persistent garbage collection pressure despite the reusable buffers used by the neighbouring motion paths. Outside this part, opened `Source/Core/CordMotion.cs:98–110`, confirming that `Sway` allocates `new List<V2>(n)` on every invocation.
- confidence: high
