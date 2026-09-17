# UNSUBSTANTIATED_SPECIES_ABILITIES_1 — the reverse audit

Owner, 2026-09-17, verbatim: *"I would also like a review of any races that appear to have
exceptional abilities that canon does NOT substantiate."*

## Why this is a different item, not a part of the other one

`XENOTYPE_CANON_CORRECTION_1` searched in ONE direction: abilities canon gives a species that
the defs fail to grant (four aquatic species that cannot breathe water, Defel without stealth,
Falleen without colour shift). This item is its mirror: abilities the defs **grant** that canon
never claimed. Nothing has looked that way yet, so the size is UNMEASURED.

🔑 Why the mirror matters more than it sounds: an ungranted canon ability is a species that
feels flat. An **ungrounded** granted ability is a species that is quietly stronger than the
world says it should be — a balance defect wearing lore's clothes, and one no canon-vs-def
comparison in the other direction can ever surface.

Two already-known instances came out of the forward audit and belong here rather than there:

- **Rakata carry psychic genes.** Post-plague Rakata are Force-blind, so this is an ability
  granted against canon, not merely misassigned.
- **Cerean carries enhanced psychic ability**, where the source says its Force sensitivity is
  ordinary.

## spec

1. Read every xenotype in `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/` and list the
   genes each grants that confer a real advantage — psychic, combat, resilience, aptitude,
   metabolic, longevity, immunity.
2. For each, check the species' entry in `design/RimStarWars/canon_references/` for a source
   that substantiates it. Three verdicts, kept apart: substantiated · unsubstantiated ·
   contradicted (canon says the opposite).
3. ⚠️ **Do not treat our own canon library as authority on its own.** The owner ruled
   2026-09-17 that the downloaded canon material contains errors and he verifies citations by
   web search himself. Where the library asserts something with no source, report it as
   unsourced rather than as canon.
4. Rank by how much the ability actually changes play, not by how far it departs — a flavour
   gene nobody notices is a lower priority than a combat or psychic advantage.

## verify

Every xenotype examined (count stated MEASURED, matching the file's real xenotype count).
Each granted advantage carries one of the three verdicts and, where substantiated, the
verbatim canon text and its source. No fix applied — this item reports; the owner rules.

## his standing constraint on fixes

He ruled 2026-09-17 on the sister item that aptitude corrections are **confirmed with him
one at a time**, not applied in a batch. Assume the same here until he says otherwise.
