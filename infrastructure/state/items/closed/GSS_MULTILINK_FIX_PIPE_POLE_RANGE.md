## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.6)
Verdict: CONFIRMED MINOR. Probe cmultilink plan uses AerialSettings.Range for all kinds (ConduitStyleProbe.cs:99) while the gizmo groups by kind with RangeFor (CompAerialAnchor.cs:477-480) -> probe disagrees with play

### GPT finding (verbatim)
### FB_hose_gss_2.6 — Multilink planning uses the power range for pipe poles
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStyleProbe.cs:99` (`MultiLink`, `:plan` branch); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs:478–479` (`AutoLinkSelected`)
- evidence:
  ```csharp
  var pairs = AerialMath.MinimumSpanningLinks(mine.Select(s => s.Info()).ToList(), AerialSettings.Range);
  ```
- failure scenario: With the shipped 20-cell power range and 12-cell pipe range, ask `cmultilink:…:plan` about two pipe poles 16 cells apart. The probe returns a planned pair, while the real gizmo groups by kind and correctly creates no link. The purported control therefore disagrees with the action it claims to model.
- confidence: high
