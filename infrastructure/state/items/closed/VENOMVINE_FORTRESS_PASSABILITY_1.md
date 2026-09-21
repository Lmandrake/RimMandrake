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

## BUILT offline, 2026-09-21 — live verification owed, NOT deployed

Built by FOUNDRY without the bridge (another window held it). Compiles clean,
both def files validate at 0 errors, `run_selftests.py` 69/69, `naming_lint.py`
clean for `mandrake.rm.environmentalhazards`. **Nothing has been seen running
and nothing has been deployed** — successor `VENOMVINE_FORTRESS_LIVE_VERIFY_1`
(`needs: bridge`) carries both, and the deploy commands are in it.

### the engine survey the item asked for, and its one real answer

MEASURED against the decompiled 1.6 engine via RimSage, 2026-09-21.

🔴 **RimWorld 1.6 has NO native per-body-size passability, and the item's
option (a) — "an `Impassable`-for-large-pawns flag via a Harmony patch on the
pathfinder" — is not how 1.6 works at all.** The pathfinder was rewritten to
Unity's job system: `PathFinderMapData` builds exactly three `CostSource`s
(`map.pathing.Normal`, `.FenceBlocked`, `.Flying`) into a private readonly
list, and `ParameterizeGridJob` picks between two of them with
`request.TraverseParms.fenceBlocked ? fenceBlockedCost.Data : normalCost.Data`.
The A* itself is a `PathGridJob : IJobParallelFor` reading native arrays — there
is no per-cell managed callback to postfix.

⚠️ **The obvious-looking route is a trap and was rejected on evidence.**
`Pathing`'s constructor walks `DefDatabase<PathGridDef>.AllDefsListForReading`
and builds a `PathingContext` for **every** `PathGridDef`, so a mod CAN declare
a fourth path grid with its own `PathGrid` subclass and it WILL be constructed.
It would then never be consulted: the three `CostSource`s above are the only
grids the pathfinder job can be handed. A fourth `PathGridDef` gets you a
correct-looking grid that decides nothing.

The complete list of per-pawn passability channels in 1.6 is: those three fixed
`PathGridDef`s, the single `fenceBlocked` bool on `TraverseParms`,
`TraverseMode`, the allowed `Area`, and —

```
PathRequest.IPathGridCustomizer { NativeArray<ushort> GetOffsetGrid(); }
```

— a per-REQUEST offset grid. `PathGridJob.CostForCell` adds `custom[index]` to
the cell's cost, and **`PathGridJob.CellIsPassable` returns false outright when
`custom[index] >= 10000`.** That is the only channel in the engine that can make
specific cells impassable to one pawn's route while leaving them open to
another's, it is public, and vanilla drives it twice itself (`BreachingGrid`,
`GenStep_Roads`). It is what this build uses.

### what was built

Three new files in `src/RimMandrake/EnvironmentalHazards/Source/`
(`RM_CompBodySizeBarrier.cs`, `RM_MapComponent_BodySizeBarrier.cs`,
`RM_BodySizeBarrierPatches.cs`), generic in the same way
`CompProperties_ContactVenom` beside them is generic — nothing in the C# names a
plant, a biome or a campaign.

**Three bands, not two**, because the sheet's prose has three:

| sheet | band | mechanism |
|---|---|---|
| "small creatures pass through easily" | BodySize ≤ `passFreelyBodySize` 0.8 | nothing; the cell costs the plant's own `pathCost` |
| "sparser stands let a Jawa slowly thread them" | 0.8 → `blockBodySize` 1.5 | `threadMoveCost` 300 per cell (~33x a normal step) |
| "larger ones simply cannot" | > 1.5 | cell is IMPASSABLE to the route |

🔑 **1.5 is not a guess — it is vanilla's own "this pawn fills the cell"
constant.** `PawnUtility.PawnsCanShareCellBecauseOfBodySize` returns false
outright once either pawn is `>= 1.5f`. It puts muffalo (2.4), bison (2.1),
boomalope (2.0), rhinoceros (3.0), elephant/thrumbo (4.0), dewback (3.0),
bantha (4.0), ronto (6.0) and `RSW_ShrublandGiant` (6.0) on the far side of the
wall — the shrubland size ladder's HUGE band exactly. 0.8 is ours, set against
the roster so womprat/shyrack/scurrier/hare and every bird cross free.

**Two Harmony patches**, both bailing on a settings field read before touching a
map, both armed through `EnvironmentalHazardsMod`'s existing `Apply()` helper
that logs and declines if a signature has moved:

- Prefix on `PathFinder.CreateRequest(…, Pawn, IPathGridCustomizer)` — the
  overload that actually constructs the request, so it covers every pawn path
  request including `Pawn_PathFollower.GenerateNewPathRequest`'s. It only ever
  FILLS IN a customizer nobody supplied, so breach raids and road generation
  keep theirs.
- Postfix on `Pawn_PathFollower.GetPawnCellBaseCostOverride` — a public static
  with two consumers, and both are wanted: `CostToMoveIntoCell` (what a step
  actually costs → the "slowly thread" band) and `RCellFinder`, which rejects a
  candidate wander cell when that value exceeds 20 → a blocked animal stops
  CHOOSING thicket cells, which is what stops it generating path requests it can
  never satisfy.

