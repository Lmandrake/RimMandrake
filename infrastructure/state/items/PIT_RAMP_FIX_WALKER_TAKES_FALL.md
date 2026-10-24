## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.1)
Verdict: CONFIRMED MAJOR. RM_SuperdeepTrap.cs:782-800 IsFallingArrival judges by NaturalClimbLimitOf with no ramp exemption; ramps join up to MaxSpan 3 (RM_PitRamp.cs:60); DescentFalls (RM_PitTrapMath.cs:123) exempts only ladders/gear so a captured hostile walking a ramp falls

### GPT finding (verbatim)
### FC_pits_superdeep_2.1 — Walking down a valid ramp can inflict fall damage
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:686–687 (`RM_SuperdeepTrapState.Tick`)
- evidence:
  ```csharp
  if (RM_PitTrapMath.DescentFalls(walked, RM_LadderRules.LadderLetsOut(map, pos, p) || (walked && RM_PocketGrid.ClimbsOnGear(p)),
      p.Faction == Faction.OfPlayer, RM_SuperdeepTrap.Captures(p)))
  ```
- failure scenario: A normal human raider walks down a working three-notch ramp. The ramp permits this step despite the pawn’s two-notch natural climb limit, but `IsFallingArrival` classifies the drop as a fall. The quoted exemption recognizes ladders and gear, but never ramps. The raider receives fall damage during an ordinary permitted descent. Outside this part, I opened `Source/RM_PitTrapMath.cs` and confirmed that `DescentFalls` returns true for this captured, non-player walked arrival.
- confidence: high
