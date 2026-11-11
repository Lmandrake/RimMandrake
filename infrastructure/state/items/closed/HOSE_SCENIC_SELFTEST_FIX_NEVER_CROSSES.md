## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_2.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_2.3)
Verdict: CONFIRMED MINOR. HoseReviewChecks.cs:445-448 walls at z=7/10 leave the westward corridor open, so forced.Ok never needs to cross the costed rig

### GPT finding (verbatim)
### FE_cs_selftests_2.3 — The “building cost never blocks” fixture never requires crossing a building
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs:445–448 (`HoseGptFix.ScenicRoute`)
- evidence:
```csharp
            CordWorld boxed = Rig(true);
            for (int x = 0; x < 44; x++) { boxed.SetBlocked(new Cell(x, 7), BlockKind.Wall); boxed.SetBlocked(new Cell(x, 10), BlockKind.Wall); }
            HoseLay forced = HoseMath.Lay(boxed, reel.Mouth, new Cell(14, 9).Centre, prm, 7, null, reel.Outward);
```
- failure scenario: The reel occupies x=20–21 and faces west; the target is west at x=14.5. The walls leave the westward route open. Thus `forced.Ok` proves that a hose can leave its nozzle along the corridor, without proving that it can cross a costed building when necessary. A regression that forbids traversing building cells can escape this particular check. Outside this part, I opened `Source/Hose/HoseMath.cs` to confirm the default west-facing mouth.
- confidence: high
