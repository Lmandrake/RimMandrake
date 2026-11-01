## Spec
Owner ruling 2026-10-16, by card "How should players lacquer clothes and weapons with deepfire? → Bill + right-click
the press". Lacquering happens at the powered deepfire press (RM_DeepfirePress), never through a pawn gizmo:
1. Bills RM_LacquerApparel / RM_LacquerWeapon (`src/RimMandrake/LuminousPigment/Defs/RecipeDefs/RM_LacquerAtPress.xml`):
   one stored item plus N deepfire (N = costApparel / costWeapon Mod Setting) gives back the SAME item with one more coat.
2. Right-click the press with a colonist selected: "Lacquer <item> (N deepfire)" for each worn or held item; the option is
   disabled with "The deepfire press has no power." when the press is unpowered.
Code: `Source/LacquerAtPress.cs` (worker, bill eligibility patch, FloatMenuOptionProvider), `LuminousPigmentMod.cs`
SetLacquerRecipeCost. Built c34ad447fc; DLL 603e89e053 (srchash MATCH 2026-10-30).

## Verify
- [x] Offline: `selftest_lacquer_press.py` (XML-to-C# contract, 17 mutants red) and `selftest_luminouspigment.py` green
  (295921bc44). RM_LacquerAtPress.xml CLEAN on GPT review (2 rounds, 0 XML findings).
- [x] Live: bill round trip returns the same item with +1 coat (verify partial, 747999af5b, Transient/bench_live_20261016b/fw_afk_batch.md).
- [ ] Live, owed: right-click the powered press with a colonist selected lists one option per worn/held item, and taking
  one runs the lacquer job.
- [ ] Live, owed: with the press unpowered, the same options show greyed with "The deepfire press has no power."

## Notes
selftest_lacquer_press.py is DIRTY: its last edits (GPT round 2's findings) have not had a zero-finding review round yet.
Evidence and reviews: D:\ClaudeWork\rimmandrake\lacquer_press\ (gpt_review_r1.md, gpt_review_r2.md, selftest_lp.txt).
