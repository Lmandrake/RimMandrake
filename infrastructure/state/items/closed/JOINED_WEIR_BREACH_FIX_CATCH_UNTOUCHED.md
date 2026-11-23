## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.7)
Verdict: CONFIRMED MINOR. Catch is placed at RunHead().BankCell (RM_Weir.cs:362,385) but Breach->WashCatch washes this.HeldCatch() of the breaching section (RM_Weir.cs:424,459) -> head's shared catch stays on the bank

### GPT finding (verbatim)
### FA_core_sim_4.7 — A breach away from a joined wall’s head leaves the shared catch untouched
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs`:362, 420–424, 459 (`CaptureFloating`, `Breach`, `WashCatch`)
- evidence:
  ```csharp
  RM_Building_BankWeir head = RunHead() ?? this;
  int washed = RM_RiversSettings.breachWashesCatch ? WashCatch() : 0;
  return RM_RiverMath.WashHeld(HeldCatch(),
  ```
- failure scenario: Build a long joined weir wall. Every section deposits its catch at the run head’s bank, but a section several cells away breaches. The shared pool correctly disappears because `RunHolds` fails; the breach wash nevertheless searches only around the breached section. Catch at the head remains on the bank despite the configured run-breach wash behavior.
- confidence: high
