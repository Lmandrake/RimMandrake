## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.8)
Verdict: CONFIRMED MINOR. GenPlace Near placement (RM_Weir.cs:385) is unbounded while HeldCatch counts only within HeldCatchRadius 2.5 (123) -> cap and breach wash miss displaced stacks

### GPT finding (verbatim)
### FA_core_sim_4.8 — Catch placement can escape the radius used to enforce the catch cap
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs`:123, 385–391, 407 (`CaptureFloating`, `HeldCatch`)
- evidence:
  ```csharp
  private const float HeldCatchRadius = 2.5f;
  if (GenPlace.TryPlaceThing(t, head.BankCell, map, ThingPlaceMode.Near, null, dry))
  foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, HeldCatchRadius, true))
  ```
- failure scenario: Occupied or unsuitable nearby bank squares force a captured stack’s `Near` placement beyond 2.5 cells from the head. Placement succeeds, but subsequent `HeldCatch` calls omit that stack. Further captures can exceed the advertised held-item cap, and a later breach omits the displaced catch from its wash.
- confidence: high
