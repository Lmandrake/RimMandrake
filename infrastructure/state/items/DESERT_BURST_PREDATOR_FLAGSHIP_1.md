# DESERT_BURST_PREDATOR_FLAGSHIP_1 — the desert's burst-predator flagship

## what is wrong

desert.md §4 and §10 describe a burst-predator "flagship" — bursts, grabs,
retreats to cool — as "nearly native" to build: staged `statFactors` with a
negative `severityPerDay` (`GhoulFrenzy` pattern) plus one C# line on the
attack job. Wraid and Gutkurr were slowed to 4.4 as interim legal predators
standing in for it. The flagship itself has no def and no item.

## why it matters

The desert's headline predator behavior — a described, nearly-buildable
mechanic — doesn't exist; two unrelated creatures are standing in for it
indefinitely.

## the work

File after `DESERT_SHADE_GRID_KEYSTONE_1` lands — the flagship's
retreat-to-cool behavior reads `ShadeAt` to know when to retreat, so it
cannot be correctly built before that MapComponent exists. Body of the work:
reskin the strongest already-ported burst predator rather than author a new
species from scratch; add the staged `statFactors`/`severityPerDay` hediff
(`GhoulFrenzy` pattern) and the one-line C# retreat-to-shade job.

## Watch out

Do not start this before `DESERT_SHADE_GRID_KEYSTONE_1` lands — the retreat
behavior has no shade signal to read without it. This is the second of two
items (with `EXTREME_DESERT_GIANT_COMMENSALS_1`) explicitly sequenced after
that keystone item.

## verify

A burst-predator item exists, references `DESERT_SHADE_GRID_KEYSTONE_1` as a
hard dependency, and names which already-ported creature it reskins.

## criteria

The desert's burst-predator is either shipped or filed as a
correctly-sequenced item, not indefinitely covered by two unrelated
stand-ins.
