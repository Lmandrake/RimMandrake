# jawa/patch_switch live proof

Written by src/RimMandrake/bridgetools/prove_patch_switch.py.

| row | result | detail |
|---|---|---|
| 1 list shows at least 1 Explosive Knockback patch | PASS | 15 patches of mandrake.rm.explosiveknockback; jawaBenchPatches=529 otherPatches=733 |
| 2 after arm_count, ticks raise both counters | PASS | patch +16, original +16 in 1200 ticks (a patch counter at 0 means an inlined caller, E9) |
| 3a off succeeds and reads back off | PASS | off |
| 5a the deviation record shows the entry as overlay PUT BACK process | PASS | [{'kind': 'overlay', 'class': 'PUT BACK', 'reach': 'process', 'target': 'prefix:RimMandrake.ExplosiveKnockback.RM_Patch_JobTracker_KnockbackLandingNoSearch.Prefix@Verse.AI.Pawn_JobTracker.CheckForJobOverride(Single,Boolean)', 'before': 'on', 'after': 'off', 'state': 'UNVERIFIED', 'current': 'off', 'readBack': 'matches'}] |
| 3b a second off is refused ALREADY_OFF | PASS | ALREADY_OFF: prefix:RimMandrake.ExplosiveKnockback.RM_Patch_JobTracker_KnockbackLandingNoSearch.Prefix@Verse.AI.Pawn_JobTracker.CheckForJobOverride(Single,Boolean) |
| 3c after off, the original counter rises and the patch counter does not | PASS | patch +0, original +19 in 1200 ticks |
| 4a on succeeds and reads back on | PASS | on |
| 4b after on, both counters rise | PASS | patch +24, original +24 in 1200 ticks |
| 5b the entry is repaid and the receipt reads tainted | PASS | {'tainted': True, 'clean': False, 'overlay': 'none'} |
| 4c a second on is refused ALREADY_ON | PASS | ALREADY_ON: prefix:RimMandrake.ExplosiveKnockback.RM_Patch_JobTracker_KnockbackLandingNoSearch.Prefix@Verse.AI.Pawn_JobTracker.CheckForJobOverride(Single,Boolean) |
| 4d a JawaBench patch is refused by name | PASS | JAWABENCH: JawaBench.BridgeTools.JawaBenchPatchSwitch.CountPatchPre is a JawaBench patch; the switch does not take off its own hooks |
| 6 a canonical save is refused (scene layer; tool: unit off-refusals) | PASS | CANONICAL_SAVE |

VERDICT PASS
