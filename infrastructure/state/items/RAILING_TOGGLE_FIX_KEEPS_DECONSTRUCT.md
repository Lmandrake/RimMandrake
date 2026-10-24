## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.12). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.12)
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
