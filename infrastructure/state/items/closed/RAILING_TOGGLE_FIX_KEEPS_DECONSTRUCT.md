## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.12). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Resolved in this drain round. Completion evidence follows the original report.

### original verification (FC_pits_superdeep_1.12)
Verdict: CONFIRMED MINOR. PlaceRailing 1207-1220 returns on RailedAt, never cancels Deconstruct designation

### GPT finding (verbatim)
### FC_pits_superdeep_1.12 — Switching railings back on does not cancel their deconstruction
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:1207-1213,1284-1287` (`PlaceRailing`, `RemoveRailing`)
- evidence:
  ```csharp
  if (rail == null || RailedAt(map, c))
  return;
  map.designationManager.AddDesignation(new Designation(rail, DesignationDefOf.Deconstruct));
  ```
- failure scenario: Switch railings off, then back on before a colonist dismantles them. The first action queues deconstruction. The second sees existing railings and returns without removing those designations. Colonists subsequently dismantle them while the bridge’s switch says “on.” Nothing automatically rebuilds them afterward.
- confidence: high

## criteria

- A1 L1: Production-method off/on regressions pass, reject the original defect and targeted mutants, retain unrelated designations and placement behavior, and have a passing relevant suite and matching shipping build with formatting equivalence established.
- A2 L2: Disposable all-DLC live off/on before work clears real railing Deconstruct marks while retaining identities and unrelated designations, with exact deployed DLL identity and restored scene/settings.

## completion

Published shipping repair 2c1d3f3879f7224b2946626da8a361dc0a7f8338, corrected live driver 16caafc7efcec461334253f8a70c8681736f74cf, readability-only follow-up 5e808f72c6b413b514b28be82258e4e79bc4bd82 and complete evidence 5eed07366f58f18c8fac045e597a3e7e9271bca0. Evidence resides in whittle/fw-drain-railing-toggle, including exact raw judgments and parent_acceptance_refreshed.json. The full relevant suite passed before formatting. C# tokens, project XML and Python AST match, and formatted actual-method/driver controls pass. Shipping compile inputs and DLL/stamp remain byte-identical to live.

Live attempt 1 failed in the proof reader before any toggle and restored successfully. Corrected attempt 2 passed with all four railing IDs/materials/HP retained and Plan/wall controls intact. Existing railings on raised or collapsed leaves also receive cancellation, covered offline. Game DOWN and process absent, bridge and host driver FREE. No GSS look change. Pawn scheduling, already-running/completed deconstruction, mid-off save/reload and full-list integration remain UNVERIFIED. An old stuck ON save needs an off/on cycle. Two disposable guarded begin snapshots remain for audit.
