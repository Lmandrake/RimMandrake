## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.4)
Verdict: CONFIRMED MINOR. Lowering a leaf restores StructuralDeckAt cells (RM_Drawbridges.cs:305-334) without classifying pawns already on the floor under it into the floor band -> they read as on the deck

### GPT finding (verbatim)
### FC_pits_superdeep_1.4 — Lowering a drawbridge promotes occupants beneath it onto the deck
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs:306-333` (`Apply`), `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:916-939` (`SweepUnder`)
- evidence:
  ```csharp
  d.leafRaised = up;
  NotifyToggled(map, changed);
  if (p == null || p.Dead || !p.Spawned || p.Map != map || RM_SuspensionUnderpass.PassingDeckAt(map, p.Position) == null)
  ```
- failure scenario: Raise a bridge over a sufficiently deep, dry pit, let a pawn walk along the exposed floor beneath the leaf, then lower it. While raised, there is no passing deck, so the pawn has no floor-band flag; existing flags are also swept away. `Apply` restores the deck without classifying its occupants as underneath. The stationary pawn now reads as standing on the deck: its draw height, load contribution, immersion protection, and movement band change. `Notify_DeckBuilt` handles this situation for newly constructed decks, but lowering does not call equivalent logic.
- confidence: high
