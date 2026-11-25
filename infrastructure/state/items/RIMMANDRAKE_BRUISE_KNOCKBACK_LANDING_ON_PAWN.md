## spec
Explosive Knockback, Design Version 0.2.0 (bar `collision_bruise_by_size` in `design/concepts/ExplosiveKnockback/record.json`).
When a thrown pawn meets another pawn, both are bruised, and each one's bruise follows the size of the other.

Owner, 2026-11-24 (OWNER:1795565769863524396): "Thrown pawn lands on another bruises both, and the bruising should be
proportional to the size of the thing that hit you (BIG creature on small creature really hurts small creature, big creature
relatively unaffected, tune to common sense elephant/rat, person on dog or dog on person, etc.)". This replaces the first
text of this item, which scaled the bruise by the thrown pawn's mass only. His card of 2026-11-14 (journal question 8):
"Bruise in the next version".

The rule, as the Designer read it (his to undo):
- "Size" is the creature's mass (the Mass stat), the measure this mod already throws by.
- Each pawn takes one Blunt hit. Its amount rises with the mass of the OTHER pawn against its own mass. A like pair bruise
  each other lightly and alike. In an unequal pair the lighter one is really hurt and the heavier one is nearly unhurt.
- Common sense, to tune against (these are tuning, not bars): a person on a rat can kill or cripple the rat and leaves the
  person a scratch at most; a rat on a muffalo or an elephant hurts the rat and leaves the big animal nothing to treat; a
  person on a dog downs or badly bruises the dog, and the person gets a light bruise; a dog on a person bruises both, the
  dog more; a person on a person bruises both lightly, and never downs a healthy adult.
- No living creature over the mass limit is ever thrown, so an elephant is only ever the one that is landed on.
- The same rule covers both ways two pawns meet: a pawn that walks onto the landing cell mid-flight (journal line
  `land_on_pawn`), and a pawn in the path that stops the thrown pawn (leaf pawn_hits_pawn_stops; today only the thrown pawn
  takes a wall-like hit).
- A pawn that a sandbag stops before it reaches the other pawn hits nobody (bar `no_impact_without_contact`).
- A landing on an empty cell bruises nobody. The bruise is not blast damage: a shield belt does not absorb it.

0.1.0 as built and kept: the thrown pawn lands on its planned cell, the journal writes `land_on_pawn` naming the other pawn,
and neither takes damage.

## Acceptance test
1. Offline (kernel selftest, new case K_COLLISION_BRUISE; seen red on 2026-11-24's code, which has no such function):
   a function of (own mass, other mass) returns the Blunt amount one pawn takes.
   - like pair (70 kg, 70 kg): both amounts equal, above 0, and under the amount that downs a healthy adult;
   - unequal pair (70 kg person, 1 kg rat): the rat's amount is many times the person's, and the person's is near 0;
   - the amount never falls as the other's mass rises with own mass fixed, and never rises as own mass rises with the
     other's fixed (swept over 0.5 to 2000 kg);
   - no other pawn: 0; a mass of 0 or less, or not a number: 0 and no exception.
2. Offline: lane | sandbag | pawn returns no hit and no bruise for the standing pawn (red today: `RM_KnockbackMath.Resolve`
   reports the hit).
3. In game (a revised sc_pawn_arc lane, proof build, the mod's small list), kind A:
   - a colonist thrown onto a cell that a small animal walks onto: the animal takes one Blunt hit, the colonist a far
     smaller one, and `land_on_pawn` carries both amounts;
   - a colonist thrown onto a cell that a large animal walks onto: the colonist takes the larger hit;
   - a colonist thrown into a standing colonist: both take a light hit and neither is downed;
   - control: a landing on an empty cell gives no hit to anyone.

Listed in `design/concepts/ExplosiveKnockback/version/next_version/README.md`.
