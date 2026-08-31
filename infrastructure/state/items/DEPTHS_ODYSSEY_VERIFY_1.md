# DEPTHS_ODYSSEY_VERIFY_1 — Odyssey source read: the Depths is a CLONE job, not a PATCH job

**Overall verdict: the v1 slice in `design/Jawa/worldbuilding/depths_concept.md` is
buildable, but not as a pure XML patch mod.** Odyssey's vacuum layer is real, and its
*triggers* are genuinely data-driven — but every runtime consumer of vacuum is compiled
against the literal `StatDefOf.VacuumResistance` field and the literal `Room.Vacuum`
property, plus a hard `ModsConfig.OdysseyActive` gate. A parallel "pressure/drowning"
system that coexists with vacuum (rather than reskinning it outright) needs a companion
DLL / Harmony patch from day one. The mapgen and arrival layers, by contrast, are
genuinely reusable via new defs alone. SwimmingKit is dead (last touched 2022, 1.0–1.4
only, broken since 1.5, not installed here) — underwater pawn MOVEMENT is an unsolved
problem this project would have to build itself, or the v1 slice (caravan-scale dive
sites, no colony) sidesteps it entirely by never putting a controllable pawn in open
water. Lane-1's four borrowed-fauna mods all check out license-wise for patch-only reuse.

## spec
Answer, from source (RimSage `search_defs`/`search_source`/`read_csharp_symbol` against
the vendored Odyssey C# and defs; the live def dump at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs.sqlite`;
and the web where local source doesn't reach) six feasibility questions gating
`depths_concept.md`'s build spec: vacuum pipeline patchability, vacsuit stat gating,
leak/flood-fill, orbital mapgen + arrival families, SwimmingKit's 1.6 status, and the
license terms on the mods Lane 1 (`the_seas.md`) proposes to patch.

## 1. Vacuum pipeline patchability — PARTIAL (trigger is patchable; propagation is not)

The mechanism is `Verse.VacuumComponent : MapComponent, ICellBoolGiver`
(`Source/Verse/VacuumComponent.cs`), ticking `ExchangeRoomVacuum()`/`RebuildData()` to
diffuse a plain C# property, `Room.Vacuum` (`Source/Verse/Room.cs` ~L133, saved via
`TemperatureVacuumSaveLoad` — **not a StatDef, not a HediffDef**). Its getter's first
line is `if (!Map.Biome.inVacuum) return 0f;`.

- **The gate is genuinely XML-patchable**: `BiomeDef.inVacuum`
  (`Source/RimWorld/BiomeDef.cs` L87, public bool field) turns the whole pipeline on for
  any biome. No `TileMutatorDef` involved — it's biome-keyed. Per-object participation is
  also data-driven: `BuildingProperties.alwaysExchangeVacuum` / `canExchangeVacuum`
  (`BuildingProperties.cs` L57-59), `Building.ExchangeVacuum` (virtual), and
  `TerrainDef.exposesToVacuum` (`TerrainDef.cs` L222).
- **The math is hardcoded C#**: `VacuumComponent`, `VacuumUtility`,
  `HediffGiver_VacuumBurn`, and `Room.Vacuum` itself have no Def-level hook to run a
  *second, independent* severity type in parallel with vacuum. Every runtime call site
  additionally hard-gates on the literal `ModsConfig.OdysseyActive`.
- **Consequence**: flagging a new "Depths" biome `inVacuum=true` lights up the *existing*
  vacuum machinery for free (a pure reskin: rename the overlay text/color, nothing else
  changes) — but a coexisting, independently-tuned "water pressure" resource that isn't
  literally vacuum needs a companion `MapComponent` (Harmony patch or new DLL), because
  `Room.Vacuum` has no analog field to piggyback on.

## 2. Vacsuit stat gating — NO, hardcoded to the literal static field

`StatDefOf.VacuumResistance` (`Source/RimWorld/StatDefOf.cs` L162) is a static field bound
to defName `VacuumResistance`. Every consumer references this field directly, not a
swappable stat list:

- `Pawn.HarmedByVacuum` / `Pawn.ConcernedByVacuum` (`Pawn.cs` L2154-2182)
- `HediffComp_VacuumExposure` (`HediffComp_VacuumExposure.cs` L16)
- `VacuumUtility.IsProtectiveApparel` (`VacuumUtility.cs` ~L110)
- `ThingStuffPair.VacuumResistance` (`ThingStuffPair.cs` L71) and
  `PawnApparelGenerator` (multiple sites, L349-479)

`StatWorker_VacuumResistance` is XML-assignable as the StatDef's `workerClass`, so the
*value calculation* has one legitimate data hook — but none of the ~6 call sites above
would ever check a parallel `DiveSuit`/`PressureResistance` StatDef without a Harmony
patch. **A dive suit that grants `VacuumResistance` directly (pure reskin, same stat,
new apparel def) works today with zero C#. A dive suit gated by its own distinct stat
does not.**

