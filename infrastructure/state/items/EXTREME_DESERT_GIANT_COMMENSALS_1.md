# EXTREME_DESERT_GIANT_COMMENSALS_1 — shade-commensal micro-fauna under giants

## what is wrong

dune_sea §4 describes "following a giant is how you cross the dune sea" —
shade-commensal micro-fauna living under a walking giant's shadow, plus a
mirror-plated sun-axis giant. Neither has a def or an item. The `new_defs`
note marks the commensal as needing C# (shade-follow behavior).

## why it matters

A named, described mechanic central to how the dune sea's ecology is meant
to read (giants as mobile shelter) does not exist in any form.

## the work

File as a design item — this needs the shade-follow C# behavior and cannot
be authored as a plain ThingDef/PawnKindDef alone.

## Watch out

This item depends on `DESERT_SHADE_GRID_KEYSTONE_1` — a giant's shadow is
meaningless as a "moving shade patch" until `ShadeAt(IntVec3)` exists to
query. **Do not start this before `DESERT_SHADE_GRID_KEYSTONE_1` lands.**

## verify

A design item exists describing the commensal's shade-follow behavior and
the sun-axis giant, both referencing `DESERT_SHADE_GRID_KEYSTONE_1` as a hard
dependency.

## criteria

The giant-commensal mechanic is a filed, correctly-sequenced item, not an
unfiled note.
