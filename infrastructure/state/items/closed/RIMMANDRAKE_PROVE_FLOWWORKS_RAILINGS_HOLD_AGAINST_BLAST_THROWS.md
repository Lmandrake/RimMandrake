# RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #20 (his words, the picture, the station).

## spec

Bridge railings exist to stop a pawn being blown off (his words). A railing is a rail for blast throws (`src/RimMandrake/FlowWorks/Source/Pits/Suspension/Building_SuspensionDeck.cs:417`, `Source/Superdeep/RM_FallRails.cs:43`) [measured]; no live row reads it [guess ~80%].

## verify

Live, ExplosiveKnockback loaded: a colonist on a railed suspension deck square beside its rail, a knockback blast on the far side throwing toward the rail; a twin on a railings-off deck.

## criteria

Acceptance test: the railed colonist lands on the deck with no descent recorded; the twin is thrown into the pit. UNRUN: the game was his.
