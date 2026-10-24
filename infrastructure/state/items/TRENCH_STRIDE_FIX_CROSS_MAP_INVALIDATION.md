## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.7)
Verdict: CONFIRMED MINOR. RM_CliffMask.cs:55 FullDerives is a process-wide static; RM_TrenchStride.cs:401 compares it per map, so map A's derive rebuilds map B's masks

### GPT finding (verbatim)
### FC_pits_superdeep_2.7 — One map’s connectivity rebuild invalidates stride masks on other maps
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_TrenchStride.cs:401 (`AfterIncremental`)
- evidence:
  ```csharp
  if (m.seenFullDerives != RM_CliffMask.FullDerives || m.seenGeneration != (eng?.ClimbGeneration ?? 0))
  ```
- failure scenario: With the HugeThings stride hook registered and two active maps, digging on map A increments the process-wide `RM_CliffMask.FullDerives`. The next ordinary connectivity update on unchanged map B consequently rebuilds all its applicable stride masks. Repeated changes on another settlement therefore cause unnecessary whole-map, multi-band derivations. The invalidation counter needs map scope. The external HugeThings implementation was not opened; this finding concerns the supplied registered-hook branch.
- confidence: high