## 3. Leak/flood-fill — EXISTS, but vacuum-specific (not a generic room-flood utility)

Confirmed real (not assumed): `VacuumComponent.MergeRoomsIntoGroups()` builds a
room-adjacency graph through doors/edifices flagged for vacuum exchange;
`HasDirectPathToVacuum()` is a BFS/frontier search — the actual "flood fill" — that finds
whether a room group has an open path to a room with `Room.ExposedToSpace == true`
(roof-hole count via `ExposedCountStopAt(1)`, dirtied by `RoofChanged`/
`TerrainChanged`/door open-close events). `ExchangeRoomVacuum()` then runs every 250
ticks, diffusing `Room.Vacuum` toward a weighted neighbor average — this is periodic
diffusion, not an instant one-shot propagation on breach.

Two lookalikes are **not** this system and would mislead if cited: `RoomPart_Breached`
is a map-*generation*-time wall decorator for orbital-ruin layouts (cosmetic); the
raider wall-breaching pathfinder (`BreachingGrid`/`BreachingUtility`) is unrelated combat
code.

**Repointability**: the room-graph-plus-periodic-diffusion *pattern* is a reusable
template, but the implementation is hard-wired to `Room.Vacuum` and the vacuum exchange
flags — there is no generic severity field on `Room` to redirect at a water level. A
flooding-dive-site mechanic needs new C#: either a parallel `MapComponent` replaying the
same graph-BFS-diffuse shape against its own field/side-dictionary, or a Harmony patch
onto the existing one. Not a drop-in.

## 4. Orbital mapgen + arrival families — YES for mapgen, PARTIAL-BUT-GOOD for arrival

**Mapgen is fully data-driven.** `MapGeneratorDef` (`Source/Verse/MapGeneratorDef.cs`) is
a plain `Def` (`genSteps: List<GenStepDef>`, `defaultUnderGridTerrain`, `roofDef`,
`isUnderground`, `pocketMapProperties`). `Defs/Odyssey/MapGeneration/SpaceMapGenerator.xml`
defines `MapGeneratorDef Space` (genSteps `Space`/`ScenParts`/`FogSpace`) with children
`Asteroid`, `OrbitalRelay`, `SettlementPlatform` built purely via `ParentName`
inheritance and genStep add/remove — **new orbital-family map types are authored as new
defs already**, no C# required for the def side. `SpaceMapParent`
(`Source/RimWorld/Planet/SpaceMapParent.cs`) picks its generator from
`def.mapGenerator ?? MapGeneratorDefOf.Space`, so a seafloor `WorldObjectDef` likely
doesn't need its own `MapParent` subclass either.

The one non-XML piece: the actual terrain fill is a hardcoded one-off,
`GenStep_Space.cs` (`SetTerrain(allCell, TerrainDefOf.Space)` for every cell) — a
"seafloor" analog filling silt/reef/wreck terrain patterns needs one new `GenStep` C#
class (small, not a large lift), unless an existing terrestrial water-gen GenStep can be
reused instead. No Odyssey `TileMutator` was found for space/orbital
(`Defs/Odyssey/TileMutators/` only has Natural/ManMade/AncientStructures/Special/
Modifiers/Landmarks) — orbital maps bypass the TileMutator system entirely.

**Arrival**: no Odyssey-specific "descend into space" `PawnsArrivalModeWorker` exists;
skyfallers (`Skyfaller`, `DropPodIncoming`, `ShuttleIncoming`) are generic, not
space-tied. Notably, vanilla core already ships almost exactly the requested "descent
through the water column" pattern: **`PawnsArrivalModeWorker_EmergeFromWater`**
(`PawnsArrivalModeDef EmergeFromWater`) flood-fills water cells
(`map.floodFiller.FloodFill`) and staggers pawn spawns from them — directly reusable via
a new `PawnsArrivalModeDef` (data-only), no new C# needed for descent arrivals.

**Not found in indexed source** (stated plainly, not guessed around): no
space/orbital-specific `TileMutatorDef`, and RimSage's index is the decompiled C# +
XML defs shipped with the game — if any Odyssey internals are IL-only with no decompiled
symbol, that wasn't distinguishable from "doesn't exist" in this pass. Nothing found
suggests such a gap, but it isn't provable negative.

## 5. SwimmingKit 1.6 status — DEAD, and not installed here

- **Not present** anywhere in the current mod set: zero hits for `swim`/`terrainmovement`
  in `ModsConfig.xml`, zero folders under the 8440-item Steam workshop cache
  (`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100`) with an
  About.xml naming SwimmingKit or TerrainMovementKit, and zero rows in the live
  `defs.sqlite` `mods` table.
