## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.10). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.10)
Verdict: CONFIRMED MINOR. Cover trigger cheap lead test checks cardinals only (CompPitCoverTrigger.cs:75-79); every local id-minimum then runs a full Deck flood-fill (82-86) -> near-quadratic scans on patterned decks

### GPT finding (verbatim)
### FC_pits_superdeep_1.10 — Cover scans remain quadratic for decks with many local ID minima
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Trigger/CompPitCoverTrigger.cs:75-85` (`RunScan`)
- evidence:
  ```csharp
  if (n != null && n.thingIDNumber < self.thingIDNumber) return;
  List<Building_PitCover> deck = RM_PitCoverUtility.Deck(self);
  if (c.thingIDNumber < self.thingIDNumber) return;
  ```
- failure scenario: Build alternating cells of a large cover deck first, then fill its gaps. Many earlier covers have only higher-ID cardinal neighbours, so all pass the cheap test. Each performs the entire allocating flood-fill before discovering that it is not the global lead. There can be approximately N/2 such candidates on an N-cell deck, retaining O(N²) work every scan interval and causing recurring game hitches. The optimization works well for monotonic construction order but does not provide the claimed general reduction.
- confidence: high
