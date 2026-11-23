## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.5)
Verdict: CONFIRMED MINOR. RM_PocketGrid.cs:822 Trapped takes a one-hop UsableLadderIn; a ladder into another sealed pocket reads as escape

### GPT finding (verbatim)
### FC_pits_superdeep_2.5 — A ladder into another sealed pocket is mistaken for an escape
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_PocketGrid.cs:822–823 (`TrappedIn`)
- evidence:
  ```csharp
  return RM_PocketGridMath.Trapped(ComponentIsPocket(k, component), UsableLadderIn(k, component, p),
      WideEverywhere(k, component, RM_SuperdeepTrap.RequiredWidth(p)));
  ```
- failure scenario: A deep inner pocket has a usable ladder onto a shallower shelf, but the shelf is itself enclosed by an unclimbable outer wall. On an ordinary inner-floor cell, the pawn is held, yet `TrappedIn` returns false merely because a ladder crosses the first component boundary. It never checks whether the ladder graph reaches an escapable component. Consequently, an upright stranded colonist does not trigger `TryQueueFor`’s rescue assistance. Outside this part, I opened `Source/RM_PocketGridMath.cs` and confirmed that `Trapped` only tests the supplied one-hop boolean.
- confidence: high