### the three judgement calls, recorded rather than buried

1. 🔴 **A SIBLING def, not a comp on `RM_Venomvine`.** This item's own "Watch
   out" says the gate must not change the desert's use of the plant, and one
   ThingDef cannot be both scattered-and-ungated and a fortress. So
   `RM_VenomvineThicket` is a new def in the same file: same contact-venom comp
   with the same numbers (item point 3 — small enough to pass must never mean
   immune), same `texPath` (the `rmvenomvine_v1` artpipe job's own `style_notes`
   were written to double as "its shrubland sibling", so **no new art is owed**),
   and different clustering (radius 8 / weight 25 against the desert form's 4/6),
   HP, `growDays` and `harvestWork`. `RM_Venomvine` itself is byte-unchanged
   except for a header comment that now points at the sibling. ✅ The item's
   "don't invent new terrain" holds: **the dungeon is the def's own clustering**,
   no `TerrainDef` and no structure.
2. ⚠️ **"no larger race can" cannot be taken literally and this build does not
   pretend it can.** "Jawa" is lore text in this campaign, not a race def, so a
   Jawa colonist IS a humanlike at BodySize 1.0 and no threshold separates one
   from any other humanlike. Humanlikes therefore THREAD rather than being
   blocked, and the fortress reads as "nothing big gets in" rather than "only
   Jawas get in". If the owner wants the literal reading, it needs a Jawa
   xenotype carrying a body-size gene, which is a different item.
3. ⚠️ **Blocking is ROUTE-level, not physics.** Reachability still runs on the
   Normal grid, so a destination reachable only through a thicket reports
   reachable and then fails to path — which ends the job and lets the AI choose
   something else, the same way a fence-blocked animal behaves in vanilla. A
   pawn already standing on a barrier cell gets NO customizer at all (the
   start-cell carve-out) so it can always walk out; it simply cannot path back
   in. Making this physics would mean patching `PathGrid.CalculatedCostAt`
   itself, which is per-map and not per-pawn, i.e. it would block everyone.

### files

```
src/RimMandrake/EnvironmentalHazards/Source/RM_CompBodySizeBarrier.cs          new
src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_BodySizeBarrier.cs new
src/RimMandrake/EnvironmentalHazards/Source/RM_BodySizeBarrierPatches.cs       new
src/RimMandrake/EnvironmentalHazards/Source/BiomeGlowPatches.cs                Apply() gained asPrefix; two patches armed
src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs      options 40/41
src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj     3 Compile items + Unity.Collections
src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml    RM_VenomvineThicket
src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml               wildPlants 0.15
design/Jawa/worldbuilding/biomes/rosters/arid_shrubland.json                   roster row
design/Jawa/mods/biome_flora.py                                                FAMILIES row
```

⚠️ The roster and `FAMILIES` are updated together on purpose: `biome_flora.py
--check` fails the build when an authored def and its roster disagree, and that
check is the one whose absence cost `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`. It
could not be RUN this pass — it needs a `defs.sqlite` capture that does not
exist on this machine right now — so the agreement is asserted from the three
files, not measured.

## DEPLOYED AND VERIFIED LIVE, 2026-09-21

`VENOMVINE_FORTRESS_LIVE_VERIFY_1` ran on a 19-mod `shrublandfauna` quicktest and
returned **9 of 10 steps observed, the mechanism works**. Read that item for the
numbers; the load-bearing ones:

- In a sealed 1-wide corridor with no detour to prefer, a muffalo (2.4) reached
  x=55 and stopped one cell short of the band with the barrier ON, and crossed all
  ten band cells with it OFF — same pawn, same order, toggled live.
- Three distinct bands MEASURED: hare (0.2) ~127 ticks/cell (the plant's own
  `pathCost` 90, no override), colonist (1.0) **315–336 ticks/cell**
  (`threadMoveCost` 300), muffalo (2.4) never entered.
- The start-cell carve-out works: 3 of 3 muffalo spawned onto thicket cells walked
  out. The worst outcome this build could produce did not occur.
- 0 of 436 samples over 101,230 ticks put an undrafted muffalo on a thicket cell.
- Save/load restores the grids from `PostSpawnSetup`: 324 ticks/cell after reload.
- Map removal with an allocated `NativeArray` disposed clean — 0 native-collection
  diagnostics anywhere in `Player.log`, no crash.
- The desert form is untouched: swapping ONLY the band def to `RM_Venomvine` let
  the same muffalo cross at ~73 ticks/cell with the barrier still ON.

⛔ **Still UNSEEN: whether `wildClusterRadius 8` / `wildClusterWeight 25` produce
stands on a naturally generated map.** Not a defect — the only generation route
available (`jawa/world_tile_map_generate`) produced maps carrying 0–231 wild
plants against 17,904 on a normally generated map, and none of the biome's SEVEN
declared wildPlants appeared on any of them, so the instrument cannot answer it.

⚠️ And MEASURED while staging: `RM_VenomvineThicket` is refused by a lot of
ground — `jawa/set_plants` rejected 52 of 100 cells on untouched shrubland terrain
("terrain or conditions cannot support"), and 6 of 100 on plain `Soil`.

⇒ **CLOSED.**
