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
