## spec
Ruling: `items/CAST_NINE_SPECIES_MISSING_1.md` `## ruling`.

Add **nine XenotypeDefs** to `src/Jawa/RimMandrake_StarWarsRaces/`, so eleven named
characters generate as the species they were written as:

| xenotype | characters | the anatomy the prose names |
|---|---|---|
| `RimMandrakeWhiphid` | Ma'kesh Bruul | 2.5 m, matted white fur, tusks, hates heat |
| `RimMandrakeArcona` | Vekshaa · Nekk Arda | hammerhead skull; ⭐ **eye colour carries the salt addiction and must be visible** |
| `RimMandrakeGran` | Pell Onasso · Ubo Tass | three stalked eyes |
| `RimMandrakeIshiTib` | Ushet Kel Ba | hooked beak, eyestalks, hide that splits when dry |
| `RimMandrakeKitonak` | Onk-Onk-Deshu | pale, boneless-looking, 300 kg, breathes through the skin |
| `RimMandrakeAbyssin` | Uzzo One-Eye | ⭐ **one enormous eye**, regenerating limbs, works at noon |
| `RimMandrakeBarabel` | Sszik Vhan | black scales |
| `RimMandrakeBesalisk` | Vurgo Nakk | ⚠️ four arms — see below |
| `RimMandrakeToydarian` | Ippo Nuum | ⚠️ snout, wings — see below |

⭐ **The pattern is proven seventy times over in this exact mod.** Copy the shape of an
existing entry — `RimMandrakeQuarren` is a good model: `defName` · `label` · `description` ·
`iconPath` · `inheritable` · `canGenerateAsCombatant` · `factionlessGenerationWeight 0` ·
`nameMaker` · `genes`. The mod already ships `GeneDefs/`, `HeadTypeDefs/`, `RulePackDefs/`
and `XenotypeIcons/`.

⛔ **Reuse genes wherever the species allows it.** These nine are supporting cast; nine new
gene trees is not the ask. Heat tolerance, skin colour, head type and a namer carry most of
it.
🔑 **Three carry a mechanical fact the prose depends on** — Whiphid's heat misery,
Abyssin's regeneration, Kitonak's needing no water. Those should be genes, not just
description, because a player who reads the bio will test them.

### ⚠️ Two are unrenderable and that is FINE — do not solve it

**Besalisk four arms** and **Toydarian wings** are anatomy RimWorld does not model at all.
Ship the xenotype for everything else it carries (size, colour, head, namer) and **leave the
prose alone.** ⛔ Do not rewrite Vurgo Nakk's four arms out of his brief, and do not
substitute a different species to make the sprite honest — the bio is text the player reads,
and §5.6's rule is about claims the game **contradicts**, not detail it does not draw.

⛔ **Do not add these to any faction's `xenotypeSet`.** They exist so eleven *named*
characters can be forced onto them (`INHABITED_DESIGN.md` §5.7). Adding them to a faction
would change what its anonymous pawns look like, which is the owner's race/faction matrix.

⚠️ **Not worldgen-blocking.** `Inhabited` stamps people onto a finished planet, so this can
land after the click.

## verify
- nine new defNames resolve in a regenerated dump whose mod set matches `ModsConfig.xml`
- each of the eleven characters' `race` string maps to one of them — ⚠️ watch the spelling
  trap: the prose says `Klatooinian` where an existing def says `Klatoonian`, so **match the
  prose, and if you must differ, say so in the def's comment**
- no faction's `xenotypeSet` gained an entry
- `validate_patch.py --defs` clean

## criteria
Onk-Onk-Deshu is three hundred kilos and needs no well; Uzzo has one eye; and nobody had to
be rewritten into somebody else.
