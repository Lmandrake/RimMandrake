# Explosive Knockback: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

**Opened as Design Version 0.2.0 on 2026-11-24** (`../VERSION.json`, `../vision.md` §0.2.0). The three entries below are its scope; each keeps its record here. The bruise entry's rule changed on his words of 2026-11-24 (see the entry).

*Empty at entry on 2026-11-13: no open judge gap sorted as next version.* His melee-shove idea was ruled to belong to FlowWorks and is listed there.

## The carried thing flies its own trajectory (rimflow `RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC`)

- **Proposed by:** the owner, 2026-11-14, answering journal question 7: *"For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories."*
- **Why not 0.1.0:** his own word, "for today have them hold it". 0.1.0 flies the pawn with what it carries (`flyWithCarriedThing: true`); sc_pawn_arc checks it still holds the stack after landing.
- **Acceptance test:** a kernel case gives the pawn and its carried stack separate plans by their own mass (the lighter stack goes farther; a stack over the light-goods limit drops on the takeoff cell); in a revised sc_pawn_arc the colonist's hands are empty on the launch tick, the stack flies in its own goods flyer on a different drawn path, lands on its own planned cell with its count unchanged and no duplicate, and the colonist lands empty-handed. Control: a colonist carrying nothing flies as in 0.1.0. Full text in the item.

## A thrown pawn landing on a pawn bruises both (rimflow `RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN`)

- **Proposed by:** the owner by card, 2026-11-14, journal question 8: "Bruise in the next version".
- **Why not 0.1.0:** the card's choice. 0.1.0 keeps the harmless landing (journal line `land_on_pawn`, no damage).
- **Changed 2026-11-24, his words** (OWNER:1795565769863524396): *"Thrown pawn lands on another bruises both, and the bruising should be proportional to the size of the thing that hit you (BIG creature on small creature really hurts small creature, big creature relatively unaffected, tune to common sense elephant/rat, person on dog or dog on person, etc.)"*. The entry had scaled the bruise by the thrown pawn's mass only.
- **Acceptance test:** a kernel function gives each of the two pawns a Blunt amount from the mass of the other against its own: far larger for the lighter of an unequal pair, near nothing for the heavier, small and equal for a like pair, and 0 on an empty cell; live, a colonist thrown onto a small animal and onto a large one shows each case, and the `land_on_pawn` line carries both amounts. Full text in the item.

## Our own blast show replaces Extra Explosion Effects (rimflow `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`)

- **Proposed by:** the owner by card, 2026-11-12 about 4:5x PM PST: Extra Explosion Effects → "Absorb the idea into Knockback" (OWNER tsn 1794530931586663595). On his Gimme Some Slack walk of 2026-11-20, the note on the item made the donor's soot and crater flecks the art bar: our soot, scorch and crater must be a significant improvement on them.
- **Why not 0.1.0:** the 0.1.0 vision (`../vision.md`) holds no blast visuals. This adds a part, so it is Divergent. Entered here by the ticket sweep of 2026-11-22 by the obvious reading. The Conductor confirms the split.
- **Acceptance test:** `proof/absorb_blast_show_check.py` (red on base at filing: A1, A3, A4, A5). Our own FleckDefs and textures pass the art judge. A one-blast live look shows both kept mods (Better Explosions, Dynamic Effects Forge) loaded, with no doubled show. Full text in the item.
- **Changed 2026-11-24, his words** (OWNER:1795565769863524396): *"Let's drop all those mods and replace them with SO MUCH BETTER stuff."* This replaces his card of 2026-11-12 that kept Better Explosions and Dynamic Effects Forge: all three explosion-visual mods leave the lists when our show ships, so no stacking with a kept mod is designed. The design, its ranked set and its art list: `design/specs/2026-11-24-knockback-blast-show/design.md`.
