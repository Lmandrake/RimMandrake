# DESERT_GLITTER_BIRDS_COMMENSALS_1 — desert megafauna's glitter-bird shadow commensals

## what is wrong

desert.md §4c names "tiny glittering bird-like creatures that live their
entire lives in one animal's shadow, never touching open ground" — commensals
of the desert megafauna (now `RSW_ShadeWhale`, landed by
COMMISSION_LEDGER_CLEANUP_1), framed as "the herd-as-shade-structure idea at
its limit." No def and no item existed for it.

## why it matters — this is NOT a fresh design problem

`EXTREME_DESERT_GIANT_COMMENSALS_1` (open, `## needs: offline`) is already
mid-design on the *exact same mechanic*: grain-scale life that shelters
under, rides, and follows a large creature's moving shadow — there for the
dune_sea/deep_desert giants ("mirror-plated sun-axis giant"), here for the
desert's own megafauna. Both need the identical hard C# problem that item's
own text names: `ShadeAt(IntVec3)` (DESERT_SHADE_GRID_KEYSTONE_1) answers
"how shaded is this cell right now," a static query — "follow THIS
creature's moving shadow" needs either a per-host tracked shadow-caster
component, or `ShadeAt` plus a proximity/most-recently-darkened heuristic.
That design question should be answered ONCE, not twice.

## the work

- **Do not re-derive the shade-follow mechanism here.** Track
  `EXTREME_DESERT_GIANT_COMMENSALS_1`; whichever route it settles on (tracked
  shadow-caster vs. `ShadeAt`+proximity heuristic) is the route glitter-birds
  uses too — this item should be built as a second consumer of that
  mechanism, not a parallel implementation.
- What IS specific to this slug: the commensal species itself. desert.md
  calls for small, glittering, flightless-in-practice (never touch open
  ground) birds — a new `PawnKindDef`/`ThingDef`, small body size, likely a
  reskin of an existing small SW bird-analog already in `mandrake.rsw.
  swbestiary` (check the roster for a candidate before authoring from
  scratch, same "reskin, not new species" precedent as
  `DESERT_BURST_PREDATOR_FLAGSHIP_1`/`RSW_ShadeWhale`).
- Host: `RSW_ShadeWhale` is now the desert's actual megafauna — this item's
  commensal rides IT, distinct from the giant-commensal item's
  extreme-desert giant host.

## Watch out

Do not file a THIRD version of the shade-follow design question if a future
biome demands the same "commensal follows a specific moving shadow" pattern
again — extend/reference `EXTREME_DESERT_GIANT_COMMENSALS_1`'s eventual
mechanism instead.

## verify

This item names `EXTREME_DESERT_GIANT_COMMENSALS_1` as the shared mechanism
dependency (not duplicated), and — once that item's shade-follow route is
decided — a glitter-bird `PawnKindDef` exists, wired to follow
`RSW_ShadeWhale` specifically.

## criteria

Glitter-birds ship as a real commensal creature riding the shade whale's
shadow, built on the SAME shade-follow mechanism the giant-commensal item
lands, not a second one invented for this slug alone.
