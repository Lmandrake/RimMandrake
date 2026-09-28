# DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1 — grain-scale life riding the mirror giant's shadow

## what is wrong

dune_sea.md §4 ("the giants carry the only moving shadows on the planet, and
there is an ecology living in them... commensals ride it, shelter under it,
and follow it") names a grain-scale commensal fauna with no def and no item.
roster's own entry (`rosters/dune_sea_deep_desert.json`, "shade-commensal
micro-fauna living under a walking giant") flags `mechanic_load: "C#:
shade-follow (no donor mechanic keys to another creature's shadow)"` — this
is a mechanics ask, not a pure art/def commission, per this ledger item's own
"watch out" (COMMISSION_LEDGER_CLEANUP_1).

## why it matters — this is NOT a fresh design problem, it's a THIRD consumer

`EXTREME_DESERT_GIANT_COMMENSALS_1` (closed, design-only) already raised
exactly this mechanic for this exact host (the dune_sea/deep_desert giant),
and `DESERT_GLITTER_BIRDS_COMMENSALS_1` (open) already filed as the second
consumer, for the desert's own `RSW_ShadeWhale` megafauna. Both need the
identical hard C# problem: `ShadeAt(IntVec3)` (`DESERT_SHADE_GRID_KEYSTONE_1`,
closed) answers "how shaded is this cell right now" — a static query.
"Follow THIS creature's moving shadow" needs either a per-host tracked
shadow-caster component, or `ShadeAt` plus a proximity/most-recently-darkened
heuristic. That design question is answered ONCE, not three times.

The host for this consumer is now `RM_MirrorGiant`
(`src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_MirrorGiant.xml`,
authored this same ledger pass) — the mirror-plated sun-axis giant
`EXTREME_DESERT_GIANT_COMMENSALS_1` was waiting on.

## the work

- **Do not re-derive the shade-follow mechanism here.** Track
  `DESERT_GLITTER_BIRDS_COMMENSALS_1`'s own build (it is the currently-open
  item nearest to actually building this); whichever route it settles on
  (tracked shadow-caster vs. `ShadeAt`+proximity heuristic) is the route this
  item uses too — build as a third consumer, not a parallel implementation.
- What IS specific to this slug: the commensal species itself. dune_sea.md
  §4 calls for grain-scale (the biome's own bimodal body-size law: "giants
  on the surface, and grain-scale life below it, with a hard gap where every
  ordinary animal would be" — §4) micro-fauna that rides/shelters under/
  follows `RM_MirrorGiant`. Check `cast_assignment.csv`/`animal_census.csv`
  for a small existing grain-scale candidate before authoring from scratch
  (same discipline that caught the tunnel-snake/kinrath near-misses
  elsewhere in this ledger item).
- Host: `RM_MirrorGiant`, RM_-tier (invented, not Star Wars IP), wired into
  `RM_Stillsand`'s own `wildAnimals` directly (not the frozen
  `RUT_ExtremeDesert.xml` twin, not the `WildAnimals_Stillsand.xml` patch —
  that file only replays copied Star-Wars-named content).

## needs

offline (design continues; no owner card needed yet — a card may be needed
once a specific commensal species/mechanism choice is proposed, same posture
the other two items in this family use).

## verify

This item exists, names `DESERT_GLITTER_BIRDS_COMMENSALS_1` as the shared
mechanism to follow (not re-derive), and names `RM_MirrorGiant` as its real,
already-built host.

## criteria

The shade-commensal mechanic and species are built as a third consumer of
whichever shade-follow route `DESERT_GLITTER_BIRDS_COMMENSALS_1` lands on —
not an unfiled note, and not a duplicated design pass.
