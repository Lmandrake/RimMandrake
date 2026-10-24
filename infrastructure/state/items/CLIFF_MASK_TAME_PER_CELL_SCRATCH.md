## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.9)
Verdict: CONFIRMED MINOR. RM_CliffMask.cs:264-291 new int[9] plus a closure per band per cell in full derives

### GPT finding (verbatim)
### FC_pits_superdeep_2.9 — Full cliff-mask rebuilds allocate scratch state separately for every affected cell
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_CliffMask.cs:264–291 (`DeriveCell`)
- evidence:
  ```csharp
  var d9 = new int[9];
  ```
- failure scenario: A large excavation changes climb generation while pawns request paths. Each full derivation visits the excavation and its neighbours, allocating a new nine-element array and capturing structural-join callback state for every affected cell. A large basin therefore produces tens of thousands of temporary allocations per rebuild, repeated for the floor view when applicable. The supplied stride implementation already demonstrates reusable `CellProbe` scratch state, but the ordinary masks retain this allocation-heavy path.
- confidence: high
