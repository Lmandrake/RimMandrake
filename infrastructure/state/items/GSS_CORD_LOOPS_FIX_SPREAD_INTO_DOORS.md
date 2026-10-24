## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_3.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_3.4)
Verdict: CONFIRMED MINOR. Ordinary loop/heap candidates are accepted by AllClear+over+Lassoes (CordLayer.cs:527-529) with no door check; NearDoor guards only end heaps (471)

### GPT finding (verbatim)
### FB_hose_gss_3.4 — Ordinary loops and heaps can spread into doorways
- severity: MINOR
- where: `src/RimMandrake/_Shared/SlackGeometry/CordLayer.cs:527–529` (`AddLoops`, ordinary-shape branch)
- evidence:
  ```csharp
                      List<V2> c = cand.Key ? Heap(Q[j], t, nrm, r, side, rr) : fig8 ? Figure8(Q[j], t, nrm, r, side) : Loop(Q[j], t, nrm, r, side);
                      bool over = s[s.Length - 1] + Geo.Length(c) > target * 1.25;
                      if (AllClear(w, c, LayParams.RC + 0.02) && !over && !Lassoes(w, c, own)) { shape = c; break; }
  ```
- failure scenario: A cord passes beside a doorway without originally crossing its door cell. A loop rooted on the adjacent floor can extend sideways into that doorway. Door cells remain walkable, so `AllClear` accepts them; the root’s pin/ramp test cannot detect doors reached only by the added shape. Unlike the end-heap branch, this branch never rejects `w.IsDoor` points. The player sees loops or heaps in a doorway despite the stated doorway exclusion.
- confidence: high
