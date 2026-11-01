## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.8)
Verdict: CONFIRMED MINOR. RM_PitLipOcclusion.cs:133-152 new Vector3[]/Color32[]/int[] per shade call each frame (call site 408), pooling covers only Mesh objects

### GPT finding (verbatim)
### FC_pits_superdeep_2.8 — Pooled lip-shadow meshes still allocate their backing arrays every frame
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs:133–152 (`DrawEdgeShade`)
- evidence:
  ```csharp
  var verts = new Vector3[nv];
  var cols = new Color32[nv];
  bool any = false;
  ```
- failure scenario: Several visible pit occupants stand near shadow-casting walls. Every shaded cover piece allocates fresh vertex and colour arrays; pieces containing shade also allocate triangle arrays. These allocations recur every rendered frame despite pooling the `Mesh` objects. Occupied pits along walls can therefore create sustained garbage collection pressure and frame stutter; even pieces ultimately rejected by `!any` have already allocated two arrays.
- confidence: high
