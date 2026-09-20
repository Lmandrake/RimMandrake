# DESERT_SHADE_GRID_KEYSTONE_1 — build the ShadeAt MapComponent

## what is wrong

desert.md §10 states "the shade grid is the keystone and we must build it" —
a single MapComponent exposing `ShadeAt(IntVec3)`, which burst-predator AI,
herbivore heat endurance, megafauna heat response, and shade-seeking AI are
all meant to read. No item exists for it: a grep of `items/` for "ShadeAt" or
"shade grid" found only `BIOME_ENRICHMENT_DESERT_WASTELAND_1` and
`INHABITED_AUGMENTATION_BUILD_1` mentioning it in passing, neither as its
actual owner. Without this component, the desert's entire behavioral identity
("nothing pursues", "an animal at the edge of a shadow, deciding") remains
prose with nothing implementing it.

## why it matters

This is the single dependency multiple other desert gap-list items are
blocked on — filing it late blocks everything downstream of it (see Watch
out).

## the work

File as a `RimMandrake`-tier (biome-agnostic) engine item, feature-gated per
`MOD_OPTIONS_RETROFIT_1`'s retrofit rules. Shape:

- a MapComponent implementing `ShadeAt(IntVec3)`
- a `JobGiver_WanderInRoofedCellsInPen`-pattern insert at
  `insertTag Animal_PreWander` for shade-seeking wander behavior
- a `GhoulFrenzy`-pattern staged-`severityPerDay` hediff for the
  burst-predator's heat-driven retreat

`design/Jawa/worldbuilding/desert_ecology_feasibility.md` already has the
full route table for this — read it before designing the component from
scratch.

## Watch out

`EXTREME_DESERT_GIANT_COMMENSALS_1` (shade-commensal micro-fauna under a
giant's moving shadow) and `DESERT_BURST_PREDATOR_FLAGSHIP_1` (the
burst-predator flagship's heat-retreat behavior) both explicitly depend on
this item and must not be started before it lands.

## verify

A MapComponent exposing `ShadeAt(IntVec3)` exists and is feature-gated in Mod
Settings per `MOD_OPTIONS_RETROFIT_1`; at least one consumer (even a stub)
reads it.

## criteria

The desert's shade mechanic is a real, queryable game system, not prose in a
design doc.
