## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_1.8)
Verdict: CONFIRMED MINOR. Carried hose skips EnsureLay (RM_MapComponent_Hoses.cs:764) but its Cached mesh stays in meshes (dropped only on Deregister/new lay, 120,528); crossing-shadow loop (950) still reads its old rp

### GPT finding (verbatim)
### FB_hose_gss_1.8 — Cached former hose routes continue casting crossing shadows
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:763–767 (`DrawAll`),942–953 (`DrawCrossShadow`); src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs:356–360 (`HoseChanged`),723–738 (`ReelIn`)
- evidence:
  ```csharp
  if (r.carry == HoseCarryState.Carrying && r.trail.Count > 0) { DrawCarrying(r, y, lastFar); continue; }
  if (lay == null) { lastDraw[r] = "none"; continue; }
  if (o == r || !meshes.TryGetValue(o, out Cached oc) || oc.rp == null || RankOf(o) >= rank) continue;
  ```
- failure scenario: Pick up an older hose that crosses beneath a newer hose, then carry its end until that crossing disappears. Its old laid mesh remains in `meshes`; other hoses still use that route to generate crossing shadows because the lookup does not require the lower hose to remain laid or currently drawn there. Instant or automatic reel-in can leave the same phantom shadow. It clears when a subsequent lay drops the old cache.
- confidence: high
