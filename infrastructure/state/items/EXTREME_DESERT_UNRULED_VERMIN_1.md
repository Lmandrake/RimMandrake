# EXTREME_DESERT_UNRULED_VERMIN_1 — owner card: rule the Fall Line vermin rows for extreme desert

## what is wrong

12 of 23 `wildAnimals` rows on RUT_ExtremeDesert come from the Fall Line
injection layer (`design/Jawa/worldbuilding/biomes/rosters/fall_line.json`)
and were never ruled against this biome's own design sheet.

`RSW_Scavrat` (0.6 weight) and `RSW_WompRat` (0.4 weight) are the two
heaviest rows on the biome. Scavrat's bodySize is **0.5 (MEASURED from
`RSW_Scavrat.xml`)** — "medium" under ruling R22's grain-≤0.2 / giant-≥4
bimodal, which the biome's own sheet explicitly bans. `Rat` (bodySize 0.2,
unguarded Core def) is the "instantly-nameable Earth organism" the sheet
singles out as exactly the wrong kind of creature for this biome.
`RSW_WompRat`'s bodySize is **UNMEASURED** — it does not appear in its own
race file; it inherits `baseBodySize` from a parent def, and resolving that
inheritance was not done in the source review.

## why it matters

The two heaviest-weighted animals on the biome may both violate the sheet's
own size law, and a third (`Rat`) is named by the sheet as precisely the
wrong kind of creature — none of this has ever been put to the owner.

## the decision this needs

Keep/cut/trim each of the 12 Fall-Line-injected rows for RUT_ExtremeDesert
specifically. (They stay in RUT_Desert/AridShrubland regardless of this
call — this ruling is extreme-desert-only.) Only 3 of the 12 rows are named
individually in the source review; the remaining 9 must be pulled from
`fall_line.json`'s `injection_layer` before the card is presented to the
owner.

Recommended default (from the review): cut `Rat` entirely; trim
`RSW_Scavrat` to 0.1; trim `RSW_WompRat` to 0.1; keep Mynock, Cindermite, and
the droid rows (droids are the deep_desert §4 "invisible to the food web"
beat and are not subject to the size law).

## Watch out

- `RSW_WompRat`'s bodySize is **UNMEASURED**, not zero and not assumed-medium
  — resolve it before presenting the card if the size-law reasoning is part
  of the pitch. Instrument: `measure` on the def dump, or parse with
  inheritance via `validate_patch.py --defs`.
- Whatever gets ruled here interacts with `DesiredAnimalDensity` on a +55°C
  map — how many of these 12 rows actually pass `SeasonAcceptableFor` at that
  temperature was not re-checked after `ANIMAL_TOLERANCES_JOIN_BROKEN_1`
  resolved. Instrument: `python3 design/Jawa/fauna/animal_tolerances.py`
  against the current `RUT_` tables, or a live
  `WildAnimalSpawner.DebugString()` on a dune-sea quicktest (it prints
  `DesiredAnimalDensity` directly).
- The full 12-row list is not in this item yet — pull it from
  `fall_line.json`'s `injection_layer` before building the card.

## verify

RUT_ExtremeDesert's `wildAnimals` table matches the owner's ruling for all 12
rows; no medium-class (bodySize 0.2–4) unguarded creature remains unless
explicitly kept by name.

## criteria

Every Fall-Line-injected vermin row on the extreme desert has been put to the
owner and ruled, not inherited by default from an unrelated injection layer.


---

## 🔴 RULED 2026-09-20 — and the question was rejected, not answered

The owner was asked to keep/cut/trim the 12 Fall-Line rows. He rejected the
framing. Verbatim:

> *"These falling injections should not be listed as 'sometimes appears' in the
> deep desert but rather arrive with injected content from inhabited from
> wreckage or, alternatively, if we pursue the generator option to produce the
> same. They are not part of 'the biome' there are simply events and subregions
> where you can meet them. Add that to the fall spec or other guidance docs as
> appropriate. And the rat was there because actual terrestrial rats might be fun
> to fall from a ship as a white lab rat. That is all. So keep it."*

**So this is not a commonality-tuning job.** ⛔ Do not trim `Scavrat` to 0.1. ⛔ Do
not cut `Rat`. Both of those were the recommended answer to the wrong question.

### What the work actually is

1. **Remove all Fall-Line injection rows from the biome `wildAnimals` tables** —
   `RUT_ExtremeDesert`, `RUT_Desert`, `RUT_AridShrubland`. Ambient commonality is
   the wrong mechanism for every one of them.
2. **Re-home them onto injected wreckage content and subregions** — something you
   walk into or that arrives, not something that lives there. A generator that
   produces the same effect is an acceptable route.
3. **`Rat` stays, as an arrival.** It is ruled in deliberately, for the white-lab-
   rat-out-of-a-wreck joke. 🔴 It will look exactly like the Earth-organism ban
   violation this sheet otherwise enforces — do not let a purity sweep cut it.
4. Keep the 7 `OuterRim_*` droid rows; they are the sheet's "invisible to the
   food web" beat and suit arrival scoping well.

### The consequence, stated so nobody backfills it

With the vermin gone, `RUT_ExtremeDesert` loses its two heaviest ambient rows
(`Scavrat` 0.6, `WompRat` 0.4) across 3,969 tiles. 🔑 **That emptiness is the
intended outcome, not a hole.** The deep desert is meant to be bare; what you
meet there should be something that arrived. Do not add ambient species to
compensate.

The full ruling and its rationale live in
`design/Jawa/worldbuilding/biomes/fall_line.md` §8a.
