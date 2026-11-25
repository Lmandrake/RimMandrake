## spec
Explosive Knockback, Design Version 0.2.0 (next version; not 0.1.0). When a blast throws a pawn that is carrying something,
the carried thing leaves its hands and flies on its own trajectory, separate from the pawn.

Owner, 2026-11-14 about 2:40 PM PST, answering journal question 7 (`design/concepts/ExplosiveKnockback/journal.md`):
"For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories."

0.1.0 as built and kept: the pawn flies holding what it carries (`RM_MapComponent_Knockback.cs`, `PawnFlyer.MakeFlyer(...,
flyWithCarriedThing: true)`); scene sc_pawn_arc checks that the colonist still holds the stack after landing. The hose-end
rule (bar hose_drops_at_takeoff, owner Q6: a hose end drops where the carrier stood) is a separate bar and stays.

## Acceptance test (draft)
1. Offline (kernel selftest, new K case): for one blast and one ray, a 70 kg pawn and the 10 kg stack it carries get two
   plans from the kernel, each for its own mass; the stack's planned cells are more than the pawn's (lighter flies farther),
   and a stack over lightMassLimit gets no throw plan (it drops on the takeoff cell). Seen red on today's code, where the
   carried stack has no plan of its own.
2. Offline (static): the pawn throw no longer calls MakeFlyer with flyWithCarriedThing true; the carried stack is handed to
   the goods flyer (RM_ThingFlyer_Knockback). Seen red today.
3. In game (a revised sc_pawn_arc, proof build, minimal list): a colonist hauling a named stack one cell from a grenade. On
   the launch tick the colonist's hands are empty and the stack is inside its own RM_ThingFlyer_Knockback; the two drawn
   positions differ on at least one mid-flight tick; the stack lands on its own kernel cell, count unchanged, no
   duplicate; the colonist lands on its planned cell with empty hands. Control: a colonist carrying nothing flies as today.

Owner, 2026-11-24 (OWNER:1795565769863524396): "Thing thrown colonist carries flies on own arc: YES." It is bar
`carried_thing_own_arc` of Design Version 0.2.0 (`design/concepts/ExplosiveKnockback/record.json`).

Also in this work, only if it changes `RM_PawnFlyerPatches.Hauling` (the Conductor's call, 2026-11-24): an entry of that
static map is removed when its pawn dies or is destroyed in flight. Test first: a kernel or static case that a pawn killed
in flight leaves no entry. If this work does not touch that code, leave the static as it is.

Listed in `design/concepts/ExplosiveKnockback/version/next_version/README.md`.