- **Steam page confirms** (`steamcommunity.com/sharedfiles/filedetails/?id=1542399915`,
  fetched live): supports RimWorld **1.0–1.4 only**, last updated **Oct 29, 2022**.
  Community reports it breaks wildlife spawning and leaks memory on 1.5; no 1.5 or 1.6
  update was ever released. TerrainMovementKit (the companion framework SwimmingKit
  depends on) shows the same pattern via web search — last updated 2022, 1.1–1.4, no 1.6
  build found.
- **Consequence**: underwater pawn movement is an unsolved problem for this project.
  Nothing in the current stack lets a normal pawn traverse `WaterDeep`/`WaterOceanDeep`
  (both remain Impassable per `EMPTY_SEAS_FAUNA_1`'s MEASURED finding, unchanged by any
  of the 584 active mods). The v1 "dive expeditions" slice in `depths_concept.md` already
  sidesteps this on its own terms — it specs a caravan-scale visited *site*, not free pawn
  swimming on the open sea tile — so this is a real gap but not a blocker for v1 as
  scoped. It is a hard blocker for anything resembling v2's "drowned colony" with pawns
  walking the seafloor, absent new C# movement work (a SwimmingKit-equivalent would need
  to be built in-house, not adopted).

## 6. Lane-1 license checks — CLEAR, all four reuse-safe for patch-only content

Resolved the actual source mods for every creature `the_seas.md` Lane 1 names (identity
was ambiguous from the doc's short names alone; joined against the live `defs.sqlite`
def→mod index and confirmed each has a LICENSE file on disk):

| defName prefix | Source mod | packageId | License (file read in full) |
|---|---|---|---|
| `KwazelMaw`, `Mott`, `Dianoga`, `Dragonsnake`, `Fambaa`, `Fanback`, `Blixus` | Star Wars Animal Collection (Continued) | `mlie.starwarsanimalcollection` | **MIT** (LICENSE.md) — fully permissive |
| `BMT_MucklurkerCatfish`, `BMT_TaintedTurtle`, `BMT_MutatingTumorfish*` | Biomes! Polluted Lands | `biomesteam.biomespollutedlands` | **CC BY-NC-SA 4.0** (LICENSE.md) — noncommercial + share-alike + attribution; fine for a free mod, but any redistributed adaptation must stay CC BY-NC-SA and credited |
| `Megasquid` | Beasts of the Rim (Continued) | `mlie.beastsoftherim` | **MIT** (LICENSE.md) — fully permissive |
| `DA_LeviathanCrab` | Dark Ages: Beasts and Monsters | `van.beasts` | **CC BY 4.0** (LICENSE) — attribution only, no NC/SA restriction |

All four resolved package folders are already active in the live 584-mod set (workshop
IDs `3497316713`, `3390196656`, `2194018641`, `3472275628`) — Lane 1's plan is
PatchOperations against defs those mods already ship (spawn-table edits, biome
placement), not asset extraction/redistribution, which is the lightest-touch reuse case
under any of these four licenses. **No blocker.** The one condition worth carrying
forward: if the eventual mod ever bundles or redistributes Biomes! Polluted Lands assets
directly (rather than patching the live def), the CC BY-NC-SA share-alike clause applies
and the result must stay noncommercial and equivalently licensed — moot for a personal
campaign mod, worth a line in the mod's own credits if it ever ships publicly.

## verify
Every class/method/field name above was read from RimSage's decompiled-source index
(`mcp__rimsage__search_source`/`read_csharp_symbol`/`search_defs`) against the vendored
Odyssey C#, not inferred from play knowledge or guessed. SwimmingKit's version claim
came from a live fetch of its own Steam Workshop page, not a cached description. Lane-1
mod identities came from the live `defs.sqlite` def→mod join (frozen dump lineage
`OFFICIAL-2026-08-29`, `1742630eb6253187`, refreshed captures through 2026-08-31 in the
same mod set), and each license was the actual LICENSE/LICENSE.md file read in full from
its workshop folder, not the About.xml blurb.

## criteria
All six questions carry a source-backed verdict with no "probably". Ambiguity is flagged
explicitly where it exists (§4's negative-existence caveat on space TileMutators) rather
than papered over.

## Design decision this leaves for BENCH
The verdict is a **scaled build, not a hard blocker**: ship v1 ("dive expeditions") as
specced — it needs one new companion-DLL-or-Harmony `MapComponent` (§3's flood/pressure
analog, §1's parallel severity if the design wants water pressure to feel distinct from
reskinned vacuum) plus one new `GenStep` C# class (§4) and a data-only
`PawnsArrivalModeDef` reusing `EmergeFromWater` (§4) — a small, bounded C# surface, not
"build space from scratch." The open call is whether v1's dive-suit stat should be a
**pure `VacuumResistance` reskin** (zero C#, ships fastest, but literally shares vacuum's
number space with any future space content) or an **independent stat** (needs the
Harmony patch from §2, but keeps "diving" and "spacewalking" tunable separately forever).
That's a design register call, not a technical one — leaving `doing` for BENCH to rule on
it before a build spec is written.
