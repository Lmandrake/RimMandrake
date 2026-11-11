## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Current source contains cache invalidation for carried, unlaid and retracting hoses. Independent verification and closure remain owed.

### verification (FB_hose_gss_1.8)
Current source inspection (2026-11-11): production DrawAll drops cached meshes before drawing a carried trail, on a null lay and before drawing a retracting hose. These changes postdate the original finding below. Verify DropMeshes also invalidates the crossing index and existing regression coverage before deciding closure; rendered live behavior is not newly claimed.

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
