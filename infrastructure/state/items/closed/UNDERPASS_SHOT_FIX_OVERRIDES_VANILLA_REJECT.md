## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.1)
Verdict: CONFIRMED MAJOR. CanHitTargetFrom postfix replaces a false vanilla result with only the cliff test when both ends are floor-side (RM_SuspensionPatches.cs:752-768) -> a wall-blocked shot under a deck becomes legal

### GPT finding (verbatim)
### FC_pits_superdeep_1.1 — Underpass shooting can override vanilla shot rejection
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs:752-768` (`RM_Patch_SuspensionBandShots.Postfix`)
- evidence:
  ```csharp
  __result = !RM_RelativeRulesMath.ShotBlocked((x, z) => RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, new IntVec3(x, 0, z)),
      root.x, root.z, targ.Cell.x, targ.Cell.z, RM_SuperdeepShooting.CliffNotches);
  ```
- failure scenario: A shooter beneath a deck targets another pawn on the same pit floor, with a wall blocking the shot. When `CanHitTargetFrom` returns false, this branch replaces that result using only the cliff test. With no intervening cliff, the result becomes true despite the wall. `ProofShot` can report an impossible shot as legal, and combat AI can select it. The code does not distinguish a cliff rejection from vanilla or another mod’s rejection. Outside this part, opened `Source/RM_Patch_SuperdeepShooting.cs` to confirm that the cliff prefix can also skip vanilla’s original method.
- confidence: high
