# EXTREME_DESERT_CAVERN_BEAST_1 — author the Mandalorian cave-beast and its eggs

## what is wrong

deep_desert §8 calls for "serious authoring effort" on a Mandalorian
cave-beast with massive eggs — "a Jawa would cross a desert for" them. It
sits in `new_defs` with no item. deep_desert's own "Owed" section separately
notes that cavern authoring in general is a substantial piece of work on its
own.

## why it matters

A named creature the design sheet treats as a headline feature of the biome
has no def and no filed item at all.

## the work

File as one creature ThingDef/PawnKindDef plus one egg ThingDef (the eggs
function as portable water per deep_desert §4). Cavern map-generation itself
is separate, larger work and is explicitly out of scope for this item.

## Watch out

Do not fold cavern map-gen into this item's scope — the source review is
explicit that it is a separate, larger piece of work belonging elsewhere.

## verify

A creature + egg item exists, scoped to just the creature and its egg item,
not cavern generation.

## criteria

The cave-beast has a filed, correctly-scoped item distinct from the larger
cavern-authoring work.
