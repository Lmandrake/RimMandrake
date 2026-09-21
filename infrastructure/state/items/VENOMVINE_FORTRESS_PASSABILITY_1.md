# VENOMVINE_FORTRESS_PASSABILITY_1 — venomvine fortress: size-gated passability C# for the shrubland thicket

## what is wrong

`COMMISSION_LEDGER_CLEANUP_1`'s arid_shrubland sheet slug
`venomvine-fortress-flora-passability-by-body-size` has no mechanism.
`VENOMVINE_CONTACT_VENOM_BUILD_1` (built and MEASURED offline 2026-09-20,
`10033074a`) shipped `RM_Venomvine` — the DESERT-lineage plant with the
contact-venom scratch comp (`CompContactVenom`/`MapComponent_ContactVenom`,
`mandrake.rm.environmentalhazards`) — and its own `## Watch out` section says
explicitly:

> Do NOT build the shrubland thicket's body-size passability here — separate
> owed slug (`venomvine-fortress-flora-passability-by-body-size`,
> `COMMISSION_LEDGER_CLEANUP_1`). Just don't preclude it.

This item is that separate slug, now actually filed (it had only been named
as a cross-reference until this pass).

The source text, `arid_shrubland.md` §4 "Venomvine — the fortress flora":

> Dense thickets that sometimes manage to colonize: nearly impossible to cut
> down, and a scratch carries venom with serious results. **Small creatures
> pass through easily; larger ones simply cannot.** Desert lineage — they
> resist fire greatly and burn only grudgingly.
>
> 🔑 **A mature thicket is a dungeon.** Sparser stands let a Jawa slowly
> thread them — no larger race can — but inside it is a dangerous, cave-like
> maze whose residents move through the walls to their advantage.

The biome doc's own "Owed" section lists "venomvine passability by body size"
as part of the biome's still-unrun engine feasibility pass, the same class of
gap as the giants' parental enrage (`SHRUBLAND_GIANT_ENRAGE_1`).

## why it matters

Without it, "nearly impossible to cut down... small creatures pass through
easily, larger ones simply cannot" and "a mature thicket is a dungeon" are
both pure prose — `RM_Venomvine` currently has one `pathCost` (60) that
applies uniformly regardless of the pawn's body size, so nothing distinguishes
a Jawa threading a thicket from a giant that (per the biome's own lore)
"simply cannot" enter one at all. The entire "sneaking in and out is
lucrative; fighting through is perilous" gameplay loop the sheet describes
does not exist without this.

## the work — scoping only, not yet designed in detail

1. **Engine feasibility check first**, per the biome doc's own flag. RimWorld
   pathfinding cost is per-TerrainDef/per-Thing, not natively body-size-aware
   per pawn — survey whether a body-size gate is better expressed as: (a) an
   `Impassable`-for-large-pawns flag via a Harmony patch on the pathfinder
   checking `pawn.BodySize` against a threshold when crossing a
   `RM_Venomvine`-occupied cell, or (b) a much higher `pathCost` combined with
   a hard block (hediff/damage) for anything above a body-size threshold,
   which is cheaper but reads as "very slow" rather than "physically cannot"
   for large pawns.
2. **The "dungeon" read** — dense clusters of `RM_Venomvine` (already
   `clusters 4/6` per `VENOMVINE_CONTACT_VENOM_BUILD_1`) forming maze-like
   regions is largely already implicit in the plant's own clustering; what's
   missing is the SIZE gate, not new terrain generation. Don't over-build a
   new TerrainDef/structure for this — the biome doc's own header comment
   (`RUT_AridShrubland.xml`) already scoped "venomvine as a dungeon-thicket
   TerrainDef/structure" OUT of a simple pass; a size-gated passability comp
   on the existing plant should be tried first before inventing new terrain.
3. Reuse `RM_Venomvine`'s existing `CompContactVenom` — a pawn small enough
   to pass should presumably still take the contact-venom scratch; don't
   accidentally make "small enough to pass" also mean "immune to the venom."

## Watch out

- This is C#-on-a-shared-plant work: `RM_Venomvine` is `mandrake.rm.
  environmentalhazards`'s def, used by BOTH the desert (`RUT_Desert.xml`,
  0.25) and (once this item builds it) the shrubland. A body-size passability
  gate must not change the desert's own use of the plant — the desert
  thicket is described as scattered/sparse ("strange vines and thorny venom
  writhing around some areas"), not a fortress; whatever gate this item adds
  should be additive (e.g. a MapComponent/comp check that no-ops when body
  size never exceeds the threshold in practice) rather than a redefinition of
  the plant's baseline behaviour.
- Art (`rmvenomvine_v1`, `infrastructure/artpipe/pending/`) is already queued
  and, per its own `style_notes`, was explicitly written to double as "its
  shrubland sibling" — do not requeue art for this slug, the existing job
  covers it.
- The desert build's own C# rode a game load alone (tier c: compile with the
  user-local .NET SDK, deploy the DLL only while the game is down) — same
  constraint applies here since it's the same assembly.

## criteria

A large pawn cannot enter a `RM_Venomvine` thicket cell (or pays a
prohibitive, mechanically-distinct cost vs. a small pawn), verified live —
per `arid_shrubland.md`'s own wording, "small creatures pass through easily;
larger ones simply cannot."
