# Frozen statement not proved

Both requested stale failures pass at tested HEAD `14b5a573688a293511f8a64ea2cac4d90410ff2c`. The existing test-only repair is published in `4e9da327df7ba0a60b50837e200efb711fcbfef1`; production changes explain both original mismatches. No source/test edits or weakened assertions were made here.

The single real full relevant run is RED: 1233/1238 main cases, 455/455 hose assertions, runner exit 1. Raw complete output and receipts are in `evidence/csharp_stdout.txt`, `evidence/selftest_stdout.txt`, and `evidence/selftest_receipt.json`. Therefore the frozen suite-green bullet cannot be claimed. Fixing five distinct further guards across different subsystems is beyond this two-stale-failure verification unit. No repeated run or other-item repair was performed.

The next authorized work must establish the intended behavior for each failed guard against the current implementation before changing tests or production:

| Failed case | Exact source pairing and observed difference to investigate |
| --- | --- |
| RiverSwitchFlip_weirWhiteWater | `Source/SelfTest/RiverSwitchFlipChecks.cs:210` vs `Source/Rivers/RM_Weir.cs:705`: old inline setting condition vs `animate` local controlling white-water drawing. |
| PitCapture_follows_a_held_pawn_that_moves | `Source/SelfTest/RelativeRulesChecks.cs:79` vs `Source/Superdeep/RM_PitRooms.cs:761` and `:813`: step logic remains; victim hold now uses a separate job/helper rather than the old exact ForceWait call. |
| PipePole_P3_sag_at_the_slider_extremes | `Source/SelfTest/PipePoleChecks.cs:122` vs `../GimmeSomeSlack/Source/Aerial/AerialMath.cs:147`: guard expects the inline parabola; current curve uses `Droop(t)`. Prove the intended curve and slider behavior rather than replacing the literal blindly. |
| LW1 … TakeLayWorld … | `Source/SelfTest/HoseMateEndQueueChecks.cs:298` vs `Source/Hose/RM_MapComponent_Hoses.cs:416`: old bool MarkDirty/MapChanged fallback vs current corridor versions and unconditional MarkDirty calls. Prove invalidation/convergence before adjusting the guard. |
| Thirst_small_pond_drink_admitted | `Source/SelfTest/ThirstChecks.cs:80` vs `Source/Thirst/RM_ThirstUtility.cs:506`: guard expects a continue in the search method; affordability refusal now returns true from local Consider. Prove that this skips the candidate without ending admission incorrectly. |

Paths beginning `Source/` above are relative to `src/RimMandrake/FlowWorks/`. These are observed guard mismatches and next inspection targets, not accepted repairs or proof of five production defects. After genuinely resolving them under the appropriate scope, run the same relevant wrapper once and obtain review of that new evidence.

The one fresh independent Opus judge returned `would show: no`. It confirms the two repairs preserve their intended checks, rejects the green-suite claim, and qualifies bullet 1's wording: the count pins the three unit-times-beds resizing occurrences, not every capacity assignment or method identity. Parent marked DONE bullet 1 false because that broader wording is not proved; the original verifier assessment is preserved in evidence/done_before_parent_review.md. The frozen statement was not rewritten.

CLI denied the judge's Write. Its exact complete denied payload was recovered unchanged, with hashes and denial preserved in `evidence/judge_raw.json` and `evidence/judge_recovery.json`. No additional reviewer was launched. Post-review ancestry and integrity checks are recorded separately; they do not change the independent report or its rejection.

Parent alone decides subsequent scope, publication, ledger and closure. Nothing here marks the unit accepted or CLEAN.
