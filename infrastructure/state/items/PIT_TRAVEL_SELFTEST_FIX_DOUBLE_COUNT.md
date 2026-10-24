## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_2.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_2.1)
Verdict: CONFIRMED MINOR. PitAccessChecks.cs:141-143 Src (RiverSwitchFlipChecks.cs:44) collapses whitespace, so both regexes match both detectors (RM_SuperdeepTrap.cs:682,765-766): 4 matches, still >=2 with one guard removed

### GPT finding (verbatim)
### FE_cs_selftests_2.1 — One arrival detector is counted twice as proof that both are guarded
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/PitAccessChecks.cs:141–143 (`PitTravel_every_trap_mask_reach_and_fall_read_asks_it`)
- evidence:
```csharp
                Assert(System.Text.RegularExpressions.Regex.Matches(tr, @"!p\.Flying && !\(RimMandrakeFlowWorksSettings\.pitFreeTravelEnabled && RM_PocketGrid\.FreePitTraveller\(p\)\)").Count
                    + System.Text.RegularExpressions.Regex.Matches(tr, @"!p\.Flying\s*&& !\(RimMandrakeFlowWorksSettings\.pitFreeTravelEnabled && RM_PocketGrid\.FreePitTraveller\(p\)\)").Count >= 2,
```
- failure scenario: Remove the free-traveller guard from either arrival detector. The other detector, with an ordinary space before `&&`, matches both expressions and contributes two matches. The assertion still passes while one arrival path can treat a jumper or floater as falling. I reproduced the double count with a single constructed detector string. Outside this part, I opened `Source/Superdeep/RM_SuperdeepTrap.cs` to confirm the two intended detector sites.
- confidence: high
