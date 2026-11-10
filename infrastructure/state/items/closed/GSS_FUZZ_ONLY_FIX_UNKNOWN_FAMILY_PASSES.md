## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_4.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_4.6)
Verdict: CONFIRMED MINOR. GssFuzz.cs:630-672 each family gated on only==name with no unknown-name refusal; --fuzz-only cord runs 0 checks and exits 0

### GPT finding (verbatim)
### FE_cs_selftests_4.6 — Unknown fuzz-family names silently run zero checks successfully
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/GssFuzz.cs:630–705`; `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/Program.cs:45` (`Run`, fuzz-only dispatch)
- evidence:
  ```csharp
  if (only == null || only == "cords")
  ```
  ```csharp
  if (only == null || only == "aerial")
  ```
  ```csharp
  if (only == null) NegativeControls();
  ```
- failure scenario: Invoke `--fuzz-only cord`, or use the former `hose` family after its move to FlowWorks. Neither family executes, and negative controls are skipped too. `Program.Main` prints `0/0 checks passed (fuzz only)` and exits zero. A typo or stale automation therefore becomes a successful empty run. This follows entirely from the supplied files.
- confidence: high
