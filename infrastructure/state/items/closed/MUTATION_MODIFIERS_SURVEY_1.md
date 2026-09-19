# MUTATION_MODIFIERS_SURVEY_1 — survey every mutation-type system in the stack

Owner, 2026-09-06 (`the_contagion.md` §7): Contagion-touched must start *much larger, more
random* mutations — *"I think there are also other mutation-type modifiers already in the
game we should survey, so it's not just genetic shuffling."* Bad genes are definitely in
the deck (genetic instability and kin). **It never just upgrades you.**

## spec
- Inventory, from the live def dump + mod XML (never guess a defName):
  - Biotech: negative/instability genes, gene complexity/metabolism costs, xenogerm
    rejection, archite genes.
  - Anomaly (if `ANOMALY_EXCEPTION_ACCESS_1` allows reading it): fleshmass, mutations,
    the shambler/ghoul hediff families.
  - More Consumables & Mutagens: the Igni/Sil/Ursa/Midia/Myrol part mutations
    (`Hediff_AddedPart` with melee verbs), `SlurryHigh`'s random hediff-giver roll,
    `makeImmuneTo` exclusivity pairs (`genepack_mods_plunder.md` has the read).
  - Alpha Animals / Alpha Biomes: any transformation hediffs (the half-transformed tree
    pattern, infected variants).
  - Vanilla: mechanites, luciferium-style permanent hediffs, scarring/permanent injuries.
- Classify each by: genetic vs somatic vs part-addition vs behavioral; reversible?;
  net-negative guaranteed?; visible on the pawn?
- Propose the Contagion-touched deck from that classification: weighted toward
  somatic/part mutations and instability, with the never-upgrade guarantee enforced by
  construction (every roll pairs at least one cost).
- Feeds also: the Unfinished's random-limb spawner (same part-addition mechanism).

## verify
A written table with defNames and sources; the owner rules the deck.

## Survey done 2026-09-12 (BENCH belt wave)
Deliverable written: `research/mutation_systems_survey_2026-09-11.md` — 7 systems,
~55 defNames MEASURED (per-section counts + UNMEASURED stat blocks flagged inside),
classification table + "DRAFT — owner rules the deck" section. Remaining on this
item: the owner rules the deck (can ride MECHANICS_CARDS_SITTING_1).

## Deck RULED 2026-09-12 (owner cards) — item complete
Custom Utinni instability gene; removal risk copies the existing
hostile-spawn mechanism; roll shape is the owner's 50% all-negative / 50%
positive+negative large-variance rule ("The Contagion isn't nice"), deleting
the drafted 90/10. Recorded verbatim in the survey's "THE DECK IS RULED"
section. Build rides the Contagion/Unfinished items.
