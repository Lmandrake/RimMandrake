## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_3.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_3.5)
Verdict: CONFIRMED MINOR. Colour seed union joins only laid-piece endpoints (RM_MapComponent_CordGraph.cs:180-188); a run joined through hidden/buried conduit gets two seeds

### GPT finding (verbatim)
### FB_hose_gss_3.5 — Hidden conduit connections split a single net’s legacy colour seed
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:179–187` (`ComputeNetSeeds`)
- evidence:
  ```csharp
                  string a = p.EndA != null ? Tok(p.EndA) : own;
                  Find(a);
                  if (p.EndB != null) Union(a, Tok(p.EndB));
  ```
- failure scenario: Load an unstyled colony, select Modern/Mixed defaults, and connect two exposed conduit runs through a buried wall run or hidden conduit. Seed computation joins only endpoints represented by laid pieces. The hidden connection produces no piece, leaving separate roots—and potentially separate colours—for parts of the same electrical net. `StyleProbe.cordNets` also counts these seed components as distinct nets. Outside this part, opened `Core/CordBuilder.cs` and `Core/CordGraph.cs`: production builds edges from `CordEdges()`, which explicitly excludes hidden edges.
- confidence: high
