## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.3)
Verdict: CONFIRMED MINOR. NeedsWrite skips legacy members whose look equals the default (ConduitStyles.cs:352-357, RM_MapComponent_ConduitRuns.cs:327-328); joined to an explicitly styled winner they drift when the default changes

### GPT finding (verbatim)
### FB_hose_gss_2.3 — A styled winner can retain legacy members that later change to another look
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStyles.cs:352–356` (`NeedsWrite`); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_ConduitRuns.cs:328` (`Paint`)
- evidence:
  ```csharp
  if (force || hasStyle) return true;
  if (look != defaultLook) return true;
  return isConduit && look == "Modern" && (IsColour(colourMode) || colourMode == Mix);
  ```
- failure scenario: With Industrial as the default, join a smaller legacy run to a larger explicitly styled Industrial run. The legacy members remain unwritten because their current appearance already matches. Change the default to Modern: those members become Modern while the explicitly styled winner remains Industrial. The legacy-winner clearing rule handles the opposite case, but this case still breaks “one run, one style.”
- confidence: high
