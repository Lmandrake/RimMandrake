## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_1.7)
Verdict: CONFIRMED MINOR. MateTail is called with blocked=null (RM_MapComponent_Hoses.cs:1328-1329; HoseSpliceMath.cs:436) so the splice join is drawn through walls; render only

### GPT finding (verbatim)
### FB_hose_gss_1.7 — Automatic splice shaping bypasses obstacle and hose-length validation
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Hose/HoseSpliceMath.cs:435–436,595–609,651 (`MateTail`, `MatePair`, `Clear`); src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:1289–1296 (`RefreshMates`)
- evidence:
  ```csharp
  List<V2> a = MateTail(A, C, u, straight, kmax, null, null, out Seed sa, width);
  List<V2> b = MateTail(B, C, -u, straight, kmax, a, null, out Seed sb, width);
  if (blocked != null && blocked(P[i])) return false;
  ```
- failure scenario: Two open ends lie diagonally adjacent across a corner pinched by two wall cells. Each hose’s original route is valid, but `RefreshMates` considers the ends close enough to join, and the splice solver receives no world obstacle predicate or band restrictions. It can draw the join through the forbidden gap. Likewise, moving the second end onto the first end’s coupling point can extend a nearly full-length hose beyond its reel’s capacity; the splice API has no maximum-length input. These changes are draw-only, so the census’s wall and length measurements of the original `HoseLay` can remain clean.
- confidence: high
