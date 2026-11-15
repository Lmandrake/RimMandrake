# RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY

## spec

Explosive Knockback sc_storeroom_bomb_pit expects "the stack aimed at the covered cell falls through it with one descent
and the cover is destroyed". No code does it: Building_SpanDeck's load sums living walking pawns only (FlowWorks
`Pits/Building_SpanDeck.cs` ~256) and `RM_ThingFlyer_Knockback` never touches a cover.

## decision (2026-11-15 11:45 AM PST, BENCH, delegated under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME)

Build it; the scene text stands. A landing thrown stack breaks the cover and falls through. The locked, certified leaf
`thrown_into_pit_falls` (`design/concepts/ExplosiveKnockback/tree.json`) says "A pawn or a good thrown toward an open pit
falls to its floor, one thrown onto a covered pit cell falls through and leaves the cover broken", and `sheet.md:44`
says "Anything thrown ... onto a covered cell falls through and breaks the cover". No owner word against it was found.

Where to build it is the builder's call; the flyer's landing on a covered pit cell (Knockback side) touches the least,
and widening SpanDeck's walking-pawn load would change FlowWorks for every item dropped on a deck.

Acceptance: the live cover row of `knockback_runner.py --scenes storeroom_bomb_pit --ticks 900` (cover=True), plus an
offline check that a stack landing on a covered cell destroys the cover and descends once; watch it fail on the base.
