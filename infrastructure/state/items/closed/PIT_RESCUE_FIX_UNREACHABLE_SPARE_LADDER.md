## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.3)
Verdict: CONFIRMED MINOR. RM_PitAccess.cs:257-268 SparePortable has no reachability check; an unreachable minified ladder is chosen over building one

### GPT finding (verbatim)
### FC_pits_superdeep_2.3 — An inaccessible stored ladder can permanently stall automatic pit rescue
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs:257–267 (`SparePortable`)
- evidence:
  ```csharp
  if (t is MinifiedThing m && m.InnerThing?.def == portable && m.Spawned && !m.IsForbidden(Faction.OfPlayer)
      && InstallBlueprintUtility.ExistingBlueprintFor(m) == null)
  ```
- failure scenario: A minified portable ladder lies in a sealed chamber, while accessible wood could supply a new rescue ladder. This search selects the inaccessible ladder without checking whether any installer can fetch it. `TryQueueFor` creates an install blueprint, which nobody can complete. Subsequent attempts see that pending blueprint and decline to build another ladder, leaving the trapped colonist without automatic assistance.
- confidence: high
