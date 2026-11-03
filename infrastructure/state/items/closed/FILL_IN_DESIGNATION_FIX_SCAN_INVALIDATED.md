## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.1)
Verdict: CONFIRMED MAJOR. PotentialWorkCellsGlobal yields lazily over SpawnedDesignationsOfDef while HasJobOnCell calls des.Delete() (WorkGiver_FillInCanal.cs:22-48) -> collection modified during JobGiver_Work scan; DigCanal copies the list

### GPT finding (verbatim)
### FA_core_sim_3.1 — Deleting stale fill-in designations invalidates the active work scan
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/WorkGiver_FillInCanal.cs:20–24,48` (`PotentialWorkCellsGlobal`, `HasJobOnCell`)
- evidence:
  ```csharp
  foreach (Designation item in pawn.Map.designationManager.SpawnedDesignationsOfDef(RimMandrakeFlowWorks_DefOf.RM_FillInCanal))
  {
      yield return item.target.Cell;
  ```
- failure scenario: A fill-in designation becomes stale—for example, a building is constructed over the designated cell. During the work scan, `HasJobOnCell` deletes it. Resuming the lazy enumeration then encounters the modified designation collection and throws, interrupting work selection. The supplied `WorkGiver_DigCanal` explicitly documents this engine interaction and already avoids it by returning a copied list.
- confidence: high
