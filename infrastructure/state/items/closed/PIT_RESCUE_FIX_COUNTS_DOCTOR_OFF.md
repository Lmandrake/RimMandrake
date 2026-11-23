## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.2)
Verdict: CONFIRMED MAJOR. RM_PitAccess.cs:164-167 WorkTypeIsDisabled is capability, not the work-tab setting; its own doc (155-159) says only colonists vanilla DoctorRescue would send must count

### GPT finding (verbatim)
### FC_pits_superdeep_2.2 — Rescue considers colonists with Doctor work switched off available rescuers
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs:165–167 (`AnyRescuerReaches`)
- evidence:
  ```csharp
  && !c.WorkTypeIsDisabled(WorkTypeDefOf.Doctor)
  && c.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation)
  && c.CanReach(downed, PathEndMode.ClosestTouch, Danger.Deadly))
  ```
- failure scenario: The only colonist equipped to reach a downed pawn in a ladderless pit has Doctor unchecked in the Work tab. Other colonists assigned to Doctor cannot climb into the pit. `WorkTypeIsDisabled` checks capability restrictions, not the player’s work assignment, so this colonist suppresses the rescue ladder indefinitely despite never taking the rescue job. I opened the installed Core `Defs/WorkGiverDefs/WorkGivers.xml`; `DoctorRescue` belongs to Doctor work.
- confidence: high
