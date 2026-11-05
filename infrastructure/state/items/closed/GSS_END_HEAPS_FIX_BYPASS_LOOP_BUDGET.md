## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_3.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_3.3)
Verdict: CONFIRMED MINOR. Long-run end heaps (CordLayer.cs:459-476) are placed without the target/over budget check the ordinary loops use (528)

### GPT finding (verbatim)
### FB_hose_gss_3.3 — Mandatory end heaps bypass the loop budget
- severity: MINOR
- where: `src/RimMandrake/_Shared/SlackGeometry/CordLayer.cs:459–486` (`AddLoops`, long-run branch)
- evidence:
  ```csharp
                      double r = 0.5 * prm.Cap / 1.6;
                          List<V2> c = Heap(Q[j], t, nrm, r, side, re);
                          if (AllClear(w, c, LayParams.RC + 0.02) && !c.Any(q => w.IsDoor(q.Floor)) && !Lassoes(w, c, own)) { shape = c; break; }
  ```
- failure scenario: Set the loop budget to two cells and lay a long cord across open ground. Once its pre-loop length exceeds 40 cells, this branch inserts two substantial heaps without checking `target` or remaining budget. The later settle cannot remove the excess through its rest-length clamp because that clamp preserves at least the already sprawled length. A numerical reproduction of this branch with a 45-cell straight input, target 47, default cap, and RNG seed 1 inserted approximately 31.9 cells of heap. This is heap expenditure itself, independently of the documented additional lateral wander.
- confidence: high
