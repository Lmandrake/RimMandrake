# SPECIES_TRAITS_OVER_APTITUDES_1 — skill bonuses are the wrong instrument for species character

## the ruling that started it

Owner, 2026-09-20, while confirming six aptitude corrections one at a time:

> *"Broad comment: we should consider deeply making better traits that might do a
> better job of capturing these fine points and nuances than pluses to skills."*

He is not asking for the six fixes to be undone. He is asking whether the
**instrument** is right at all.

## why it came up — three cases in one sitting where the number could not say it

Each of these is a species whose truth does not fit on a skill axis:

1. **Geonosian.** He removed `terrible intellectual` and then said, verbatim:
   *"Not sure how to genetically capture their hive structure and need to group
   think."* The penalty was a clumsy proxy for something real — a caste insect that
   thinks as a colony. Removing it is correct and **leaves the real trait
   unexpressed**. Neither `+intellectual` nor `-intellectual` can say "needs the
   hive to think well".
2. **Abednedo.** Not wrong, over-stated: *"descended from underground builders
   before conquering their surface and space… A light nod toward it would likely be
   better and then some intellectual."* A single aptitude cannot hold "we used to
   be this, and we became that" — history, not capability.
3. **Bothan mood-sensitive fur** (`XENOTYPE_CANON_CORRECTION_1`, same sitting). The
   signature fact about the species is that their fur broadcasts their emotional
   state. There is no skill number for that at all; it is a social mechanic.

## the question to answer

**Is a RimWorld trait (or a gene with real behaviour) a better carrier for species
character than an aptitude offset — and if so, which species get one?**

Sub-questions worth putting to him separately rather than as one lump:

- Does this REPLACE aptitudes for a species, or sit alongside a reduced set?
- Is the unit a `TraitDef`, a `GeneDef` with a comp, or a hediff? Different species
  may want different answers — fur that reacts is not the same kind of thing as a
  hive dependency.
- How many species actually need this? ⚠️ If the answer is three, this is a small
  build; if it is thirty, it is a programme. **Measure the candidates before
  scoping it.**
- Does it interact with Mod Settings? Every mod we ship carries a real settings
  screen, and a species-behaviour toggle is exactly the kind of thing that belongs
  there (`MOD_OPTIONS_RETROFIT_1`).

## Watch out

- ⛔ **This does not block `XENOTYPE_CANON_CORRECTION_1`'s five confirmed aptitude
  fixes.** Those are ruled and should land. This item asks what comes after, not
  whether to pause.
- 🔴 **Gungan's `poor intellectual` is ruled to STAY** — deliberately, as *"half joke
  and half rebuke"* of the films. Any redesign here must preserve it. It is not an
  oversight and a sweep must not clean it up.
- ⚠️ **Cosmetic genes are gated.** Anything touching appearance — including Bothan fur
  as a *visual* — needs the owner's permission first, because it can break animated
  faces. Fur as a *mechanic* is not gated; fur as a *render* is.
- ⚠️ A trait is player-facing text as much as mechanism. Whatever is built, the
  description is read by the player and is subject to his eye like any prose.
- 🔑 **Do not start by writing traits.** Start by listing which species have a truth
  that no number can hold, and put that list to him. The list is the decision.

## verify

A species whose character is not a skill axis — Geonosian hive dependency, Bothan
mood-fur, Abednedo ancestry — is expressed by something a player can notice in play,
and no species carries an aptitude offset that is standing in for a concept.

## criteria

The defs say what the species IS, not the nearest number to it.


---

## 🔴 RULED 2026-09-20 — the shape, and the gene-vs-trait test

Verbatim: *"A species' trait would handle things that aptitudes don't, ideally. So
it would reduce the aptitudes that were surrogates for a better-suited trait.
Ideally these would be genes in the modern game if they apply to ALL of the race's
members, a traitdef for ones that apply to most/many but not all."*

### It REPLACES the surrogates, and only the surrogates

A trait does not sit alongside the aptitude it supersedes. **Where an aptitude was
standing in for something a trait can say properly, the aptitude is REDUCED or
removed.** ⛔ Do not leave both — that double-counts the species.

⚠️ And do not strip aptitudes that are genuinely about skill. The test is *"was this
number a surrogate for a concept?"*, not *"does this species have a trait now?"*

### 🔑 The unit is decided by REACH, and this is the whole test

| does it apply to… | use |
|---|---|
| **ALL** members of the race | **a GeneDef** |
| **most or many, but not all** | **a TraitDef** |

⇒ Worked against the three cases that raised this item:
- **Geonosian hive dependency** — true of every Geonosian ⇒ **gene**.
- **Bothan mood-sensitive fur** — canon describes it as a species-wide physiological
  fact ⇒ **gene**. ⚠️ Its *visual* expression stays behind the cosmetic gate.
- **Abednedo builder ancestry** — cultural and historical, not universal ⇒ likely a
  **trait**, if it warrants a unit at all rather than just the softened aptitude he
  already ruled.

### What is still open after this

The reach test answers *which unit*; it does not answer *which species qualify*.
🔑 **That list is still the decision** — build it and put it to him, as this item
already says. Do not start writing genes.
