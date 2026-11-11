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

## Completed 2026-11-11 — CODEX_ARCHMAGI_FWDRAIN

Existing production repairs are verified at artifact 0d1a449a52a6c71c6e65227824617c86982e5ad6, evidence `whittle/fw-drain-hose-shadow/`. Historical fixes 32ca2009d7, f3e8255a14, 32bb6a4c78 and 8ef7d5275a are published ancestors. No shipping source, DLL/stamp or art changed in this verification unit.

The offline harness executes seven exact whole production methods with the real crossing index and explicit renderer/lay/clock/Verse doubles. Three transitions in both draw orders remove the old cached route; active lower crossings survive. Rank/re-lay, idempotent drop, budget draining and legacy comparison controls pass. Eight original-behavior/mutant controls compile and fail behaviorally, then the external stage restores byte-exact. Actual standard FlowWorks runner PASS1/1 with1287/1287 main cases,188/188 hose checks,457/457 hose assertions and HoseFuzz4/4; all nonpass categories zero.

Fresh independent Opus broaden/judge and actual Codex Whittle/full validator accepted. Parent independently rehashed6034 inputs,349 shipping inputs,264 stage compile inputs and exact7 method bodies, then decoded111623 stdout/zero stderr bytes from the complete observer. Cache-admission refusal is preserved despite matching source hashes.

L1 mechanism acceptance only: live pixels, Unity mesh lifecycle, real jobs/saves and empty carried trail remain unverified. Upper-first ordering and frame budgets can temporarily retain an old shadow until a later scan; retracting hoses cast no crossing shadow on their remaining visible strand. LegacyFrame deliberately preserves the original comparison behavior. These are recorded limits, not a new L2 claim.
