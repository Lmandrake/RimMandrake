## spec
`src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_journal_jolt.py` (blind cycle 2, steward decisions 4,
6, 7) reads `RM_MapComponent_Knockback.cs` for text patterns (`int kernelCells = RM_KnockbackMath.ThrowCells(`, the
goods' WildCells x GoodsThrowWild line, ThrowContainer's ContainerThrowCells, the flying-off and too_weak skips, the
ItemWillBeThrown kernel-cell guard). ffc3937ee7 moved those rules into `RM_KnockbackPlan.cs`, and its own message says
three other text checks read the old file "and are red until the steward applies the drafted repair". Standalone run
2026-11-18 ~7:10 PM PST on 0117263cc: rc 1, 6 faults, 11 of 16 planted breaks caught [measured]. Whether each rule
still holds in RM_KnockbackPlan.cs is unread; that is the repair's first step. The suite is registered as a supports-only
entry (T_JOURNAL_JOLT_OFFLINE) by RIMMANDRAKE_REGISTER_EK_SELFTESTS_THIRTEEN_NO_TABLE_ENTRY_SAW, so its red shows on
every certificate run.
Same cause in `selftest_explosiveknockback_blind_cycle1.py` (registered as T_BLIND_CYCLE1_OFFLINE): its
`design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_1/lane2/check_fix_wiring.py` reads Execute for
"throws goods by WildCells with GoodsThrowWild", "keeps the plain kernel for pawns", "ItemWillBeThrown decides by
WildCells": 8/11 FAIL, 2026-11-18 ~8:10 PM PST [measured].

## verify
Acceptance test: `python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_journal_jolt.py` exits 0 with
16 of 16 planted breaks caught, and `python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blind_cycle1.py`
exits 0. Both watched FAIL as above.

## criteria
- Each journal/jolt rule is checked where it now lives, and every planted break is caught.
