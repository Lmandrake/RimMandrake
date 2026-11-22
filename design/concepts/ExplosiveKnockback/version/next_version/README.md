# Explosive Knockback: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*Empty at entry on 2026-11-13: no open judge gap sorted as next version.* His melee-shove idea was ruled to belong to FlowWorks and is listed there.

## The carried thing flies its own trajectory (rimflow `RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC`)

- **Proposed by:** the owner, 2026-11-14, answering journal question 7: *"For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories."*
- **Why not 0.1.0:** his own word, "for today have them hold it". 0.1.0 flies the pawn with what it carries (`flyWithCarriedThing: true`); sc_pawn_arc checks it still holds the stack after landing.
- **Acceptance test:** a kernel case gives the pawn and its carried stack separate plans by their own mass (the lighter stack goes farther; a stack over the light-goods limit drops on the takeoff cell); in a revised sc_pawn_arc the colonist's hands are empty on the launch tick, the stack flies in its own goods flyer on a different drawn path, lands on its own planned cell with its count unchanged and no duplicate, and the colonist lands empty-handed. Control: a colonist carrying nothing flies as in 0.1.0. Full text in the item.

## A thrown pawn landing on a pawn bruises both (rimflow `RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN`)

- **Proposed by:** the owner by card, 2026-11-14, journal question 8: "Bruise in the next version".
- **Why not 0.1.0:** the card's choice. 0.1.0 keeps the harmless landing (journal line `land_on_pawn`, no damage).
- **Acceptance test:** a kernel function gives a small Blunt amount that rises with the thrown pawn's mass, stays under a stated cap that never downs a healthy colonist, and is 0 on an empty cell; live, a pawn that walks onto the landing cell mid-flight and the thrown pawn each take that one hit, the `land_on_pawn` line carries the amount, a heavy thrown pawn bruises more than a light one, and an empty-cell landing hurts no one. Full text in the item.

## Our own blast show replaces Extra Explosion Effects (rimflow `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`)

- **Proposed by:** the owner by card, 2026-11-12 about 4:5x PM PST: Extra Explosion Effects → "Absorb the idea into Knockback" (OWNER tsn 1794530931586663595). On his Gimme Some Slack walk of 2026-11-20, the note on the item made the donor's soot and crater flecks the art bar: our soot, scorch and crater must be a significant improvement on them.
- **Why not 0.1.0:** the 0.1.0 vision (`../vision.md`) holds no blast visuals. This adds a part, so it is Divergent. Entered here by the ticket sweep of 2026-11-22 by the obvious reading. The Conductor confirms the split.
- **Acceptance test:** `proof/absorb_blast_show_check.py` (red on base at filing: A1, A3, A4, A5). Our own FleckDefs and textures pass the art judge. A one-blast live look shows both kept mods (Better Explosions, Dynamic Effects Forge) loaded, with no doubled show. Full text in the item.
