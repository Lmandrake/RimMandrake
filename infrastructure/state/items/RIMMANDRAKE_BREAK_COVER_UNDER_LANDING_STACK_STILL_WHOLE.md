## spec
ExplosiveKnockback 0.1.0, in-game visit 3 (`design/concepts/ExplosiveKnockback/version/in_game/visit_3/SUMMARY.md`): the
one FAIL row, sc_storeroom_bomb_pit, fails on its cover half only. Evidence
`design/concepts/ExplosiveKnockback/version/in_game/visit_3/evidence/sc_storeroom_bomb_pit_p2.txt`:
`cover=False [cell 14,8 gone=False stack@14,8 descents=1]`. The stack aimed at the covered pit cell lands on the cover and
the cover stays. No code breaks a pit cover under a landing thrown stack: `RM_ThingFlyer_Knockback.cs` never touches a
cover, and FlowWorks' `Building_SpanDeck` load sums living walking pawns only.

This item takes over RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY (filed before visit 3, caused by the scene's
first writing), so the Maturation tick routes it from this visit's road back.

## decision (carried, 2026-11-15, delegated under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME)
Build it; the scene text stands. The locked, certified leaf `thrown_into_pit_falls`
(`design/concepts/ExplosiveKnockback/tree.json`) says a good thrown onto a covered pit cell falls through and leaves the
cover broken; `sheet.md:44` says the same. Any thrown stack breaks it (the leaf names no mass floor; the obvious reading).
Where to build it is the builder's call; the flyer's landing on a covered pit cell (Knockback side, reusing
`RM_KnockbackCompat`'s cover lookup) touches the least. Widening SpanDeck's load would change FlowWorks for every dropped item.

## sort
Lowest stage that shows the fault: OFFLINE (a C# change plus an offline check); the live row is Stage 6's.
- Offline acceptance (the builder writes it with the fix, red on the base): a check that a stack's landing on a covered
  pit cell destroys the cover and descends once (e.g. a new check in
  `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storeroom_bomb_pit.py`, or the C# SelfTest).
- In-game check, recorded UNRUN with `maturation.py unrun` at close: test-table id sc_storeroom_bomb_pit,
  `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control --ticks 900`
  (proof build); PASS needs cover=True with gone=True and the control unchanged.

## launch-checks
must-fail: grep -q Cover src/RimMandrake/ExplosiveKnockback/Source/RM_ThingFlyer_Knockback.cs

(Watched red at filing on 6aabda0ebb: `grep -c Cover` prints 0, exit 1. It is a launch guard only — the flyer
still has no cover code — not the oracle.)

## verify
Acceptance test: the offline check above red on the base and green after, `selftest_explosiveknockback_storeroom_bomb_pit.py`
and `selftest_explosiveknockback_kernel.py` green; the live row recorded UNRUN for the next visit.

## criteria
- a thrown stack landing on a covered pit cell destroys the cover and falls to the floor, one descent;
- the control (no blast) leaves the cover solid;
- no change to FlowWorks' deck load for dropped items.

## refs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_ThingFlyer_Knockback.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackCompat.cs
file: src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storeroom_bomb_pit.py
